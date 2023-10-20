import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

OPENAI_API_KEY=os.getenv('OPENAI_KEY')
llm = OpenAI(openai_api_key=OPENAI_API_KEY,temperature=0.6,max_tokens=2500)

templates=[
    """Question: {question}
    Answer: Let's think step by step. Give explanation why you picked these certain animals""",

    """Job Description: {job_description}
       Answer: Return the job_title,company_name and 5 questions that an interviewer could ask based on this job description,as a JSON.
    """,

        """Given the following resume data:

                {resume}

                Please generate a set of interview questions categorized by the following domains:
                - Job Title
                - Skills
                - Experience
                - Projects
                - Languages
                - Publications

                Return the questions as a JSON with keys corresponding to the domains listed above.
                The questions should be in the topics of the details, in depth and technical.
                """,
        """
        Generate a list of advanced technical interview questions for the '{section_name}' section of a resume, where the content is related to {section_content}. 
        These questions should assess the candidate's deep understanding and practical experience in the specified domain.
        Consider asking questions that require problem-solving, scenario-based questions, and in-depth technical knowledge. 
        Ensure that the questions cover both theoretical and practical aspects of the field. 
        You may also include concepts in the subject of the field and ask questions from that.
        The output should be formatted as a JSON object with one key: 'Questions'. 
        The value associated with 'Questions' should be a list of all the advanced questions generated.
        """
    
]


def jd_questions(job_description):
    prompt = PromptTemplate(template=templates[1], input_variables=["job_description"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    
    return llm_chain.run(job_description)

def resume_questions(resume):
    prompt = PromptTemplate(template=templates[2], input_variables=["resume"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return llm_chain.run(resume)    

def resume_section_questions(section_name,section_content):
    prompt = PromptTemplate(template=templates[3], input_variables=["section_name","section_content"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    return llm_chain.run(section_name=section_name,section_content=section_content) 