import json
import os
import boto3
from utils import bedrock, print_ww
import yaml
import re
import time
import pandas as pd


def read_yaml(path_to_yaml: str) -> dict:
    """
    Reads a YAML file and returns its contents as a dictionary.

    Args:
        path_to_yaml (str): The file path to the YAML file.

    Returns:
        dict: The contents of the YAML file as a dictionary.
    """

    with open(path_to_yaml) as yaml_file:
        content = yaml.safe_load(yaml_file)
    return content

# print relevant documents after similarity seacrh with table description
def print_relevant_documents_from_table_desc(user_query:str, vecDB):
    """
    Prints the relevant documents fetched from a vector database based on the user's query.

    This function takes a user's query, generates its embedding using the vector database's 
    embedding function, and performs a similarity search to retrieve the most relevant documents.
    The number of retrieved documents and their content are then printed.

    Args:
        user_query (str): The query provided by the user to search for relevant documents.
        vecDB: An instance of the vector database that supports embedding generation 
               and similarity search operations.

    Returns:
        None
    """
    user_query_embedding = vecDB.embedding_function(user_query)
    relevant_documents = vecDB.similarity_search_by_vector(user_query_embedding, k=1)
    print(f'{len(relevant_documents)} documents are fetched which are relevant to the query.')
    print('----')
    for i, rel_doc in enumerate(relevant_documents):
        print_ww(f'## Document {i+1}: {rel_doc.page_content}.......')
        print('---')
        
# get relevant documents after similarity seacrh with table description   
def get_relevant_documents_from_table_desc(user_query:str, vecDB):
    """
    Retrieves relevant documents from a vector database based on the user's query.

    This function generates an embedding for the given query using the vector database's 
    embedding function and performs a similarity search to fetch the most relevant documents.

    Args:
        user_query (str): The user's query to search for relevant documents.
        vecDB: An instance of the vector database that supports embedding generation 
               and similarity search operations.

    Returns:
        list: A list of relevant documents fetched from the vector database.
    """
    user_query_embedding = vecDB.embedding_function(user_query)
    relevant_documents = vecDB.similarity_search_by_vector(user_query_embedding, k=1)
    return relevant_documents

# print relevant documents after similarity seacrh with metadata vectorstore
def print_relevant_documents_from_metadata(user_query: str, vecDB, k: int = 50)->str:
    """
    Prints the relevant documents fetched from a vector database using metadata-based similarity search.

    This function takes a user's query, generates its embedding using the vector database's 
    embedding function, and performs a similarity search to retrieve the top `k` most relevant 
    documents, which are then printed along with their content.

    Args:
        user_query (str): The query provided by the user to search for relevant documents.
        vecDB: An instance of the vector database that supports embedding generation 
               and similarity search operations.
        k (int, optional): The number of relevant documents to retrieve. Defaults to 50.

    Returns:
        None
    """
    user_query_embedding = vecDB.embedding_function(user_query)
    relevant_documents = vecDB.similarity_search_by_vector(user_query_embedding, k=k)
    print(f'{len(relevant_documents)} documents are fetched which are relevant to the query.')
    print('----')
    for i, rel_doc in enumerate(relevant_documents):
        print_ww(f'## Document {i+1}: {rel_doc.page_content}.......')
        print('---')
        
# get relevant documents after similarity seacrh with metadata vectorstore      
def get_relevant_documents_from_metadata(user_query: str, vecDB, k: int = 50)->list:
    """
    Retrieves relevant documents from a vector database using metadata-based similarity search.

    This function generates an embedding for the user's query using the vector database's 
    embedding function and performs a similarity search to fetch the top `k` most relevant 
    documents.

    Args:
        user_query (str): The query provided by the user to search for relevant documents.
        vecDB: An instance of the vector database that supports embedding generation 
               and similarity search operations.
        k (int, optional): The number of relevant documents to retrieve. Defaults to 50.

    Returns:
        list: A list of relevant documents fetched from the vector database, where each document
              contains metadata and content.
    """
    user_query_embedding = vecDB.embedding_function(user_query)
    relevant_documents = vecDB.similarity_search_by_vector(user_query_embedding, k=k)
    return relevant_documents

# extract column and thier description from relevant documents after similarity search with metadata vectorstore
def extract_column_and_desc(relevant_docs_from_metadata: list)->list:
    """
    Extracts column names and their descriptions from a list of relevant documents.

    This function parses the content of each document to retrieve the column name 
    and a short description. It then organizes this information into a list of dictionaries.

    Args:
        relevant_docs_from_metadata (list): A list of documents, where each document has 
                                            a `page_content` attribute containing metadata.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
              - "column_name" (str): The name of the column.
              - "short_description" (str): A short description of the column.
    """
    relevant_columns_desc_list = []
    for doc in relevant_docs_from_metadata:
        temp = {}
        content = doc.page_content
        col_name = content.split("\n")[1].split(":")[1].strip()
        short_desc = content.split("\n")[3].split(":")[1].strip()
        temp["column_name"]= col_name
        temp["short_description"]= short_desc
        relevant_columns_desc_list.append(temp)
    return relevant_columns_desc_list

# get sql query
def get_sql_query(conversation, required_table_name, user_query, vecDB, k: int = 50):
    """
    Generates an SQL query based on a user's query, relevant table, and metadata from a vector database.

    This function refines the user query, retrieves relevant column descriptions using a similarity 
    search from a vector database, and constructs a final prompt to generate the SQL query through 
    an AI-powered conversation system.

    Args:
        conversation: An AI-powered conversation model or assistant capable of processing prompts 
                      and generating SQL queries.
        required_table_name (str): The name of the database table to use in the query.
        user_query (str): The user's input query or requirement for which an SQL query is to be generated.
        vecDB: An instance of the vector database that supports embedding generation 
               and similarity search operations.
        k (int, optional): The number of relevant documents to fetch for similarity search. Defaults to 50.

    Returns:
        str: The generated SQL query as a string.
    """
    updated_user_query = f"""Search {required_table_name} to find relevant columns required to create a SQL code for given user_query: {user_query}"""
    relevant_docs_from_metadata = get_relevant_documents_from_metadata(updated_user_query, vecDB, k)
    relevant_columns_desc_list = extract_column_and_desc(relevant_docs_from_metadata)
#     final_prompt = final_prompt = f"""You are a SQL developer who is expert in writing SQL queries. Use below given columns and their description to understand which columns are required from table {required_table_name} to create SQL query for, {user_query}.\n
#                    Columns and their description are: {relevant_columns_desc_list}.\n
#                    As a final output provide me with a sql query. Don't try to make columns name on your own, if you don't get the right columns, ask user to query again with more clarification on columns name. Use table name which is provided above to complete your query.
# """
    final_prompt = f"""Give me only a sql statement based on columns: {relevant_columns_desc_list} and table: {required_table_name} to find user_query: {user_query}. Negative prompt: No explanation needed. output format: alwyas end sql_statement with ``;`` and use (days.month.year) date format like this ``01.01.2023```"""
    
    response = conversation.predict(input=final_prompt)
    return response

# wrapper function
def wrapper_function(conversation, user_query:str, table_vec_DB, metadata_vec_DB, k: int = 50):
    relevant_document = get_relevant_documents_from_table_desc(user_query, table_vec_DB)
    required_table_name = relevant_document[0].page_content.split("\n")[0].replace("\ufeff", "").split(":")[1].strip()
    result = get_sql_query(conversation, required_table_name, user_query, metadata_vec_DB, k)
    return result


# def extract_sql_from_response(llm_response:str)->str:
#     start_index = llm_response.index('{')
#     end_index = llm_response.index('}')
#     req_string = llm_response[start_index:end_index+1]
#     temp = json.loads(req_string)
#     sql_query = temp["sql_statement"]
#     return req_string

def extract_sql_from_response(llm_response:str)->str:
    """
    Extracts an SQL query from the AI model's response.

    This function uses a regular expression to search for the SQL query within the model's response 
    and returns the SQL query as a string.

    Args:
        llm_response (str): The response returned by the AI model that potentially contains 
                             the SQL query.

    Returns:
        str: The extracted SQL query from the model's response.
    """

    pattern = "SELECT(.|\n)*;"
    match  =re.search(pattern, llm_response)
    sql_query = llm_response[match.start():match.end()]
    return sql_query


def get_athena_client(ATHENA_ROLE_ARN:str, ATHENA_ROLE_SESSION_NAME:str, ATHENA_DEFAULT_REGION:str):
    """
    Assumes an IAM role and creates an AWS Athena client using temporary credentials.

    This function uses AWS Security Token Service (STS) to assume a specified IAM role and 
    retrieve temporary security credentials. It then uses those credentials to create an Athena 
    client to interact with AWS Athena in the specified region.

    Args:
        ATHENA_ROLE_ARN (str): The Amazon Resource Name (ARN) of the IAM role to assume.
        ATHENA_ROLE_SESSION_NAME (str): A unique session name for the assumed role session.
        ATHENA_DEFAULT_REGION (str): The AWS region where Athena will be accessed.

    Returns:
        botocore.client.Athena: An Athena client object authenticated with temporary credentials 
                                 from the assumed IAM role.
    """
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
                                    RoleArn=ATHENA_ROLE_ARN,
                                    RoleSessionName=ATHENA_ROLE_SESSION_NAME)
    
    credentials = assumed_role_object['Credentials']

    session = boto3.Session(
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken'])

    athena_client=session.client('athena', ATHENA_DEFAULT_REGION)

    return athena_client


def get_athena_response(sql_query:str, athena_client, 
                        ATHENA_DATABASE_NAME, 
                        ATHENA_OUTPUT_LOCATION)->str:
    """
    Executes an SQL query on AWS Athena and returns the query results.

    This function starts a query execution on AWS Athena using the provided SQL query and 
    waits for the query to complete. Once the query is finished, it retrieves the results 
    and formats them into a string representation. If the query succeeds, the results are 
    returned as a formatted string or message indicating no data was found. In case of failure, 
    an error message is returned.

    Args:
        sql_query (str): The SQL query string to execute on AWS Athena.
        athena_client: The AWS Athena client object used to interact with Athena.
        ATHENA_DATABASE_NAME (str): The name of the Athena database where the query will run.
        ATHENA_OUTPUT_LOCATION (str): The S3 location where query results are stored.

    Returns:
        str: A string representation of the query results or an error message.
             - The results are returned as a formatted string (in tabular form).
             - If no data is found, it returns "No data found".
             - If there is an error, it returns an error message such as "StartQueryExecution error" or "failed".
    """
    
    try:
        response = athena_client.start_query_execution(QueryString=sql_query,
                            QueryExecutionContext={'Database': ATHENA_DATABASE_NAME},
                            ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_LOCATION})
        
        query_execution_id = response['QueryExecutionId']
   

        # Wait for query execution to complete
        
        while True:
            query_execution = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            query_status = query_execution['QueryExecution']['Status']['State']
            
            if query_status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            time.sleep(5)

        if query_status == 'SUCCEEDED':

            results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
            
            column_names = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            
            row_values = []
            for row in results['ResultSet']['Rows'][1:]:
                row_data = row.get('Data', [])
                row_values.append([cell.get('VarCharValue', '') for cell in row_data])
            
            df = pd.DataFrame(row_values, columns=column_names)

            if df.empty:
                database_response = "No data found"
            else:
                database_response = df.to_string(index=False)

            return database_response
            
        else:
            return "failed"
    
    except:
        database_response = "StartQueryExecutin error"
        return database_response
    


def get_summary(database_response:str, conversation)->str:
    """
    Generates a summary of a database query result using a conversational AI model.

    This function takes the database query results in string format and prompts the 
    conversation model to generate a summary with insightful information based on the data. 
    The model will provide a concise summary, including key observations and insights from 
    the data, which can be used for reporting or further analysis.

    Args:
        database_response (str): A string representation of the query results, typically 
                                  in a tabular format or plain text.
        conversation: The conversational AI model used to generate insights from the data. 
                      This is assumed to be an instance of a model capable of understanding 
                      the content and providing relevant summaries.

    Returns:
        str: The summary generated by the conversation model, which contains key insights and 
             observations from the provided data.
    """
    final_prompt = f"""You are a Data Analyst, who look over data and summarize it with informative insights. Please summarize this DataFrame {database_response}"""
    summary = conversation.predict(input=final_prompt)
    return summary