from datetime import datetime
from functools import wraps
import json
import jwt
from initialise import create_app
from mongoDatabase.db import mongo
from flask import g, jsonify, render_template, request
from gpt.langchain_models import jd_questions, resume_section_questions
from werkzeug.security import generate_password_hash, check_password_hash

app=create_app()

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        g.user_data = data

        return func(*args, **kwargs)

    return decorated


@app.route('/')
def hello_world():
    return render_template("resusight_homepage.html")

@app.route('/register',methods=['POST'])
def register():
    user_input=request.get_json()

    if not user_input:
        return {"Message": "Invalid input data. Make sure to send JSON data in the request body."}, 400
    
    try:
        username=user_input['username']
        email=user_input['email']
        password=user_input['password']
    except:
        return {"Message":"Invalid data sent."}

    if not username or not email or not password:
        return {"Message": "Username, email, and password are required fields."}, 400
    
    existing_user=mongo.db.user_collection.find_one({'$or': [{'username':username},{'email':email}]})

    if existing_user:
        return {"Message":"Username or email already exists."}, 400

    hashed_password=generate_password_hash(password)
    
    new_user={
        'username':username,
        'email':email,
        'password':hashed_password
    }

    mongo.db.user_collection.insert_one(new_user)


    return {"Message":"Registration Successful. Proceed to log in."}

@app.route('/login',methods=['POST'])
def login():
    user_input=request.get_json()

    if not user_input:
        return {"Message": "Invalid input data. Make sure to send JSON data in the request body."}, 400
    
    try:
        username=user_input['username']
        password=user_input['password']
    except:
        return {"Message":"Invalid data sent."}

    if not username or not password:
        return {"Message": "Username and password are required fields."}, 400
    
    user=mongo.db.user_collection.find_one({'username':username})

    if user and check_password_hash(user['password'],password):
        token = jwt.encode({'user': username, 'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']}, app.config['SECRET_KEY'], algorithm='HS256')
        return {"Message":"Login Successful.",'token': token}

    return {"Message":"Invalid Credentials"}

@app.route('/info/<username>', methods=['GET'])
@token_required
def get_my_details(username):
    logged_in_user = g.user_data.get('user')

    if logged_in_user is None:
        return {"Message": "Login required."}

    if username != logged_in_user:
        return {"Message": "Forbidden, you can access only your own information"}, 403

    query = {"username": username}
    condition = {'_id': False}
    user = mongo.db.user_collection.find_one(query)
    user_resume = mongo.db.resumes_collection.find_one(query, condition)
    return_this = {}

    resume_questions = mongo.db.resume_questions_collection.find(query, {'_id': False, 'username': False})
    if resume_questions:
        return_this['Resume Questions'] = [question for question in resume_questions]

    contributed_jds = mongo.db.jds_collection.find({"submitted_by": username}, condition)
    if contributed_jds:
        return_this['Contributed JDS'] = [jd for jd in contributed_jds]

    jd_questions = mongo.db.jd_questions_collection.find(query, condition)
    if jd_questions:
        return_this['JD Questions'] = [question for question in jd_questions]

    if user and user_resume:
        return_this['User Resume'] = user_resume
        return return_this

    return {"Message": "User not registered/Not uploaded resume"}

@app.route('/generate/<username>/resume/<section>',methods=['GET'])
@token_required
def generate_section_questions_resume(username,section):
    logged_in_user=g.user_data.get('user')

    if logged_in_user is None:
        return {"Message":"Login required."}
    
    if section not in ['skills','experience','projects','publications','certifications']:
        return {"Message":"Not allowed to generate questions for this section"}, 403

    if username!=logged_in_user:
        return {"Message":"Forbidden, you can access only your own information"}, 403

    user_resume = mongo.db.resumes_collection.find_one({'username':logged_in_user}, {'_id': False})

    if user_resume is None:
        return {"Message":"No resume found for this user."}

    if section in user_resume:
        response=resume_section_questions(section,json.dumps(user_resume[section]))

    
    response_dict=json.loads(response)
    response_dict['username']=logged_in_user
    response_dict['section']=section
    filter = {'username': logged_in_user, 'section': section}
    update = {'$set': response_dict}

    mongo.db.resume_questions_collection.update_one(filter,update,upsert=True)

    return {"Response":json.loads(response)}


@app.route('/generate/jd',methods=['POST'])
@token_required
def generate_questions_jd():
    logged_in_user=g.user_data.get('user')
    data=request.data.decode('utf-8')

    if logged_in_user is None:
        return {"Message":"Login required."}
       
    if data:
        job_description=data
       
        response=jd_questions(job_description)
        response_dict=json.loads(response)
        jd_data={
            "job_title":response_dict['job_title'],
            "company_name":response_dict['company_name'],
            "description":job_description
        }

        required_keys = {'job_title', 'company_name', 'description'}
        if set(jd_data.keys()) != required_keys:
            return {"Message": "Invalid Data"}
        
        response_dict['username']=logged_in_user
        jd_data['submitted_by']=logged_in_user

        mongo.db.jds_collection.insert_one(jd_data)
        mongo.db.jd_questions_collection.insert_one(response_dict)
        
        return {"Response":json.loads(response)}
        
    return {"Message": "Invalid data. Make sure to send text in the request body."}