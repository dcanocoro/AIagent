

# chatbot_simple.py

import os
from dotenv import load_dotenv
from typing import List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

# ----------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------
load_dotenv()

# ----------------------------------------------------------------
# Import LLM / LangChain / LangGraph
# ----------------------------------------------------------------
from langchain_openai import ChatOpenAI
# from langchain_community.chat_models import ChatOllama  # If you want Ollama, uncomment
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import get_buffer_string

# Replace this with your actual DB credentials
DB_URI = "postgresql://postgres:Mobydick&15@127.0.0.1:5432/ai_agent"

# ----------------------------------------------------------------
# MODEL
# ----------------------------------------------------------------
# Example: Using GPT-4 on your local proxy or ChatOllama
# llm = ChatOllama(model="deepseek-r1")
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ----------------------------------------------------------------
# SCHEMA FOR ANALYST GENERATION
# ----------------------------------------------------------------
class Analyst(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )
    @property
    def persona(self) -> str:
        return (
            f"Name: {self.name}\n"
            f"Role: {self.role}\n"
            f"Affiliation: {self.affiliation}\n"
            f"Description: {self.description}\n"
        )

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations."
    )

class GenerateAnalystsState(TypedDict):
    topic: str                # Research topic
    max_analysts: int         # Number of analysts
    human_analyst_feedback: str
    analysts: List[Analyst]

# ----------------------------------------------------------------
# SIMPLE ANALYST-GENERATION GRAPH (Optional if you use it)
# ----------------------------------------------------------------
analyst_instructions = """You are tasked with creating a set of AI analyst personas. 
Follow these instructions carefully:

1. First, review the research topic:
{topic}

2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts:
{human_analyst_feedback}

3. Determine the most interesting themes based on the above.

4. Pick the top {max_analysts} themes.

5. Assign one analyst to each theme.
"""

def create_analysts(state: GenerateAnalystsState):
    topic = state["topic"]
    max_analysts = state["max_analysts"]
    feedback = state.get("human_analyst_feedback", "")

    structured_llm = llm.with_structured_output(Perspectives)
    system_prompt = analyst_instructions.format(
        topic=topic,
        human_analyst_feedback=feedback,
        max_analysts=max_analysts
    )

    perspectives = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Generate the set of analysts.")
    ])
    return {"analysts": perspectives.analysts}

def human_feedback(state: GenerateAnalystsState):
    """No-op node that can be interrupted for user feedback."""
    pass

def should_continue(state: GenerateAnalystsState):
    """If feedback is present, re-run. Otherwise end."""
    if state.get("human_analyst_feedback"):
        return "create_analysts"
    return END

analyst_graph_builder = StateGraph(GenerateAnalystsState)
analyst_graph_builder.add_node("create_analysts", create_analysts)
analyst_graph_builder.add_node("human_feedback", human_feedback)
analyst_graph_builder.add_edge(START, "create_analysts")
analyst_graph_builder.add_edge("create_analysts", "human_feedback")
analyst_graph_builder.add_conditional_edges(
    "human_feedback", should_continue, ["create_analysts", END]
)
memory_analysts = MemorySaver()
analyst_graph = analyst_graph_builder.compile(
    interrupt_before=["human_feedback"],
    checkpointer=memory_analysts
)

# ----------------------------------------------------------------
# INTERVIEW-STYLE GRAPH
# ----------------------------------------------------------------
from typing import Annotated
import operator

class InterviewState(TypedDict):
    """
    For advanced interview flow:
    - 'messages' track the conversation so far
    - 'max_num_turns' how many times the 'expert' can respond
    - 'context' the docs or info retrieved
    - 'analyst' the persona
    - 'interview' final transcript
    - 'sections' final written sections
    """
    messages: list
    max_num_turns: int
    context: list
    analyst: Analyst
    interview: str
    sections: list

# Example search-structure if you have a web or wiki search:
class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")

# Example instructions for the interview steps
question_instructions = """You are an analyst tasked with interviewing an expert 
to learn about a specific topic.

Your goal is to discover interesting and specific insights related to your topic.

1. Interesting: Insights that people will find surprising or non-obvious.
2. Specific: Insights that avoid generalities and include specific examples.

Here is your topic of focus and set of goals: {goals}

- Begin by introducing yourself using a name that fits your persona, then ask your question.
- Continue to ask questions to drill down and refine your understanding of the topic.
- End the interview with: "Thank you so much for your help!".
- Stay in character throughout your responses, reflecting the persona and goals you have.
"""

def generate_question(state: InterviewState):
    """Ask the next interview question from the analyst's perspective."""
    analyst = state["analyst"]
    messages = state["messages"]

    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)] + messages)
    return {"messages": [question]}

# OPTIONAL: Some example "search_web"/"search_wikipedia" if you have them
# For demonstration, we define placeholders that simply echo "No real search."
def search_web(state: InterviewState):
    """Fake web search, returning dummy context."""
    # A real web search would run here
    return {"context": ["[Simulated Web Search Result: No real data found.]"]}

def search_wikipedia(state: InterviewState):
    """Fake wiki search, returning dummy context."""
    # A real Wikipedia search would run here
    return {"context": ["[Simulated Wikipedia Result: No real data found.]"]}

answer_instructions = """You are an expert being interviewed by an analyst.

Analyst Focus:
{goals}

Use the provided context to answer the question as accurately as possible.

Context:
{context}

Guidelines:
1. Use only the information in the context.
2. Do not add external info or guess.
3. Include references [1], [2], etc. for relevant statements from the context.
4. End references with a sources list at the bottom, e.g.:
   [1] my-source-1
   [2] my-source-2
"""

def generate_answer(state: InterviewState):
    """Generate an expert answer based on context and the last question."""
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    system_msg = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=system_msg)] + messages)
    # Mark the AI's role
    answer.name = "expert"
    return {"messages": [answer]}

def save_interview(state: InterviewState):
    """Convert the messages to a single transcript string."""
    messages = state["messages"]
    transcript = get_buffer_string(messages)
    return {"interview": transcript}

def route_messages(state: InterviewState, name: str = "expert"):
    """Conditionally continue or end after max_num_turns or user says thanks."""
    messages = state["messages"]
    max_num_turns = state.get("max_num_turns", 2)

    # Count how many times 'expert' has responded
    num_expert_responses = len([
        m for m in messages if isinstance(m, AIMessage) and m.name == name
    ])

    if num_expert_responses >= max_num_turns:
        return "save_interview"

    # Check last question for exit
    if len(messages) > 1:
        last_question = messages[-2]  # The prompt before the expert's last answer
        if "Thank you so much for your help" in last_question.content:
            return "save_interview"

    return "ask_question"

section_writer_instructions = """You are an expert technical writer. 
Write a short, easily digestible section of a report based on the interview results.

Focus area for the analyst: {focus}

Guidelines:
1. Use ## for the main title, ### for subsections: "Summary", "Sources".
2. Summarize the interesting or novel insights from the interview (about 400 words).
3. Cite sources as [1], [2], etc.
4. Under the "Sources" section, list them using the same numbering as in the text.

Do not mention the names of the interviewer or the expert.
"""

def write_section(state: InterviewState):
    """Summarize the interview into a final 'report section'."""
    interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]

    prompt = section_writer_instructions.format(focus=analyst.description)
    # We combine the context plus interview for additional detail, if needed:
    user_message = (
        f"Below is the final interview transcript:\n{interview}\n\n"
        f"Here is your context:\n{context}\n\n"
        "Please produce the requested report."
    )
    section = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=user_message)])
    return {"sections": [section.content]}

# ----------------------------------------------------------------
# BUILD THE INTERVIEW GRAPH
# ----------------------------------------------------------------
interview_builder = StateGraph(InterviewState)

interview_builder.add_node("ask_question", generate_question)
interview_builder.add_node("search_web", search_web)
interview_builder.add_node("search_wikipedia", search_wikipedia)
interview_builder.add_node("answer_question", generate_answer)
interview_builder.add_node("save_interview", save_interview)
interview_builder.add_node("write_section", write_section)

# Flow
interview_builder.add_edge(START, "ask_question")
interview_builder.add_edge("ask_question", "search_web")
interview_builder.add_edge("ask_question", "search_wikipedia")
interview_builder.add_edge("search_web", "answer_question")
interview_builder.add_edge("search_wikipedia", "answer_question")
interview_builder.add_conditional_edges(
    "answer_question", route_messages, ["ask_question", "save_interview"]
)
interview_builder.add_edge("save_interview", "write_section")
interview_builder.add_edge("write_section", END)

# Compile the final "interview graph"
memory_interview = MemorySaver()
interview_graph = interview_builder.compile(checkpointer=memory_interview)

# ----------------------------------------------------------------
# MAIN FUNCTION: handle_interview
# ----------------------------------------------------------------
def handle_interview(question: str, thread):
    """
    This function replaces the old chatbot logic with the enhanced
    "research assistant" interview flow. It returns a list[str]
    so the FastAPI route's response_model = list[str] remains valid.
    """

    # Create a default analyst persona
    default_analyst = Analyst(
        affiliation="OpenAI Lab",
        name="Dr. ChatGPT",
        role="Research Interviewer",
        description=f"Wants to explore the topic: {question}"
    )

    # Initial messages
    initial_messages = [
        HumanMessage(content=f"So you said you were writing an article on {question}?")
    ]

    # State input for the graph
    state_input = {
        "analyst": default_analyst,
        "messages": initial_messages,
        "max_num_turns": 2,   # allow up to 2 answers from the 'expert'
        "context": [],
        "interview": "",
        "sections": []
    }

    # Use Postgres memory for conversation threads
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        graph_instance = interview_graph.with_config(checkpointer=checkpointer)
        
        # Fix: Use `config=thread` instead of `thread=thread`
        result = graph_instance.invoke(state_input, config=thread)

    # Extract final sections
    final_sections = result.get("sections", [])

    # Return as list[str] (to match FastAPI response model)
    return final_sections

