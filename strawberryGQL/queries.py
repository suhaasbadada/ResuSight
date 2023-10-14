import json
from typing import List
import strawberry
from strawberry.types import Info
from db import mongo
from gpt.langchain_models import jd_questions
from strawberryGQL.gql_schema import CertificationsOutput, EducationOutput, ExperienceOutput, LinksOutput, MonthYearOutput, ProjectsOutput, PublicationOutput, ResumeOutput, UserDetails

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
    def generate_questions_resume(info: Info, username: str) -> List[str]:
        resume=mongo.db.resumes_collection.find_one({'username':username})
        print(type(resume))
        if resume:
            return ['q1','q2','q3'] # use openai api functions here to get questions
        return []
    
    @strawberry.field
    def generate_questions_jd(info: Info, job_description: str) -> List[str]:
        questions=jd_questions(job_description)
        print(questions,type(questions),json.loads(questions))
        return json.loads(questions)['Questions']
