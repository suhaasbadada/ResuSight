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

# Certifications
@strawberry.input
class Certifications:
    certification_name: str
    issue_date: MonthYear
    issuing_organization: str
    url: str

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
    certifications:Optional[List[Certifications]] = strawberry.UNSET
    experience: Optional[List[Experience]] = strawberry.UNSET
    projects: List[Projects]
    languages: Optional[List[str]] = strawberry.UNSET
    publications: Optional[List[Publication]] = strawberry.UNSET

####################################################################
@strawberry.type    
class LinksOutput:
    website_name: str
    link: str
@strawberry.type
class MonthYearOutput:
    month: str
    year: int
    
#Certifications
@strawberry.type
class CertificationsOutput:
    certification_name: str
    issue_date: MonthYearOutput
    issuing_organization: str
    url: str

# Experience
@strawberry.type
class ExperienceOutput:
    company_name: str
    place: str
    country: str
    start_date: MonthYearOutput
    end_date: MonthYearOutput
    job_titles: List[str]
    job_description: str

#Projects
@strawberry.type
class ProjectsOutput:
    project_name: str
    tech_used: List[str]
    description: str
@strawberry.type
class PublicationOutput:
    title: str
    published_date: MonthYearOutput
    published_at: str
    
@strawberry.type
class EducationOutput:
    institute: str
    type_of_study: str
    start_date: MonthYearOutput
    end_date: MonthYearOutput
    percentage: float
    place: str
    country: str
@strawberry.type
class ResumeOutput:
    _id: str
    username: str
    email: str
    full_name: str
    links: List[LinksOutput]
    job_title: Optional[str] = strawberry.UNSET 
    education: List[EducationOutput]
    skills: List[str]
    certifications: Optional[List[CertificationsOutput]] = strawberry.UNSET
    experience: Optional[List[ExperienceOutput]] = strawberry.UNSET
    projects: List[ProjectsOutput]
    languages: Optional[List[str]] = strawberry.UNSET
    publications: Optional[List[PublicationOutput]] = strawberry.UNSET

@strawberry.type
class UploadResponse:
    message: str
    user: Optional[User] = strawberry.UNSET

@strawberry.type
class UserDetails:
    username: Optional[str] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
    message: str
    resume: Optional[ResumeOutput] = strawberry.UNSET


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
        if user and user_resume:
            resume_output = ResumeOutput(
                            _id=str(user_resume['_id']),
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
            return UserDetails(username=user['username'], email=user['email'],message="there is an existing resume",resume=resume_output)
        if user:
            return UserDetails(username=user['username'], email=user['email'],message="yet to be uploaded")
        return UserDetails(username=None,email=None,message="Not a registered user")

    @strawberry.field
    def generate_interview_questions(info: Info, username: str) -> List[str]:
        resume=mongo.db.resumes_collection.find_one({'username':username})
        print(type(resume))
        if resume:
            return ['q1','q2','q3'] # use openai api functions here to get questions
        return []
        

schema=strawberry.Schema(query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=False))