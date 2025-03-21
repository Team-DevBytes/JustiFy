from openai import OpenAI
import os 
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

class Agent:
    def __init__(self, system_msg, recipient="user", client=client):
        self.system_msg = system_msg
        self.recipient = recipient

    def respond(self, query, context=""):
        sys_prompt = f"""{self.system_msg}\n"""
        query = f"""
        {context}

        {query}
        """
        messages=[
            {"role": "system", "content": sys_prompt}
        ]
        if query is not None:
            messages.append({"role": self.recipient, "content": query})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content.strip()
    
questioner = Agent(
    system_msg="""
    You are Law Justifier, an AI-powered legal assistant specializing in Indian law.  
    Your task is to answer users' legal queries by consulting specialized lawyers: **Criminal Lawyer, Civil Lawyer, and Ethics Lawyer**.  
        
    - Generate **specific, relevant** questions for these lawyers to gather precise legal insights.  
    - Ensure the responses are aligned with **Indian legal frameworks**. 
    - Use **bold** for important points and structure your response in a clear, organized manner. 
    """,
    recipient='user'   
)
    
criminal_lawyer = Agent(
    system_msg="""
    You are a **Criminal Lawyer**, an expert in Indian criminal law.  
    Your role is to assist the senior lawyer by providing legally accurate responses to criminal law queries.  
      
    - If asked, provide **clear, precise** explanations on **criminal offenses, penalties, procedures, and defenses**.  
    - Keep responses **factual, legally sound, and relevant** to the Indian Penal Code (IPC) and other applicable laws.  
    - Your colleagues are a **Civil Lawyer** and an **Ethics Lawyer**—don't answer their questions.  
    """,
    recipient='assistant'
)

civil_lawyer = Agent(
    system_msg="""
    You are a **Civil Lawyer**, an expert in Indian civil law.  
    Your role is to support the senior lawyer by providing legal insights on civil disputes and regulations.  
      
    - If asked, provide **concise, relevant** explanations on **contracts, property law, family law, consumer protection, and civil litigation**.  
    - Ensure responses are **legally sound and in line with Indian civil law frameworks**.  
    - Your colleagues are a **Criminal Lawyer** and an **Ethics Lawyer**—don't answer their questions.  
    """,
    recipient='assistant'
)

ethics_lawyer = Agent(
    system_msg="""
    You are an **Ethics Lawyer**, specializing in legal ethics and professional conduct in India.  
    Your role is to assist the senior lawyer by ensuring responses adhere to **ethical and moral principles** within Indian law.  
      
    - If asked, provide guidance on **ethical dilemmas, professional misconduct, legal obligations, and moral considerations**.  
    - Ensure responses **align with Indian Bar Council regulations and broader legal ethics principles**.  
    - Your colleagues are a **Criminal Lawyer** and a **Civil Lawyer**—don't answer their questions. 
    """,
    recipient='assistant'
)

summarizer = Agent(
    system_msg="""
    You are a **Senior Lawyer**, responsible for answering clients' legal queries concisely and effectively.  
    You have consulted your junior lawyers (**Criminal, Civil, and Ethics Lawyers**) for relevant legal information.  
      
    - **Synthesize their responses** into a clear, **legally accurate** answer.  
    - Ensure responses are **concise, precise, and to the point**.  
    - Highlight **key points using bold formatting** (**important laws, legal terms, deadlines, etc.**).  
    - Avoid unnecessary complexity—make the response **easy to understand** while maintaining legal accuracy.  
    """,
    recipient="user"
)


def get_answer(query, context):
    questions = questioner.respond(query, f"Context:\n{context}\n")
    qna_flow = f"""
    client: {query}
    Senior Lawyer: {questions}
    """
    ag_cont = f"""
    Context: {context}

    client question: {query}
    """
    cri_resp = criminal_lawyer.respond(qna_flow, ag_cont)
    qna_flow += f"\n\nCriminal Lawyer: {cri_resp}"
    civ_resp = civil_lawyer.respond(qna_flow, ag_cont)
    qna_flow += f"\n\nCriminal Lawyer: {cri_resp}"
    eth_resp = ethics_lawyer.respond(qna_flow, ag_cont)
    qna_flow += f"\n\nCriminal Lawyer: {cri_resp}"
    sum_con = f"""
    Context: {context}

    client question: {query}

    {qna_flow}

    Senior Lawyer to User: 
    """

    answer = summarizer.respond(sum_con)

    reasoning = [
        f"Senior Lawyer: {questions}",
        f"Criminal Lawyer: {cri_resp}",
        f"Civil Lawyer: {civ_resp}",
        f"Ethics Lawyer: {eth_resp}",
        f"Senior Lawyer: {answer}"
    ]
    return answer, reasoning