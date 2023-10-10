from dataclasses import asdict
import jwt
import strawberry
from strawberry.types import Info
from db import mongo
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
    def login_user(info: Info,username: str, password: str) ->AuthResponse:
        user=mongo.db.user_collection.find_one({'username':username})

        if user and check_password_hash(user['password'],password):
            user_info = {'username': user['username'], 'email': user['email']}
            token = jwt.encode(user_info, "secret", algorithm="HS256")
            return AuthResponse(message='Login Successful',user=User(username=user['username'], email=user['email']), token=token)
        
        return AuthResponse(message='Invalid Credentials', user=None, token=None)

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