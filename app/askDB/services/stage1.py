"""
Module: document_retrieval_preprocessing

Author: Upendra Kumar  
Date: 2025-01-27  
Version: 1.0.0

Description:  
This module focuses on retrieving and preprocessing relevant documents using metadata or table descriptions. 
It provides functions for querying a vector database, extracting relevant information, and preparing data 
for subsequent stages such as SQL query generation.

Functions:  
1. `print_relevant_documents_from_table_desc`: Prints relevant documents based on table descriptions.  
2. `get_relevant_documents_from_table_desc`: Retrieves relevant documents based on table descriptions.  
3. `print_relevant_documents_from_metadata`: Prints relevant documents using metadata similarity search.  
4. `get_relevant_documents_from_metadata`: Retrieves relevant documents using metadata similarity search.  
5. `extract_column_and_desc`: Extracts column names and their descriptions from the retrieved documents.

Dependencies:  
- `vecDB`: A vector database for similarity search.  
- External libraries: None.

Usage:  
Use this module to fetch and preprocess relevant documents from a vector database, enabling further processing 
like SQL query generation.
"""



