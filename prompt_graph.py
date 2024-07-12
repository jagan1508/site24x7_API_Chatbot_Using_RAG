

def drawing_graph(api_key):
  import requests
  from bs4 import BeautifulSoup
  import json
  import pandas as pd
  import collections
  import openai
  from langchain_openai import ChatOpenAI
  from langchain.prompts.prompt import PromptTemplate
  from langchain.prompts import ChatPromptTemplate
  import os
  from langchain_community.graphs import Neo4jGraph
  import re



  def api_data(base_url,api_url):
    session = requests.Session()
    response = session.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    token_script = soup.find('script', text=lambda t: 'Zoho-oauthtoken' in t)
    token = None

    if token_script:
        token = token_script.text.split('Zoho-oauthtoken ')[1].split('"')[0]

    if not token:
        raise Exception("Failed to retrieve OAuth token from the demo page")
    headers = {
            'Authorization': f'Zoho-oauthtoken {token}'
        }
    response = session.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()
  alarms_list=api_data('https://www.site24x7.com/app/demo#/alarms','https://www.site24x7.com/app/api/alarms_list')['data']['monitors']



  def create_dataframe_from_keys(dict_list, keys):
      # Create a list of dictionaries containing only the specified keys
      filtered_dicts = [{key: record.get(key, None) for key in keys} for record in dict_list]
      
      # Create a DataFrame from the filtered dictionaries
      df = pd.DataFrame(filtered_dicts)
      
      return df
  df=create_dataframe_from_keys(alarms_list,keys=['monitor_id','outage_id','duration','last_polled_time','monitor_type','down_reason','categories','monitor_groups','monitor_groups_name'])
 
  monitor_groups=api_data('https://www.site24x7.com/app/demo#/alarms','https://www.site24x7.com/app/api/monitor_groups?subgroup_required=true')['data']
  categories=api_data('https://www.site24x7.com/app/demo#/alarms','https://www.site24x7.com/app/api/short/alarms_category')['data']
  df1=pd.DataFrame(categories)
  '''def find_category_name(id):
      for i in categories:
          if i["category_id"]==id:
              return i["category_name"]
  l=[]
  for idx,row in df.iterrows():
      if row['categories']:
          name=find_category_name(row["categories"][0])
          l.append(name)
      else:
          l.append(None)
  df["category_names"]=l'''

  group_ids=collections.defaultdict(lambda:list())
  def grp(i,group_ids):
      if "monitors" in i.keys() and "description" in i.keys():
          for j in i["monitors"]:
              group_ids[j].append(i["description"])
  def extract_group_ids(monitor_groups,group_ids):
      for i in monitor_groups:
          if "subgroups" not in i.keys():
              grp(i,group_ids)
          else:
              extract_group_ids(i["subgroups"],group_ids)
  extract_group_ids(monitor_groups,group_ids)
  group_ids=dict(group_ids)
  data_tuples = [(monitor_id, group_id) for monitor_id, group_ids in group_ids.items() for group_id in group_ids]
  df2 = pd.DataFrame(data_tuples, columns=['monitor_id', 'group_description'])
  df1.rename(columns={"category_id":"categories"},inplace=True)
  for i in range(len(df['categories'])):
      if df['categories'][i]!=None:
          df.loc[i,"categories"]=df["categories"][i][0]

  new_df=pd.merge(df,df1,on=["categories"],how="left")
  newdf=pd.merge(new_df,df2,on=["monitor_id"],how="left")


  PROMPT="""Using the given data which is of the form of PANDAS DATAFRAME having different columns . The below is the given PANDAS DATAFRAME:
  <<input>>
  DATAFRAME-{newdf}
  COLUMNS-{columns}
  <</input>>
  Given a Pandas DataFrame with columns representing different attributes, perform the following actions:
  -Identify as many entities and their attributes from the DataFrame as possible.
  -Identify and define relationships between these entities.
  -Output the results in JSON format.

  Requirements:
  -Ensure each entity is identified by a unique attribute (e.g., monitor_id for Monitor, group_id for Group).
  -Include all relevant attributes for each entity as specified in the DataFrame.
  -Use all available information from the DataFrame to define entities and relationships.
  -Include all the columns given in the DATAFRAME . DO NOT MISS ANY COLUMNS RELATE IT SOMEHOW BASED ON SIMILARITY TO THE ENTITY. 
  -Ensure it follows database properties.
  -Ensure the output is in proper JSON format

  OUTPUT FORMAT:
  {{
    "entities": {{
      "Entity1": {{
        "attributes": ["attribute1", "attribute2","attribute3",.....]
      }},
      ...
    }},
    "relationships": [
      {{
        "startNode": "Entity1",
        "endNode": "Entity2",
        "relationship": "relationship_type"
      }},
      ...
    ]
  }}

  EXAMPLE:
  {{
    "entities": {{
      "Monitor": {{
        "attributes": ["monitor_id", "monitor_type",......]
      }},
      "Entity2": {{
        "attributes": ["attribute1", "attribute2", ...]
      }},
      ...
    }},
    "relationships": [
      {{
        "startNode": "Monitor",
        "endNode": "Outages",
        "relationship": "has_outages"
      }},
      ...
    ]
  }}

  NOTES:
  -Make sure to capture the attributes and relationships accurately based on the DataFrame provided.
  -Ensure that the JSON output is properly structured and valid.
  """
  COMBINATION_PROMPT="""
  The below are the outputs from different queries for the same prompt using gpt 3.5-turbo model and gpt-4o model. 
  Use the information from both of them to produce an OUTPUT with better entity attributes and relationships.
  INPUTS:
  query1:{query}
  query2:{query2}

  The OUTPUT should be in JSON Format and REPETITION OF ENTITIES AND RELATIONSHIPS IS NOT ALLOWED.
  """
  GENERATION_PROMPT = PROMPT.format(newdf=newdf,columns=newdf.columns)
  def call_openai_api_2(prompt,model):
      openai.api_key = api_key
      response = openai.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
              {"role": "system", "content": "You are a helpful agent, just give output on the given format."},
              {"role": "user", "content": prompt}
          ]
      )
      return response.choices[0].message.content 
  query=call_openai_api_2(GENERATION_PROMPT,"gpt-3.5-turbo-0125")
  query2=call_openai_api_2(GENERATION_PROMPT,"gpt-4o")
  cp=COMBINATION_PROMPT.format(query=query,query2=query2)
  query3=call_openai_api_2(cp,"gpt-3.5-turbo-0125")
  with open("graph_schema.json", "w") as text_file:
    text_file.write(query3)
  #Generating knowledge graph for it
  os.environ['NEO4J_URI']="bolt://localhost:7687"
  os.environ['NEO4J_USERNAME']="neo4j"
  os.environ['NEO4J_PASSWORD']="test1234"
  os.environ['NEO4J_DATABASE']="site24x7"

  kg=Neo4jGraph(
      url="bolt://localhost:7687", username="neo4j", password="test1234", database="site24x7")
  from langchain.schema.output_parser import StrOutputParser

  def construct_graph(query):
      CONSTRUCT=f"""
        Construct a CYPHER QUERY to build a knowledge graph based on the provided entity-attribute relationships specified in the query below. 

        Entity-attribute relationships should be taken from the csv file where the path to that file is given, and the resulting output must be a valid CYPHER STATEMENT. 

        Ensure that the query correctly represents the relationships and attributes between entities as described in the dataframe.

        Query:
        {{query}}

        CSV FILE PATH:
        {{path}}

        Output the final CYPHER STATEMENT that can be used to build the knowledge graph .
        The output format should be formatted 
        NOTE:
        -Do not add any explanation or description ;just OUTPUT THE query
        """
      CONSTRUCT_PROMPT=CONSTRUCT.format(query=query,path="data.csv")
      q=call_openai_api_2(CONSTRUCT_PROMPT,"gpt-3.5-turbo-0125")
      print(q)
      with open("Output.txt", "w") as text_file:
        text_file.write(q)
  
  newdf.fillna(value='no-value',inplace=True)
  for i in newdf.columns:
    if i!='monitor_groups':
      newdf[i]=newdf[i].str.lower()
      
  newdf.to_csv("data.csv",index=False)

  construct_graph(query3)
  from drawgraph import draw_from_query
  draw_from_query()

