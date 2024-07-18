import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import requests
from services import get_by_questioner_id
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage



#  loading environment variables
load_dotenv()
#  accesing the evnironment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# function to fetch data from a route
def fetch_data_from_route(quetioner_id):
    
    
    data = get_by_questioner_id(quetioner_id)
    return data
#  Function to process the fetched data
def chat_with_groq(user_message,quetioner_id,language):
    processesed_data = fetch_data_from_route(quetioner_id)
    data_template = '''
        You are a helpful assistant. Here is the collected data:
        
        data: {data}
        Answer all questions based on this data to the best of your ability in {language}.
    '''
    prompt_description = "This is a chat interaction with an AI assistant using Groq."
    prom = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                data_template
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    store = {}

    model = ChatGroq(model="llama3-8b-8192")
    chain = prom | model

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]
    config = {"configurable": {"session_id":quetioner_id }} # session_id could be the user id 
    with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")
    
    response = with_message_history.invoke(
        {
            "data": processesed_data,
            "messages": [HumanMessage(content=user_message)],
            "language": language,
            "description": prompt_description
        },
        config=config
    )
    return response.content.replace('*', '').replace('\n\n', '\n').replace('\n', ' ').strip()  # Remove asterisks and extra whitespace
