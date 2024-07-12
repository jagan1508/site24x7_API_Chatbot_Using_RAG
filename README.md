# site24x7_API_Chatbot_Using_RAG
This repository contains scripts to set up and interact with a Neo4j graph database using OpenAI's API and a Gradio web interface.
## files
###1.prompt_graph.py
Purpose: Retrieves data from an API, processes it into a DataFrame, and uses OpenAI's API to generate a knowledge graph schema in JSON format. It then creates a Cypher query to construct the graph in a Neo4j database.

Functionality:

API Data Retrieval: Fetches alarm data, monitor groups, and categories.
DataFrame Creation and Processing: Merges the fetched data into a single DataFrame (newdf).
Prompt Generation: Templates for generating JSON schema and combining outputs.
OpenAI API Interaction: Generates schema using both GPT-3.5 and GPT-4 models, then combines the results.
Cypher Query Construction: Constructs a Cypher query to create the knowledge graph in Neo4j.
Graph Construction: Calls draw_from_query() to execute the Cypher query and build the graph in Neo4j.








