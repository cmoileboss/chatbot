import requests

class AiService:
    '''Service class to interact with the AI language model.'''

    def __init__(self, ai_model: str):
        '''Initialize the AI service with the specified model.
        Args:
            ai_model (str): The name of the AI model to use (e.g., "gpt-3.5-turbo", "llama3.2").
        '''
        self.ai_model = ai_model

    def response_local_llm(self, prompt: str) -> str:
        '''Call the local language model with the given prompt and return the response.'''
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.ai_model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]
    
    def converse_local_llm(self, messages: list[dict]) -> str:
        '''Call the local language model with the conversation history and return the response.
        Args:
            messages: List of {"role": "user"|"assistant", "content": str}
        '''
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.ai_model,
                "messages": messages,
                "stream": False
            }
        )
        return response.json()["message"]["content"]
    
aiservice = AiService(ai_model="llama3.2")
response = aiservice.response_local_llm("Quelle est la capitale de la France ?")
print(response)