import os
import boto3
import streamlit as st
import textwrap
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from utils import bedrock, print_ww
from utils.functions import (print_relevant_documents_from_metadata,
                             print_relevant_documents_from_table_desc,
                             get_relevant_documents_from_metadata,
                             get_relevant_documents_from_table_desc,
                             extract_column_and_desc,
                             get_sql_query,
                             wrapper_function,
                             read_yaml,
                             extract_sql_from_response,
                             get_athena_client,
                             get_athena_response,
                             get_summary)

from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain

ROOT_DIR_DB = "db"
table_vec_db_path = os.path.join(ROOT_DIR_DB, "table_desc_vec_db_faiss")
metadata_vec_db_path = os.path.join(ROOT_DIR_DB, "subset_metadata_vectorstore_faiss")

config = read_yaml("configs/config.yaml")
credentials = config["credentials"]
models = config["models"]
hyperparameters = config["hyperparameters"]

AWS_DEFAULT_REGION = credentials["AWS_DEFAULT_REGION"]
BEDROCK_ASSUME_ROLE = credentials["BEDROCK_ASSUME_ROLE"]
ATHENA_ROLE_ARN = credentials["ATHENA_ROLE_ARN"]
ATHENA_ROLE_SESSION_NAME = credentials["ATHENA_ROLE_SESSION_NAME"]
ATHENA_DEFAULT_REGION = credentials["ATHENA_DEFAULT_REGION"]
ATHENA_DATABASE_NAME = credentials["ATHENA_DATABASE_NAME"]
ATHENA_OUTPUT_LOCATION = credentials["ATHENA_OUTPUT_LOCATION"]



model_id = models["model_id"]
max_tokens_to_sample = hyperparameters["max_tokens_to_sample"]
temperature = hyperparameters["temperature"]

# boto3 bedrock client
bedrock = boto3.client('bedrock', AWS_DEFAULT_REGION)

# Claude LLM using Bedrock
llm = Bedrock(model_id=model_id, 
              client=bedrock, 
              model_kwargs={"max_tokens_to_sample":max_tokens_to_sample, "temperature":temperature})

conversation = ConversationChain(llm=llm, verbose=False)

# Bedrock Embeddings
bedrock_embeddings = BedrockEmbeddings(client=bedrock)

# Initialize table and subset metadata vector DB
table_DB = FAISS.load_local(table_vec_db_path, bedrock_embeddings)
metadata_DB = FAISS.load_local(metadata_vec_db_path, bedrock_embeddings)

# Get athena client
athena_client = get_athena_client(ATHENA_ROLE_ARN, ATHENA_ROLE_SESSION_NAME, ATHENA_DEFAULT_REGION)
        
st.set_page_config(page_title='Covestro Databot', layout='wide')

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []
if "temp" not in st.session_state:
    st.session_state["temp"] = ""

def clear_text():
    st.session_state["temp"] = st.session_state["input"]
    st.session_state["input"] = ""

# Define function to get user input
def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input", 
                            placeholder="Your DATA AI assistant! Ask me related to SAP-BW Data", 
                            on_change=clear_text,    
                            label_visibility='hidden')
    input_text = st.session_state["temp"]
    return input_text


with st.sidebar:
    st.markdown("---")
    st.markdown("# About this solution")
    st.markdown("""To enable business users to ask questions and get answers about Covestro business data in natural language 
    instead of having to consult with BI experts in order to generate complex queries.""")


# Set up the Streamlit app layout
st.title("Chat with your SAP-BW Data")
st.write(" Powered by 🦜 LangChain + AWS + Streamlit")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Get the user input
user_input = get_text()


if user_input:
    with st.spinner("Generating sql statement and summary, Please wait..."):
        llm_response = wrapper_function(conversation=conversation, 
                                        user_query=user_input, 
                                        table_vec_DB=table_DB, 
                                        metadata_vec_DB=metadata_DB)
        
        sql_query = extract_sql_from_response(llm_response=llm_response)

        database_response = get_athena_response(sql_query, athena_client, 
                                                ATHENA_DATABASE_NAME, ATHENA_OUTPUT_LOCATION)
        
        if database_response == "No data found":
            summary = "No data found for particular user query. Please try with another query."

        elif database_response == "failed":
            summary = "Query execution over Athena failed. Please try with another user query."
        
        elif database_response == "StartQueryExecutin error":
            summary = "Error occurred when calling the StartQueryExecution operation on Amazon Athena"

        else:
            summary = get_summary(database_response, conversation)

        output = f"""SQL Statement: {sql_query}\n
                    summary: {summary}"""

        st.session_state.past.append(user_input)  
        st.session_state.generated.append(output)

# Allow to download as well
download_str = []

# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.info(st.session_state["past"][i],icon="🧐")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])
                            
    # Can throw error - requires fix
    download_str = '\n'.join(download_str)
    
    if download_str:
        st.download_button('Download',download_str)

