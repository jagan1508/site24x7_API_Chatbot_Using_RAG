# site24x7_API_Chatbot_Using_RAG
This repository contains scripts to set up and interact with a Neo4j graph database using OpenAI's API and a Gradio web interface.
## Files and their Purpose

<b>1.<mark>'prompt_graph.py'</b></mark><br>
<br><b>Purpose:</b> Retrieves data from an API, processes it into a DataFrame, and uses OpenAI's API to generate a knowledge graph schema in JSON format. It then creates a Cypher query to construct the graph in a Neo4j database.

<br><b>Functionality:</b>
<br>*API Data Retrieval: Fetches alarm data, monitor groups, and categories.
<br>*DataFrame Creation and Processing: Merges the fetched data into a single DataFrame (newdf).
<br>*Prompt Generation: Templates for generating JSON schema and combining outputs.
<br>*OpenAI API Interaction: Generates schema using both GPT-3.5 and GPT-4 models, then combines the results.
<br>*Cypher Query Construction: Constructs a Cypher query to create the knowledge graph in Neo4j and stores the cypher query in a text file "Output.txt".
<br>*Graph Construction: Calls draw_from_query() to execute the Cypher query and build the graph in Neo4j.

<br><b>2.<mark>'drawgraph.py'</mark></b>
<br><b>Purpose:</b> Executes a query read from Output.txt on a Neo4j graph database.

<br><b>Functionality:</b>
<br>*Reads a query from Output.txt.
<br>*Sets environment variables for Neo4j connection.
<br>*Creates a Neo4jGraph object.
<br>*Executes the query on the Neo4j graph database.

<br><b>3.<mark>'inferfromgraph.py'</mark></b>
<br><b>Purpose:</b> Processes queries using Neo4j and OpenAI's API to interact with the graph database and return results.

<br><b>Functionality:</b>
<br>*Imports necessary modules and sets environment variables.
<br>*Initializes OpenAI and Neo4j clients.
<br>*Creates Neo4jVector indices for embedding graph data.
<br>*Defines tools for interacting with the graph data.
<br>*Creates and executes an agent to process the query and return results.

<br><b>4.<mark>'gradio_interface.py'</mark></b>
<br><b>Purpose:</b> Provides a web interface using Gradio for interacting with the graph database.

<br><b>Functionality:</b>
<br>*Defines a greet function to process the API key and query, returning the result.
<br>*Sets up a Gradio interface with input fields for API key, query, and output, along with a submit button.
<br>*Launches the Gradio interface with sharing enabled.





