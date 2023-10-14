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

     """I will send a job description: {job_description}
    Answer: Now give me 5 questions that an interviewer could ask based on this particular job description. Return the response as a json
    """
]

inputs=[
    "list 5 animal names",
    """
    Experience : 0 To 3 Years

    Company Description
    Coapps.ai is a team of highly qualified individuals working to assist businesses in finding trusted digital service providers for software development, web & mobile app, digital branding, gaming & fintech app, NFT, and recruitment agencies across the world. Over 500 CRM application and fintech app projects for diverse sectors including healthcare, automotive, IT, and banking have been accomplished.


    Role Description
    This is a full-time remote role for a Full Stack Engineer. The Full Stack Engineer will be responsible for developing and maintaining both front-end and back-end applications, working with cross-functional teams, troubleshooting and debugging code, and collaborating with other software engineers to deliver high-quality solutions.


    Qualifications

    Back-End Web Development and Software Development skills
    Front-End Development and Full-Stack Development skills
    Cascading Style Sheets (CSS) knowledge
    Experience with database management systems
    Proficient in programming languages such as JavaScript, Python, and Ruby
    Experience with JavaScript frameworks such as React.js and Node.js
    Experience with agile development methodologies
    Bachelor's degree in Computer Science or related field
    Strong problem solving and analytical skills
    Knowledge in firebase, AWS, Microsoft Azure
    """

]

def hello_langchain():    
    template = templates[0]

    prompt = PromptTemplate(template=template, input_variables=["question"])

    llm = OpenAI(openai_api_key=OPENAI_API_KEY,temperature=0.6) #global

    llm_chain = LLMChain(prompt=prompt, llm=llm)

    question=inputs[0]

    return jsonify(llm_chain.run(question))

def jd_questions():
    template = templates[1]
    prompt = PromptTemplate(template=template, input_variables=["job_description"])


    llm_chain = LLMChain(prompt=prompt, llm=llm)

    job_description=inputs[1]
    
    return llm_chain.run(job_description)
