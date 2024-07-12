# site24x7_API_Chatbot_Using_RAG
This repository contains scripts to set up and interact with a Neo4j graph database using OpenAI's API and a Gradio web interface.
## Files and their Purpose

1.prompt_graph.py
Purpose: Retrieves data from an API, processes it into a DataFrame, and uses OpenAI's API to generate a knowledge graph schema in JSON format. It then creates a Cypher query to construct the graph in a Neo4j database.

Functionality:

*API Data Retrieval: Fetches alarm data, monitor groups, and categories.
*DataFrame Creation and Processing: Merges the fetched data into a single DataFrame (newdf).
*Prompt Generation: Templates for generating JSON schema and combining outputs.
*OpenAI API Interaction: Generates schema using both GPT-3.5 and GPT-4 models, then combines the results.
*Cypher Query Construction: Constructs a Cypher query to create the knowledge graph in Neo4j and stores the cypher query in a text file "Output.txt".
*Graph Construction: Calls draw_from_query() to execute the Cypher query and build the graph in Neo4j.

2.drawgraph.py
Purpose: Executes a query read from Output.txt on a Neo4j graph database.

Functionality:

*Reads a query from Output.txt.
*Sets environment variables for Neo4j connection.
*Creates a Neo4jGraph object.
*Executes the query on the Neo4j graph database.

3.inferfromgraph.py
Purpose: Processes queries using Neo4j and OpenAI's API to interact with the graph database and return results.

Functionality:

*Imports necessary modules and sets environment variables.
*Initializes OpenAI and Neo4j clients.
*Creates Neo4jVector indices for embedding graph data.
*Defines tools for interacting with the graph data.
*Creates and executes an agent to process the query and return results.

4.gradio_interface.py
Purpose: Provides a web interface using Gradio for interacting with the graph database.

Functionality:

*Defines a greet function to process the API key and query, returning the result.
*Sets up a Gradio interface with input fields for API key, query, and output, along with a submit button.
*Launches the Gradio interface with sharing enabled.





