import strawberry
from typing import List, Optional

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

@strawberry.input
class JobDescription:
    job_title: str
    company: Optional[str] = strawberry.UNSET
    description: str
    submitted_by: str

@strawberry.type
class ContributedJds:
    company_name: str
    description: str
    job_title:str
    submitted_by: str

@strawberry.type
class ResumeQuestions:
    Questions: List[str]
    section: str

@strawberry.type
class JdQuestions:
    company_name: str
    interview_questions: List[str]
    job_title: str
    username: str
@strawberry.type
class UserResume:
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
class AllDetails:
    message: str
    contributed_jds: Optional[List[ContributedJds]] = strawberry.UNSET
    jd_questions: Optional[List[JdQuestions]] = strawberry.UNSET
    resume_questions: Optional[List[ResumeQuestions]] = strawberry.UNSET
    user_resume: Optional[UserResume]= strawberry.UNSET