import os
import jwt
import requests
import strawberry
from strawberry.types import Info
from mongoDatabase.db import mongo
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from strawberryGQL.gql_schema import AllDetails, AuthResponse, CertificationsOutput, ContributedJds, EducationOutput, ExperienceOutput, JdQuestions, LinksOutput, MonthYearOutput, ProjectsOutput, PublicationOutput, ResumeOutput, ResumeQuestions, User, UserDetails, UserResume


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
    def get_my_details(info: Info, username: str) -> AllDetails:
        try:
            token=token_manager.get_token()
            headers = {"Authorization":token}

            if not token:
                return "No authorization token provided"

            website_url=os.getenv('WEBSITE_URL')
            response = requests.get(f"{website_url}/info/{username}",headers=headers)
            response.raise_for_status() 
            data = response.json()

            contributed_jds = [ContributedJds(**jd_data) for jd_data in data.get("Contributed JDs", [])]
            jd_questions = [JdQuestions(**jd_question) for jd_question in data.get("JD Questions", [])]
            resume_questions = [ResumeQuestions(**rq) for rq in data.get("Resume Questions", [])]

            user_resume_data = data.get("User Resume", {})
            user_resume=user_resume_data
            resume_output = UserResume(
                            username=user_resume['username'],
                            email=user_resume['email'],
                            full_name=user_resume['full_name'],
                            links=[
                                LinksOutput(website_name=link['website_name'], link=link['link'])
                                for link in user_resume['links']
                            ],
                            job_title=user_resume.get('job_title', None),
                            education=[
                                EducationOutput(
                                    institute=edu['institute'],
                                    type_of_study=edu['type_of_study'],
                                    start_date=MonthYearOutput(month=edu['start_date']['month'], year=edu['start_date']['year']),
                                    end_date=MonthYearOutput(month=edu['end_date']['month'], year=edu['end_date']['year']),
                                    percentage=edu['percentage'],
                                    place=edu['place'],
                                    country=edu['country']
                                )
                                for edu in user_resume['education']
                            ],
                            skills=user_resume['skills'],
                            certifications=[CertificationsOutput(
                                certification_name=certs['certification_name'],
                                issue_date=MonthYearOutput(month=certs['issue_date']['month'],year=certs['issue_date']['year']),
                                issuing_organization=certs['issuing_organization'],
                                url=certs['url']
                            )for certs in user_resume.get('certifications',[])],
                            experience=[
                                ExperienceOutput(
                                    company_name=exp['company_name'],
                                    place=exp['place'],
                                    country=exp['country'],
                                    start_date=MonthYearOutput(month=exp['start_date']['month'], year=exp['start_date']['year']),
                                    end_date=MonthYearOutput(month=exp['end_date']['month'], year=exp['end_date']['year']),
                                    job_titles=exp['job_titles'],
                                    job_description=exp['job_description']
                                )
                                for exp in user_resume.get('experience', [])
                            ],
                            projects=[
                                ProjectsOutput(
                                    project_name=proj['project_name'],
                                    tech_used=proj['tech_used'],
                                    description=proj['description']
                                )
                                for proj in user_resume['projects']
                            ],
                            languages=user_resume.get('languages', []),
                            publications=[
                                PublicationOutput(
                                    title=pub['title'],
                                    published_date=MonthYearOutput(month=pub['published_date']['month'], year=pub['published_date']['year']),
                                    published_at=pub['published_at']
                                )
                                for pub in user_resume.get('publications', [])
                            ]
                        )
            return AllDetails(
                message="Data fetched successfully",
                contributed_jds=contributed_jds,
                jd_questions=jd_questions,
                resume_questions=resume_questions,
                user_resume=resume_output,
            )
         
        except Exception as e:
            return AllDetails(message="Error, an unexpected issue")
    
    @strawberry.field
    def logout_user(info: Info) -> str:
        token = token_manager.get_token()

        if not token:
            return "Invalid request"

        try:
            jwt.decode(token, os.getenv("JWT_KEY"), algorithms=['HS256'])
            token_manager.delete_token()
            return "Logout Successful"
        except jwt.ExpiredSignatureError:
            return "Token has expired. Please log in again."
        except jwt.DecodeError:
            return "Invalid token. Please log in again."
