import json
import os
import strawberry
from db import mongo
from flask import Flask, jsonify, render_template, request
from flask_pymongo import PyMongo
from strawberry.flask.views import GraphQLView
from gpt.langchain_test import hello_langchain, jd_questions
from strawberryGQL.queries import Query
from strawberryGQL.mutations import Mutation
from strawberry.schema.config import StrawberryConfig
from bson import json_util

app=Flask(__name__)

# Mongo Config
MONGO_ATLAS_USERNAME=os.getenv('MONGO_ATLAS_USERNAME')
MONGO_ATLAS_PASSWORD=os.getenv('MONGO_ATLAS_PASSWORD')
MONGO_ATLAS_CLUSTER_ADDR=os.getenv('MONGO_ATLAS_CLUSTER_ADDR')
MONGO_ATLAS_DB_NAME=os.getenv('MONGO_ATLAS_DB_NAME')

MONGO_URI=f"mongodb+srv://{MONGO_ATLAS_USERNAME}:{MONGO_ATLAS_PASSWORD}@{MONGO_ATLAS_CLUSTER_ADDR}.mongodb.net/{MONGO_ATLAS_DB_NAME}?retryWrites=true&w=majority"
app.config['MONGO_URI']=MONGO_URI
mongo.init_app(app)


schema=strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False))
class StrawberryView(GraphQLView):
    schema = schema


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema,graphiql=True),
)

@app.route('/info/<username>',methods=['GET'])
def get_my_details(username):
    user = mongo.db.user_collection.find_one({'username': username})
    user_resume = mongo.db.resumes_collection.find_one({'username':username}, {'_id': False})

    if user and user_resume:
        result = json.dumps(user_resume, default=json_util.default)
        print(result)
        return jsonify(user_resume)

    return {"Message":"User not registered/Not uploaded resume"}

@app.route('/generateQuestions/resume/<username>',methods=['GET'])
def generate_questions_resume(username):
    user = mongo.db.user_collection.find_one({'username': username})
    user_resume = mongo.db.resumes_collection.find_one({'username':username}, {'_id': False})
    # generate questions from openai here
    return {"Questions":["q1","q2","q3"]}

@app.route('/generateQuestions/jd',methods=['GET'])
def generate_questions_jd():
    return {"Questions":["q1","q2","q3"]}

@app.route('/lcTest')
def lctest():
    response=jd_questions()
    return response

@app.route('/')
def hello_world():
    return render_template("resusight_homepage.html")