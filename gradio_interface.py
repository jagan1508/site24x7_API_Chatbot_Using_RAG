import gradio as gr
from prompt_graph import drawing_graph
from inferfromgraph import get_data

def greet(key,query):
    #drawing_graph(key)
    return get_data(key,query)
    

with gr.Blocks() as demo:
    key=gr.Textbox(label="Api_key")
    query=gr.Textbox(label="query")
    output=gr.Textbox(label="output")
    submit=gr.Button("Submit")
    submit.click(fn=greet,inputs=[key,query],outputs=output)
    
demo.launch(share=True) 