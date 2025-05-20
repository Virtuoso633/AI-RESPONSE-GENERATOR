# Add content to backend/app/ai_service.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"  # You can change this to other models like "llama-3.3-70b-versatile"
    
    def generate_casual_response(self, query):
        """Generate a casual, conversational response to the query"""
        prompt = f"You are a friendly and casual assistant. Explain this in a conversational, easy-to-understand way: {query}"
        
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that speaks in a casual, friendly tone."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.7,
        )
        
        return completion.choices[0].message.content
    
    def generate_formal_response(self, query):
        """Generate a formal, academic response to the query"""
        prompt = f"You are a professional academic assistant. Provide a formal, detailed explanation of: {query}"
        
        completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant that speaks in a formal, academic tone."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.3,
        )
        
        return completion.choices[0].message.content
    
    def generate_responses(self, query):
        """Generate both casual and formal responses to the query"""
        casual_response = self.generate_casual_response(query)
        formal_response = self.generate_formal_response(query)
        
        return {
            "casual_response": casual_response,
            "formal_response": formal_response
        }
