import os
from db import mongo
from flask import Flask
from flask_pymongo import PyMongo
from schema import schema
from strawberry.flask.views import GraphQLView

app=Flask(__name__)

# Mongo Config
app.config['MONGO_URI']=os.getenv('MONGO_URL')+os.getenv('MONGO_DB_NAME')
mongo.init_app(app)


class StrawberryView(GraphQLView):
    schema = schema

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema),
)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__=='__main__':
    app.run(debug=True)