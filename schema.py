import os
import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongo

user_collection=os.getenv('MONGO_COLLECTION_NAME_USERS')

@strawberry.type
class User:
    username: str
    email: str


@strawberry.input
class UserInput:
    username: str
    email: str
    password: str

@strawberry.type
class AuthResponse:
    message: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register_user(info: Info, user_input: UserInput) -> AuthResponse:
        username=user_input.username
        email=user_input.email
        password=user_input.password

        existing_user=mongo.db.user_collection.find_one({'$or': [{'username':username},{'email':email}]})

        if existing_user:
            return AuthResponse(message='Username or email already exists.')

        hashed_password=generate_password_hash(password)
        new_user={
            'username':username,
            'email':email,
            'password':hashed_password
        }
        mongo.db.user_collection.insert_one(new_user)
        return AuthResponse(message='Registration Successful. Proceed to log in')
    
    @strawberry.mutation
    def login_user(info: Info,username: str, password: str) ->AuthResponse:
        user=mongo.db.user_collection.find_one({'username':username})

        if user and check_password_hash(user['password'],password):
            return AuthResponse(message='Login Successful')
        
        return AuthResponse(message='Invalid Credentials')

@strawberry.type
class Query:
    @strawberry.field
    def get_user_by_username(info: Info, username: str) -> User:
        user = mongo.db.user_collection.find_one({'username': username})
        if user:
            return User(username=user['username'], email=user['email'])
        return None

schema=strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False))