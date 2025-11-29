import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API")

class LLmodel:
    def __init__(self, model_name="openai/gpt-oss-120b",temperature=0):
        if not model_name:
            raise ValueError("Model name must be provided.")
        self.model_name = model_name
        self.api_key = GROQ_API_KEY
        self.model= ChatGroq(model_name=self.model_name, api_key=self.api_key, temperature=temperature)
    
    def get_model(self):
        return self.model
    
# Example usage:
if __name__ == "__main__":
    llm = LLmodel()
    model = llm.get_model()
    response = model.invoke("Hello, how are you?")
    print(response)