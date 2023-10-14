import os
from flask import jsonify
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

OPENAI_API_KEY=os.getenv('OPENAI_KEY')
llm = OpenAI(openai_api_key=OPENAI_API_KEY,temperature=0.1)

templates=[
    """Question: {question}
    Answer: Let's think step by step. Give explanation why you picked these certain animals""",

    """Job Description: {job_description}
    Answer: Return 5 questions that an interviewer could ask based on this job description as a JSON.
    """
]


def jd_questions(job_description):
    prompt = PromptTemplate(template=templates[1], input_variables=["job_description"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    
    return llm_chain.run(job_description)
