import json
import os
import strawberry
from db import mongo
from flask import Flask, jsonify, render_template, request
from strawberry.flask.views import GraphQLView
from gpt.langchain_models import jd_questions
from strawberryGQL.queries import Query
from strawberryGQL.mutations import Mutation
from strawberry.schema.config import StrawberryConfig
from werkzeug.security import generate_password_hash, check_password_hash
from flask_swagger_ui import get_swaggerui_blueprint

app=Flask(__name__)

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
        return {"Message":"Login Successful."}

    return {"Message":"Invalid Credentials"}

@app.route('/info/<username>',methods=['GET'])
def get_my_details(username):
    user = mongo.db.user_collection.find_one({'username': username})
    user_resume = mongo.db.resumes_collection.find_one({'username':username}, {'_id': False})

    if user and user_resume:
        return jsonify(user_resume)

    return {"Message":"User not registered/Not uploaded resume"}

@app.route('/generateQuestions/resume/<username>',methods=['GET'])
def generate_questions_resume(username):
    user = mongo.db.user_collection.find_one({'username': username})
    user_resume = mongo.db.resumes_collection.find_one({'username':username}, {'_id': False})
    # generate questions from openai here
    return {"Questions":["q1","q2","q3"]}

@app.route('/generateQuestions/jd',methods=['POST'])
def generate_questions_jd():
    data=request.data.decode('utf-8')
    if data:
        job_description=data
        questions=jd_questions(job_description)
        return {"Response":json.loads(questions)}
        
    return {"Message": "Invalid data. Make sure to send text in the request body."}