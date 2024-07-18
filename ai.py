import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import requests
from services import get_by_questioner_id
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage

# Loading environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Function to fetch data from a route
def fetch_data_from_route(questioner_id):
    data = get_by_questioner_id(questioner_id)
    return data

# Function to split large data into chunks
def split_data(data, max_chunk_size=2500):
    if isinstance(data, dict):
        data_str = str(data)
    elif isinstance(data, list):
        data_str = " ".join(map(str, data))
    else:
        data_str = str(data)

    data_chunks = [data_str[i:i + max_chunk_size] for i in range(0, len(data_str), max_chunk_size)]
    return data_chunks

# Function to process the fetched data
def chat_with_groq(user_message, questioner_id, language):
    processed_data = fetch_data_from_route(questioner_id)
    data_chunks = split_data(processed_data)

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

    config = {"configurable": {"session_id": questioner_id }} # session_id could be the user id 
    with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")

    response_content = ""
    MAX_RETRIES = 50
    BACKOFF_FACTOR = 2

    for chunk in data_chunks:
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                response = with_message_history.invoke(
                    {
                        "data": chunk,
                        "messages": [HumanMessage(content=user_message)],
                        "language": language,
                        "description": prompt_description
                    },
                    config=config
                )
                response_content += response.content
                break
            except requests.exceptions.HTTPError as err:
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    backoff_time = retry_after * (BACKOFF_FACTOR ** retry_count)
                    print(f"Rate limit exceeded. Retrying after {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    retry_count += 1
                else:
                    raise err

    return response_content.replace('*', '').replace('\n\n', '\n').replace('\n', ' ').strip()  # Remove asterisks and extra whitespace


