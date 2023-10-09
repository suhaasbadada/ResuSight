import os
from bson import ObjectId
import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from typing import List, Optional
from db import mongo
from dataclasses import asdict

# USER SCHEMA
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
    user: Optional[User] = strawberry.UNSET
    token: Optional[str] = strawberry.UNSET


# RESUME SCHEMA
# Socials
@strawberry.input
class Links:
    website_name: str
    link: str


@strawberry.input
class MonthYear:
    month: str
    year: int

#Education
@strawberry.input
class Education:
    institute: str
    type_of_study: str
    start_date: MonthYear
    end_date: MonthYear
    percentage: float
    place: str
    country: str

# Experience
@strawberry.input
class Experience:
    company_name: str
    place: str
    country: str
    start_date: MonthYear
    end_date: MonthYear
    job_titles: List[str]
    job_description: str

#Projects
@strawberry.input
class Projects:
    project_name: str
    tech_used: List[str]
    description: str

#Publications
@strawberry.input
class Publication:
    title: str
    published_date: MonthYear
    published_at: str

# Resume
@strawberry.input
class Resume:
    username: str
    email: str
    full_name: str
    links: List[Links]
    job_title: Optional[str] = strawberry.UNSET 
    education: List[Education]
    skills: List[str]
    experience: Optional[List[Experience]] = strawberry.UNSET
    projects: List[Projects]
    languages: Optional[List[str]] = strawberry.UNSET
    publications: Optional[List[Publication]] = strawberry.UNSET

@strawberry.type
class UploadResponse:
    message: str
    user: Optional[User] = strawberry.UNSET

@strawberry.type
class UserDetails:
    username: Optional[str] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
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
    
    

@strawberry.type
class Query:
    @strawberry.field
    def get_my_details(info: Info, username: str) -> UserDetails:
        user = mongo.db.user_collection.find_one({'username': username})
        user_resume = mongo.db.resumes_collection.find_one({'username':username})
        print(user_resume)
        if user and user_resume:
            return UserDetails(username=user['username'], email=user['email'],message="there is an existing resume")
        if user:
            return UserDetails(username=user['username'], email=user['email'],message="yet to be uploaded")
        return UserDetails(username=None,email=None,message="Not a registered user")

schema=strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False))