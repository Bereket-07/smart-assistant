from langchain_community.vectorstores import Pinecone
from pinecone import Pinecone
from langchain_groq import ChatGroq
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_huggingface import HuggingFaceEmbeddings


from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory


from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder

import os



def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
def download_hugging_face_embeddings():
    print("downloading embedding model from hugging face")
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("downloadind ...... completed")
    return embedding
embedding = download_hugging_face_embeddings()


store = {}

def main_ai_chat_bot(data):
    # prompt = hub.pull("rlm/rag-prompt")

    load_dotenv()

    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')



    pc = Pinecone(api_key=PINECONE_API_KEY)

    index_name = "medicalchatbot"

    index = pc.Index(index_name)
    print(f'the index name {index_name} is there ')
    vectore_store = PineconeVectorStore(index=index, embedding=embedding)
    retriever = vectore_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 3, "score_threshold": 0.5},
    )

    llm = ChatGroq(model="llama3-8b-8192")
     
    ### Contextualize question ###
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
    )
    history_aware_retriever = create_history_aware_retriever(
     llm, retriever, contextualize_q_prompt
    )

    system_prompt = (
    "You are an assistant for medical based tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know and don't mention from the context and am not a doctor they aready know that you don't."
    "you can ask back if the question is not clear or anything you want to ask"
    "Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    ### Statefully manage chat history ###
    

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    response = conversational_rag_chain.invoke(
    {"input": data},
    config={
        "configurable": {"session_id": "abc123"}
    },  # constructs a key "abc123" in `store`.
    )["answer"]
    return response







