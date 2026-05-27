from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import DoctorAppointmentAgent
from langchain_core.messages import HumanMessage
import logging
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=FileResponse)
async def home():
    return "frontend/index.html"


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class UserQuery(BaseModel):
    id_number: int
    messages: str

# Initialize once
agent = DoctorAppointmentAgent()
app_graph = agent.workflow()

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# Main endpoint
@app.post("/execute")
async def execute_agent(user_input: UserQuery):

    try:

        messages = [
            HumanMessage(content=user_input.messages)
        ]

        query_data = {
            "messages": messages,
            "id_number": user_input.id_number,
            "next": "",
            "query": "",
            "current_reasoning": "",
        }

        response = app_graph.invoke(
            query_data,
            config={"recursion_limit": 20}
        )

        return {
            "messages": [
                {
                    "type": msg.type,
                    "content": msg.content
                }
                for msg in response["messages"]
            ]
        }

    except Exception as e:

        logger.error(f"Execution Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )