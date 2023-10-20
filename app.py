from datetime import datetime, timedelta
from functools import wraps
import json
import os
import jwt
import strawberry
from db import mongo
from flask import Flask, g, jsonify, render_template, request
from strawberry.flask.views import GraphQLView
from gpt.langchain_models import jd_questions, resume_questions, resume_section_questions
from strawberryGQL.queries import Query
from strawberryGQL.mutations import Mutation
from strawberry.schema.config import StrawberryConfig
from werkzeug.security import generate_password_hash, check_password_hash
from flask_swagger_ui import get_swaggerui_blueprint

app=Flask(__name__)

app.config['SECRET_KEY']=os.getenv('JWT_KEY')
app.config['JWT_EXPIRATION_DELTA']=timedelta(days=1)
# Mongo Config
MONGO_ATLAS_USERNAME=os.getenv('MONGO_ATLAS_USERNAME')
MONGO_ATLAS_PASSWORD=os.getenv('MONGO_ATLAS_PASSWORD')
MONGO_ATLAS_CLUSTER_ADDR=os.getenv('MONGO_ATLAS_CLUSTER_ADDR')
MONGO_ATLAS_DB_NAME=os.getenv('MONGO_ATLAS_DB_NAME')

MONGO_URI=f"mongodb+srv://{MONGO_ATLAS_USERNAME}:{MONGO_ATLAS_PASSWORD}@{MONGO_ATLAS_CLUSTER_ADDR}.mongodb.net/{MONGO_ATLAS_DB_NAME}?retryWrites=true&w=majority"
app.config['MONGO_URI']=MONGO_URI
mongo.init_app(app)

# Swagger Config
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'ResuSight API Docs'
    }
)

app.register_blueprint(swaggerui_blueprint)


schema=strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False))
class StrawberryView(GraphQLView):
    schema = schema


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema,graphiql=True),
)

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

@app.route('/info/<username>',methods=['GET'])
@token_required
def get_my_details(username):
    logged_in_user=g.user_data.get('user')

    if logged_in_user is None:
        return {"Message":"Login required."}

    if username!=logged_in_user:
        return {"Message":"Forbidden, you can access only your own information"}, 403

    user = mongo.db.user_collection.find_one({'username': username})
    user_resume = mongo.db.resumes_collection.find_one({'username':username}, {'_id': False})

    if user and user_resume:
        return jsonify(user_resume)

    return {"Message":"User not registered/Not uploaded resume"}

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
    mongo.db.resume_questions_collection.insert_one(response_dict)

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