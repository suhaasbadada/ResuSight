
from datetime import timedelta
import os
import strawberry
from mongoDatabase.db import mongo
from flask import Flask
from strawberryGQL.queries import Query
from strawberryGQL.mutations import Mutation
from strawberry.schema.config import StrawberryConfig
from strawberry.flask.views import GraphQLView
from flask_swagger_ui import get_swaggerui_blueprint
from mongoDatabase.db import mongo

schema=strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False))
class StrawberryView(GraphQLView):
    schema = schema

def create_app():
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

    app.add_url_rule(
        "/graphql",
        view_func=GraphQLView.as_view("graphql_view", schema=schema,graphiql=True),
    )

    return app