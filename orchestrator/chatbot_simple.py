from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama  # Import Ollama
from langgraph.graph import MessagesState
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver



thread = {"configurable": {"thread_id": "1"}}
DB_URI = "postgresql://postgres:Mobydick&15@127.0.0.1:5432/ai_agent" 


# Change to the model you want to use

llm = ChatOpenAI(model = "gpt-4o")
#llm = ChatOllama(model="deepseek-r1") 

def chatbot(state: MessagesState):

    # System message to instruct the LLM
    system_message = """
    You are a helpful assistant that needs to help the user with their requests
    """

    return {"messages": [llm.invoke([system_message] + state["messages"])]}

def build_interview_graph(checkpointer):
    """
    Builds and returns a compiled StateGraph.
    """
    builder = StateGraph(MessagesState)

    builder.add_node("chatbot", chatbot)

    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    # 'memory' can be a checkpointer or your custom memory
    # 'memory' must be defined or imported from your library

    interview_graph = builder.compile(checkpointer=checkpointer)
    return interview_graph

def handle_interview(question: str):
    """
    Orchestrates the interview-style chat by building the graph with Postgres memory,
    then streaming or running it with an initial input.
    Returns a list of final messages from the graph for the user.
    """
    # Create initial input from the human question.
    initial_input = {"messages": HumanMessage(content=question)}
    
    # Use the PostgresSaver as a context manager.
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        # Compile the graph with the checkpointer to enable memory.
        interview_graph = build_interview_graph(checkpointer=checkpointer)
        
        # Optionally, if you have a thread variable, include it in the stream call.
        final_message = None
        for event in interview_graph.stream(initial_input, thread, stream_mode="values"):
            for message in event["messages"]:
                final_message = message.content  # keep only the latest message
    
    # Return the final message wrapped in a list. TO DO -> change the router and this to return a string only
    return [final_message]