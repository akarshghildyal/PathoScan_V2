from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from openai import OpenAI
import os, json, re
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import streamlit as st

load_dotenv()

def get_llm():
    """Initialize the LLM for agents"""
    return ChatOpenAI(
        model="google/gemini-2.0-flash-thinking-exp:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.3
    )

def get_openai_client():
    """Initialize OpenAI client for direct API calls"""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

def clean_json_response(raw_response: str) -> str:
    """Clean JSON response from markdown formatting"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_response)
    if match:
        return match.group(1).strip()
    return raw_response.strip()

def extract_text_from_pdf(file) -> str:
    """Extract text from uploaded PDF file"""
    return "\n".join([page.extract_text() or "" for page in PdfReader(file).pages])

def blood_test_analysis_tool(input_text: str) -> str:
    """Tool: Analyze blood test report and extract abnormal values"""
    llm = get_llm()
    prompt = f"""
    You are a blood test analyst. Analyze the following blood test report and extract important information.
    
    Return a JSON object with the following structure, containing on the abnormal values:
    {{
        "summary": "Brief summary of the overall blood test results",
        "abnormal_values": [
            {{
                "parameter": "Parameter name",
                "value": "Measured value",
                "reference_range": "Normal range",
                "interpretation": "Brief explanation of what this abnormal value might indicate"
            }}
        ]
    }}
    
    Report: {input_text}
    """
    
    response = llm.invoke(prompt)
    print("Blood test analysis raw response:", response.content)
    cleaned_response = clean_json_response(response.content)
    
    try:
        json_response = json.loads(cleaned_response)
        return json.dumps(json_response, indent=2)
    except json.JSONDecodeError:
        return f"Error: Could not parse JSON response. Raw response: {cleaned_response}"

def health_issue_identifier_tool(abnormal_values_json: str) -> str:
    """Tool: Identify potential health issues based on abnormal blood values"""
    llm = get_llm()
    prompt = f"""
    You are a medical expert. Given these abnormal blood test values, identify potential health issues.
    
    Return a JSON object with the following structure:
    {{
        "potential_health_issues": [
            {{
                "issue": "Name of potential health issue",
                "related_parameters": ["Parameter 1", "Parameter 2"],
                "confidence": "High/Medium/Low",
                "explanation": "Brief explanation of why these parameters suggest this issue"
            }}
        ]
    }}
    
    Abnormal Values: {abnormal_values_json}
    """
    
    response = llm.invoke(prompt)
    print("Health issue identifier raw response:", response.content)
    cleaned_response = clean_json_response(response.content)
    
    try:
        json_response = json.loads(cleaned_response)
        return json.dumps(json_response, indent=2)
    except json.JSONDecodeError:
        return f"Error: Could not parse JSON response. Raw response: {cleaned_response}"

def lifestyle_advice_tool(health_issues_json: str) -> str:
    """Tool: Provide lifestyle recommendations based on identified health issues"""
    llm = get_llm()
    prompt = f"""
    You are a health advisor. Given these potential health issues, provide actionable lifestyle recommendations.
    
    Return a JSON object with the following structure:
    {{
        "lifestyle_recommendations": [
            {{
                "category": "Diet/Exercise/Sleep/etc.",
                "recommendation": "Specific actionable advice",
                "related_issues": ["Health issue 1", "Health issue 2"],
                "importance": "High/Medium/Low"
            }}
        ]
    }}
    
    Health Issues: {health_issues_json}
    """
    
    response = llm.invoke(prompt)
    print("Lifestyle advice raw response:", response.content)
    cleaned_response = clean_json_response(response.content)
    
    try:
        json_response = json.loads(cleaned_response)
        return json.dumps(json_response, indent=2)
    except json.JSONDecodeError:
        return f"Error: Could not parse JSON response. Raw response: {cleaned_response}"

def create_pathoscan_agent():
    """Create an agentic system for blood test analysis"""
    llm = get_llm()

    tools = [
        Tool(
            name="BloodTestAnalyzer",
            func=blood_test_analysis_tool,
            description="Analyzes blood test reports and extracts abnormal values. Input should be the text extracted from a blood test report."
        ),
        Tool(
            name="HealthIssueIdentifier",
            func=health_issue_identifier_tool,
            description="Identifies potential health issues based on abnormal blood test values. Input should be a JSON string containing abnormal values."
        ),
        Tool(
            name="LifestyleAdvisor",
            func=lifestyle_advice_tool,
            description="Provides lifestyle recommendations based on identified health issues. Input should be a JSON string containing potential health issues."
        )
    ]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=5 
    )

    return agent

def process_blood_test_report(extracted_text):
    """Process blood test report using the agentic system"""
    agent = create_pathoscan_agent()
    
    agent_prompt = f"""
    I have a blood test report. Here's the text extracted from it:
    {extracted_text}
    
    Please follow these steps:
    1. First, analyze the blood test values and identify abnormal values using the BloodTestAnalyzer tool.
    2. Next, determine potential health issues based on these abnormal values using the HealthIssueIdentifier tool.
    3. Finally, provide lifestyle recommendations based on the identified health issues using the LifestyleAdvisor tool.
    
    Organize your response in a clear structure with sections for each step.
    """
    
    try:
        agent_response = agent.run(agent_prompt)
        return agent_response
    except Exception as e:
        return f"Error in agent execution: {str(e)}"

def personalized_chat(question, context, report_analysis):
    """Answer user questions about their blood test results"""
    client = get_openai_client()
    
    system_prompt = """
    You are a health assistant AI. A user has uploaded their pathology report and received analysis and lifestyle advice.
    Use the context from their report and previous analyses to answer their questions precisely and responsibly.
    
    Important guidelines:
    - Be clear and concise in your responses
    - Avoid speculative medical advice
    - Always remind them to consult their healthcare provider for professional medical advice
    - When referring to data, cite specific values from their report
    - Focus on providing educational information rather than diagnosis
    """
    
    full_context = f"""
    Blood Report Analysis:
    {report_analysis}
    
    Additional Context:
    {context}
    
    User Question: {question}
    """
    
    response = client.chat.completions.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_context},
        ],
        temperature=0.5
    )
    
    return response.choices[0].message.content.strip()

import re
import json

def extract_sections_from_agent_response(response):
    """Extract structured sections from agent response"""
    results = {}

    blood_analysis_match = re.search(
        r"1\.\s*(?:Abnormal Blood Test Values|Blood Test Analysis|Blood Test Analysis using BloodTestAnalyzer Tool).*?\n(.*?)(?=2\.\s*(?:Potential Health Issues|Health Issue Identification using HealthIssueIdentifier Tool)|$)", 
        response, 
        re.DOTALL
    )
    if blood_analysis_match:
        results["blood_analysis"] = blood_analysis_match.group(1).strip()

        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", results["blood_analysis"])
        if json_match:
            try:
                results["blood_analysis_json"] = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

    health_issues_match = re.search(
        r"2\.\s*(?:Potential Health Issues|Health Issue Identification using HealthIssueIdentifier Tool).*?\n(.*?)(?=3\.\s*(?:Lifestyle Recommendations|Lifestyle Recommendations using LifestyleAdvisor Tool)|$)", 
        response, 
        re.DOTALL
    )
    if health_issues_match:
        results["health_issues"] = health_issues_match.group(1).strip()

        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", results["health_issues"])
        if json_match:
            try:
                results["health_issues_json"] = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

    lifestyle_match = re.search(
        r"3\.\s*(?:Lifestyle Recommendations|Lifestyle Recommendations using LifestyleAdvisor Tool).*?\n(.*)", 
        response, 
        re.DOTALL
    )
    if lifestyle_match:
        results["lifestyle_recommendations"] = lifestyle_match.group(1).strip()

        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", results["lifestyle_recommendations"])
        if json_match:
            try:
                results["lifestyle_recommendations_json"] = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

    return results

