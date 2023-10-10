import os
import strawberry
from db import mongo
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from strawberry.flask.views import GraphQLView
from strawberryGQL.queries import Query
from strawberryGQL.mutations import Mutation
from strawberry.schema.config import StrawberryConfig

app=Flask(__name__)

# Mongo Config
app.config['MONGO_URI']=os.getenv('MONGO_URL')+os.getenv('MONGO_DB_NAME')
mongo.init_app(app)


schema=strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False))
class StrawberryView(GraphQLView):
    schema = schema


app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema,graphiql=True),
)


@app.route('/')
def hello_world():
    return 'Hello, World!'



if __name__=='__main__':
    app.run(debug=True)