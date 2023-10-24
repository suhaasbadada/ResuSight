from datetime import datetime, timedelta
import json
import os
from typing import List
import jwt
import requests
import strawberry
from strawberry.types import Info
from mongoDatabase.db import mongo
from gpt.langchain_models import jd_questions
from strawberryGQL.gql_schema import AuthResponse, CertificationsOutput, EducationOutput, ExperienceOutput, LinksOutput, MonthYearOutput, ProjectsOutput, PublicationOutput, ResumeOutput, User, UserDetails
from werkzeug.security import check_password_hash

class TokenManager:
    def __init__(self):
        self.token=''

    def set_token(self,token_value):
        self.token=token_value
    
    def get_token(self):
        return self.token
    
    def delete_token(self):
        self.token=''

token_manager = TokenManager()


@strawberry.type
class Query:
    @strawberry.field
    def login_user(info: Info,username: str, password: str) ->AuthResponse:
        user=mongo.db.user_collection.find_one({'username':username})

        if user and check_password_hash(user['password'],password):
            token = jwt.encode({'user': username, 'exp': datetime.utcnow() + timedelta(days=1), 'app': 'flask'}, os.getenv("JWT_KEY"), algorithm='HS256')
            token_manager.set_token(token)
            return AuthResponse(message='Login Successful',user=User(username=user['username'], email=user['email']), token=token)
        
        return AuthResponse(message='Invalid Credentials', user=None, token=None)
    
    @strawberry.field
    def get_my_details(info: Info, username: str) -> str:
        try:
            token=token_manager.get_token()
            headers = {"Authorization":token}

            if not token:
                return "No authorization token provided"

            response = requests.get(f"http://127.0.0.1:5000/info/{username}",headers=headers)
            response.raise_for_status() 
            data = response.json()
            print(data)
            return str(data)
        except requests.exceptions.RequestException as e:
            return "Error, request issue"  
        except Exception as e:
            return "Error, an unexpected issue" 
    
    @strawberry.field
    def logout_user(info: Info) -> str:
        if not token_manager.get_token():
            return "Nobody Logged in"
        
        token_manager.delete_token()
        return "Logout Successful"
