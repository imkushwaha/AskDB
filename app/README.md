# AskDB: Turning Questions into SQL and Insights


## Project Overview

AskDB is a cutting-edge GenAI-enabled chatbot that empowers business users to interact with their databases using natural language, without requiring any knowledge of SQL. It transforms user queries into precise SQL statements, executes them on the Athena database, retrieves data, and generates concise summaries in plain English. This enables users to gain actionable insights effortlessly, making data analytics accessible to everyone.

## Problem Statement

Accessing data from databases often requires technical expertise, particularly in writing SQL queries. Business users, who are typically unfamiliar with SQL, rely heavily on technical teams for data access and analysis, causing delays and inefficiencies.
The lack of user-friendly tools for non-technical users creates a barrier to unlocking the full potential of organizational data.

Current Challenges:

- `Business users struggle to interact directly with databases.`
- `Dependency on technical teams for SQL query writing.`
- `Time-consuming process to retrieve and analyze data.`
- `Lack of tools that provide insights in plain English for easy interpretation.`


## Key Objectives

- `Enable natural language interaction with databases.`
- `Automate SQL generation for user queries.`
- `Integrate with Athena DB to execute SQL statements.`
- `Provide concise summaries of data in natural language.`
- `Ensure the system is intuitive, scalable, and reliable for business users.`

## Features

- `Natural Language Querying`: Converts user queries into SQL seamlessly.
- `SQL Execution`: Executes dynamically generated SQL on Athena DB.
- `Data Summarization`: Provides easy-to-understand summaries of the retrieved data.
- `User-Friendly Interface`: Simplified design for non-technical users.
- `Customizable Mapping`: Tailors database and table selection based on user input.
- `Scalable Architecture`: Designed to handle large-scale queries efficiently.


## Technology Stack

AskDB is built using the following technologies:

-  `Python`: Core programming language.

- `Frontend`: Streamlit

- `Closed and Open Source LLMs`: For processing natural language queries.

- `Langchain`: A python framework for working with LLM

- `ChromaDB`: Vector database for managing embeddings and performing similarity searches.

- `FAISS`: For in-memory Vector Index

- `AWS SageMaker JumpStart`: For deploying Opne-source LLM

- `AWS Bedrock APIs`: For leveraging advanced language models.

- `pandas`: For data manipulation and processing.

- `AWS Cloud Services`: AWS(Bedrock, SageMaker, Athena, S3, Glue)

- `Other Python Libraries`: Supporting tools and utilities for implementation.

## System Architecture

- `User Interaction Layer`: Accepts natural language queries via a chatbot interface.
- `Query Processing Engine`:

    - Identifies the appropriate database and tables.
    - Translates natural language into SQL statements using GenAI models.
    
- `SQL Execution Layer`: Executes the SQL statement on Athena DB.
- `Data Summarization Layer`: Summarizes the retrieved data into natural language.
- `Response Layer`: Sends the summary back to the user in an easy-to-read format.



## User Interaction

Users can interact with AskDB through a web-based UI. Simply enter a query related on connected database, and the system will provide a summary as a response.

## Limitations

- The system may require training to handle complex or ambiguous queries accurately.
- Limited to the databases and schemas configured in Athena.
- Depends on the accuracy of the natural language model used for query translation.
- Processing time may increase for large-scale datasets or complex queries.

## Feature Scope

- Multi-database support beyond Athena (e.g., MySQL, PostgreSQL).
- Real-time data visualization alongside summaries.
- Voice-based query input.
- Enhanced support for ambiguous or incomplete queries using advanced NLP techniques.
- Multi-language support for non-English queries.



## Acknowledgements
- This Project is a part of my assignment for Post Graduate Diploma Degree in AI & ML at IIIT-Bangalore

## ✍️ Author
Developed by [Upendra Kumar]. For queries, reach out at [upendra.kumar48762@gmail.com].
