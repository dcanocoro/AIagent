from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

llm = ChatOpenAI(model = "gpt-4o")

def chatbot(state: MessagesState):

    # System message to instruct the LLM
    system_message = """
    You are a helpful assistant that needs to uder with their requests
    """

    return {"messages": [llm.invoke([system_message] + state["messages"])]}

def build_interview_graph():
    """
    Builds and returns a compiled StateGraph.
    """
    builder = StateGraph(MessagesState)

    builder.add_node("chatbot", chatbot)

    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    # 'memory' can be a checkpointer or your custom memory
    # 'memory' must be defined or imported from your library
    interview_graph = builder.compile()
    return interview_graph

def handle_interview(question: str):
    """
    Orchestrates the interview-style chat by building the graph,
    then streaming or running it with an initial input.
    Returns a list of final messages from the graph for the user.
    """

    interview_graph = build_interview_graph()

    initial_input = {"messages": HumanMessage(content=question)}
    collected_messages = []

    # The library might let you do interview_graph.run(...) or interview_graph.stream(...)
    for event in interview_graph.stream(initial_input, stream_mode="values"):
        for message in event["messages"]:
            collected_messages.append(message.content)

    return collected_messages