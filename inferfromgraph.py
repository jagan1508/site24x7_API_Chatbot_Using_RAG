def get_data(key,query):
    import os
    from openai import OpenAI
    import json
    from langchain_community.graphs import Neo4jGraph
    from langchain_community.vectorstores.neo4j_vector import Neo4jVector
    from langchain_openai.embeddings import OpenAIEmbeddings

    embeddings_model = "text-embedding-3-small"
    os.environ['OPENAI_API_KEY']=key
    os.environ['NEO4J_URI']="bolt://localhost:7687"
    os.environ['NEO4J_USERNAME']="neo4j"
    os.environ['NEO4J_PASSWORD']="test1234"
    os.environ['NEO4J_DATABASE']="site24x7"
    client=OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    kg=Neo4jGraph(
        url="bolt://localhost:7687", username="neo4j", password="test1234", database="site24x7")

    from langchain.chains import GraphCypherQAChain
    from langchain_openai import ChatOpenAI

    from langchain.chains import GraphCypherQAChain

    import os
    from langchain_community.vectorstores.neo4j_vector import Neo4jVector
    from langchain_openai import OpenAIEmbeddings

    os.environ['OPENAI_API_KEY'] = key

    vector_index1 = Neo4jVector.from_existing_graph(
        OpenAIEmbeddings(),
        url="bolt://localhost:7687",
        username="neo4j",
        password="test1234",
        index_name='down_reason_embeddings',
        node_label="Monitor",
        text_node_properties=['monitor_id','down_reason','moitor_type'],
        embedding_node_property='embedding',
    )

    vector_index2 = Neo4jVector.from_existing_graph(
        OpenAIEmbeddings(),
        url="bolt://localhost:7687",
        username="neo4j",
        password="test1234",
        index_name='description_embeddings',
        node_label="MonitorGroup",
        text_node_properties=['group_description','monitor_groups_name'],
        embedding_node_property='embedding',
    )

    from langchain.chains import RetrievalQA
    from langchain_openai import ChatOpenAI

    vector_qa2 = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(), chain_type="stuff", retriever=vector_index2.as_retriever())
    vector_qa1 = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(), chain_type="stuff", retriever=vector_index1.as_retriever())

    from langchain.prompts.prompt import PromptTemplate


    CYPHER_GENERATION_TEMPLATE ="""You are an expert in querying knowledge graphs using Cypher for Neo4j. Given the following natural language question, provide the corresponding Cypher query and the steps to execute it in Neo4j.

    Question: "{question}"
    
    Use the schema to get the snowledge too 
    
    Graph schems:"{schema}"

    Instructions
    1. Analyze the question to identify the entities and relationships. For this you can check with the scheme given in JSON FORMAT : SCHEMA:"{schema}"
    2. Do not use any other relationship types or properties that are not provided.
    3. Make sure if something is asked about an attribute which is embedded , use cosign similarity between our query and the embedding to find the most similar one.
    3. Formulate the Cypher query to retrieve the desired information.
    4. Provide the Cypher query.

    Example:
    Question: "How many monitors have belongs to the category 'website testing'?"
    MATCH (m:Monitor)-[:belongs_to_category]->(:Category{{category_name:"website. testing"}}) RETURN count(m)
    
    Question:"Which monitor group has the most number of monitors?"

    MATCH (g:Group)<-[:belongs_to_group]-(m:Monitor)
    WHERE g.group_description<> "no-value"
    RETURN g.group_description, count(m) as num_monitors
    ORDER BY num_monitors DESC
    LIMIT 1
    
    Question:what are the most common down reason of monitors?

    MATCH (m:Monitor)
    where m.down_reason is not null
    RETURN m.down_reason, count(m) as num_monitors
    ORDER BY num_monitors DESC
    LIMIT 1



    Question: "{question}"
    KINDLY RETURN THE GENERATED CYPHER QUERY ALONE READY TO BE IMPLEMENTED 
    """

    f = open("graph_schema.json", "r")
    schema=f.read()
    CYPHER_GENERATION_PROMPT = PromptTemplate(
        input_variables=["question", "schema"], template=CYPHER_GENERATION_TEMPLATE
    )

    from langchain.chains import GraphCypherQAChain


    kg.refresh_schema()

    cypher_chain = GraphCypherQAChain.from_llm(
        ChatOpenAI(temperature=0), graph=kg, verbose=True,
        cypher_prompt=CYPHER_GENERATION_PROMPT
    )
    from langchain.agents import create_openai_functions_agent, Tool, AgentExecutor
    from langchain import hub


    tools = [
        Tool(
            name="Down_Reason",
            func=cypher_chain.invoke,
            description="""Useful when you need to answer questions about down reason of monitors.
            Not useful for counting the number of monitors or giving its detail.
            Use full question as input.
            """,
        ),
        Tool(
            name="Description",
            func=cypher_chain.invoke,
            description="""Useful when you need to answer questions about description of monitor groups. Use the embedding here to find the similarity and return the most similar.
            Not useful for counting the number of monitors or giving its detail. Embed the query here using OpenAI embeddings and from the embedding done on the value before find the similarity based on cosign similarity . Return the most similar one.
            Use full question as input.
            """,
        ),
        Tool(
            name="Graph",
            func=cypher_chain.invoke,
            description="""Useful when you need to answer questions about monitors,
            its categories, outages and group it belongs to and make sure always "no-value" is excluded. Also useful for any sort of
            aggregation like counting the number of monitors, etc. SO here make sure to exclude entities having name as "no-value".
            Use full question as input.
            """,
        )
    ]  

    # Get the prompt to use - you can modify this!
    prompt = hub.pull("hwchase17/openai-functions-agent")
    agent = create_openai_functions_agent(
        ChatOpenAI(temperature=0, model_name='gpt-4'), tools, prompt
    )
    # Create an agent executor by passing in the agent and tools
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    response = agent_executor.invoke({"input": query})
    print(response)
    return response["output"]