from dataclasses import asdict
from datetime import datetime, timedelta
import os
import jwt
import strawberry
from strawberry.types import Info
from mongoDatabase.db import mongo
from strawberryGQL.gql_schema import AuthResponse, Resume, UploadResponse, User, UserInput
from werkzeug.security import generate_password_hash, check_password_hash

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
    def upload_or_update_resume(info: Info, resume:Resume) ->UploadResponse:
        existing_upload=mongo.db.resumes_collection.find_one({'$or': [{'username':resume.username},{'email':resume.email}]})
        if existing_upload:
            resume_dict=asdict(resume)
            mongo.db.resumes_collection.update_one({'$or': [{'username': resume.username}, {'email': resume.email}]}, {'$set': resume_dict})
            return UploadResponse(message='Update Successful', user=User(username=resume.username, email=resume.email))
        
        existing_user=mongo.db.user_collection.find_one({'$or': [{'username':resume.username},{'email':resume.email}]})
        if existing_user:
            resume_dict=asdict(resume)
            mongo.db.resumes_collection.insert_one(resume_dict)
            return UploadResponse(message='Upload Successful',user=User(username=resume.username,email=resume.email))
        
        return UploadResponse(message='Register before uploading.',user=None)