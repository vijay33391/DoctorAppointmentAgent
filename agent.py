from langchain_groq import ChatGroq
from langchain_core.tools import tool
from pydantic import BaseModel,Field,field_validator
import re
import pandas as pd
from typing import Literal,List,Optional,Any
from typing_extensions import Annotated
from langgraph.types import Command
from typing_extensions import Annotated,TypedDict
from langgraph.types import Command
# import react agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.graph import START, StateGraph,END
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph import add_messages
from utils.llm import LLmodel
from prompt_library.prompt import system_prompt
from toolkit.tools import *

class Router(TypedDict):
    next: Literal["information_node","booking_node","FINISH"]
    reasoning: str
    
    
class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    id_number: int
    next: str
    query: str
    current_reasoning: str
    
    
class  DoctorAppointmentAgent:
    def __init__(self):
        llm=LLmodel()
        self.model=llm.get_model()
        
        
    def supervisor_node(self,state:AgentState) -> Command[Literal['information_node', 'booking_node', '__end__']]:
        print("**************************below is my state right after entering****************************")
        print(state)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"user's identification number is {state['id_number']}"},
        ] + state["messages"]

        print("***********************this is my message*****************************************")
        print(messages)

        # query = state['messages'][-1].content if state["messages"] else ""
        query = ''
        if len(state['messages']) == 1:
            query = state['messages'][0].content
            
        print("************below is my query********************")    
        print(query)

        response =self.model.with_structured_output(Router).invoke(messages)
        print("*"*10,response,"*"*10)

        goto = response["next"]

        print("********************************this is my goto*************************")
        print(goto)

        print("********************************")
        print(response["reasoning"])
                
        if goto == "FINISH":
            goto = END
            
        print("**************************below is my state****************************")
        print(state)

        if query:
            return Command(goto=goto, update={'next': goto, 
                                                'query': query, 
                                                'current_reasoning': response["reasoning"],
                                                'messages': [HumanMessage(content=f"user's identification number is {state['id_number']}")]
                            })
        return Command(goto=goto, update={'next': goto, 
                                            'current_reasoning': response["reasoning"]}
        )
    
    def information_node(self,state: AgentState) -> Command[Literal["supervisor"]]:
        print("*****************called information node************")
        
        system_prompt = """
    You are the Information Agent for a hospital appointment system.

    Your responsibilities:
    1. If the user asks about doctor availability, call the appropriate tool (check_doctor_availability or check_doctor_availability_by_specialization).
    2. If the user’s query is missing required information, ask ONE clarifying question.

    CRITICAL INSTRUCTIONS:
    - If you have successfully called a tool and obtained the availability (even if the result is "No slots"), **YOU MUST ANSWER THE USER with normal text**.
    - Do NOT call a tool again if you already have the answer in your history.
    - Assume the current year is 2024.
    """
        
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{messages}")
            ]
        )
        
        information_agent = create_react_agent(
            model=self.model,
            tools=[check_doctor_availability, check_doctor_availability_by_specialization],
            prompt=prompt
        )
        
        result = information_agent.invoke(state)
        
        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(content=result["messages"][-1].content, name="information_node")
                ]
            },
            goto="supervisor",
        )
        
        
    def booking_node(self,state: AgentState) -> Command[Literal["supervisor"]]:
    
        print("*****************called booking node************")
        
        booking_system_prompt = """
    You are the Booking Agent in a hospital appointment system.

    Your responsibilities:

    1. When the user wants to SET, CHANGE, or CANCEL an appointment:
        → You MUST call EXACTLY one of these tools:
            - set_appointment
            - cancel_appointment
            - reschedule_appointment

    2. If the user request is missing required information (example: missing date, doctor name, or ID number):
        → Ask ONE clear question to collect the missing information.
        → After receiving it, you MUST call the correct tool.

    3. NEVER respond with normal text if a tool call is required.
    4. You MAY answer normally only if the user is asking a general question NOT related to booking.
    5. Always assume the current year is 2024.
    """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", booking_system_prompt),
                ("placeholder", "{messages}"),
            ]
        )

        booking_agent = create_react_agent(
            model=self.model,
            tools=[set_appointment, cancel_appointment, reschedule_appointment],
            prompt=prompt
        )

        result = booking_agent.invoke(state)

        return Command(
            update={
                "messages": state["messages"] + [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name="booking_node"
                    )
                ]
            },
            goto="supervisor",
        )
    
    def workflow(self):
        # create the state graph
        self.graph=StateGraph(AgentState)
        self.graph.add_node("supervisor",self.supervisor_node)
        self.graph.add_node('information_node',self.information_node)
        self.graph.add_node('booking_node',self.booking_node)
        self.graph.add_edge(START,'supervisor')
        self.app=self.graph.compile()
        return self.app

        
