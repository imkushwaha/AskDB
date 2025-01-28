"""
Module: sql_query_generation_execution

Author: Upendra Kumar  
Date: 2025-01-27  
Version: 1.0.0 

Description:  
This module handles the generation of SQL queries based on user queries and relevant document metadata. 
It also includes functionality for executing SQL queries on AWS Athena and retrieving results.

Functions:  
1. `get_sql_query`: Generates an SQL query based on relevant columns and user requirements.  
2. `extract_sql_from_response`: Extracts the SQL query from the AI-generated response.  
3. `get_athena_client`: Creates an AWS Athena client using temporary credentials.  
4. `get_athena_response`: Executes SQL queries on AWS Athena and retrieves query results.

Dependencies:  
- `boto3`: AWS SDK for Python to interact with Athena.  
- `re`: For regular expression matching.  
- `time`: For handling query execution wait times.  
- `pandas`: To process query results as a DataFrame.

Usage:  
Use this module to generate SQL queries dynamically and execute them on AWS Athena, retrieving results 
for further analysis.
"""
