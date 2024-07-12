def draw_from_query():
    import os
    from langchain_community.graphs import Neo4jGraph
    f = open("Output.txt", "r")
    query=f.read()
    os.environ['NEO4J_URI']="bolt://localhost:7687"
    os.environ['NEO4J_USERNAME']="neo4j"
    os.environ['NEO4J_PASSWORD']="test1234"
    os.environ['NEO4J_DATABASE']="site24x7"

    kg=Neo4jGraph(
        url="bolt://localhost:7687", username="neo4j", password="test1234", database="site24x7")
    query=query.strip(' ')
    query=query.strip(query[0])

    kg.query(query)