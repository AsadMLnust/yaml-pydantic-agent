import os
import time
import sqlite3
import pandas as pd
import yaml
from typing import List, Dict
from pydantic import BaseModel, Field
from textwrap import dedent

from flask import Flask, render_template, request

from langchain_groq import ChatGroq
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)

from crewai.tools import tool
from crewai import Agent, Crew, Task, Process,LLM
from dotenv import load_dotenv

# --- Initialize Flask App ---
app = Flask(__name__)

# --- ONE-TIME SETUP (runs only once when the server starts) ---

# Load Environment Variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set. Please create a .env file and add it.")

# --- Pydantic Schemas for Configuration Validation ---
class AgentConfig(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = Field(default_factory=list)
    allow_delegation: bool = False
    verbose: bool = True

class CrewConfig(BaseModel):
    agents: List[AgentConfig]

# --- Configuration Loading Function ---
def load_config(path: str = "config.yaml") -> CrewConfig:
    """Loads and validates the crew configuration from a YAML file."""
    try:
        with open(path, 'r') as f:
            config_data = yaml.safe_load(f)
        return CrewConfig(**config_data)
    except FileNotFoundError:
        app.logger.error(f"Error: Configuration file '{path}' not found.")
        exit()
    except Exception as e:
        app.logger.error(f"Error loading or validating configuration: {e}")
        exit()

# --- LLM Initialization ---
llm = LLM(model="groq/llama-3.3-70b-versatile",api_key= groq_api_key)


# --- Database Setup ---
try:
    df = pd.read_csv("./Financial Statements.csv")
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('/', '_')
    connection = sqlite3.connect("finance.db")
    df.to_sql(name="finance", con=connection, if_exists='replace', index=False)
    db = SQLDatabase.from_uri("sqlite:///finance.db")
except FileNotFoundError:
    app.logger.error("Error: 'Financial Statements.csv' not found.")
    exit()
except Exception as e:
    app.logger.error(f"Database setup failed: {e}")
    exit()


# --- Create Tools ---
@tool("list_tables")
def list_tables() -> str:
    """List the available tables in the database"""
    return ListSQLDatabaseTool(db=db).invoke("")

@tool("tables_schema")
def tables_schema(tables: str) -> str:
    """Input is a comma-separated list of tables, output is the schema and sample rows for those tables."""
    return InfoSQLDatabaseTool(db=db).invoke(tables)

@tool("execute_sql")
def execute_sql(sql_query: str) -> str:
    """Execute a SQL query against the database. Returns the result"""
    time.sleep(2)
    return QuerySQLDataBaseTool(db=db).invoke(sql_query)

@tool("check_sql")
def check_sql(sql_query: str) -> str:
    """Use this tool to double check if your query is correct before executing it."""
    time.sleep(2)
    return QuerySQLCheckerTool(db=db, llm=llm).invoke({"query": sql_query})

# --- Tool Mapping ---
tool_mapping = {
    "list_tables": list_tables,
    "tables_schema": tables_schema,
    "execute_sql": execute_sql,
    "check_sql": check_sql,
}

# --- Dynamic Agent and Crew Creation ---
def create_crew() -> Crew:
    """Loads config, creates agents and tasks, and assembles the crew."""
    crew_config = load_config()
    
    # Create Agents
    agents = {}
    for agent_conf in crew_config.agents:
        agent_tools = [tool_mapping[tool_name] for tool_name in agent_conf.tools if tool_name in tool_mapping]
        agents[agent_conf.name] = Agent(
            role=agent_conf.role,
            goal=agent_conf.goal,
            backstory=dedent(agent_conf.backstory),
            llm=llm,
            tools=agent_tools,
            allow_delegation=agent_conf.allow_delegation,
            verbose=True
        )

    # Create Tasks
    extract_data = Task(
        description="Extract the data required to answer the question: {query}.",
        expected_output="A list of data from the database that answers the question.",
        agent=agents["sql_dev"],
    )
    analyze_data = Task(
        description="Analyze the data provided and write a brief analysis for the question: {query}.",
        expected_output="A short, easy-to-understand text analyzing the provided data.",
        agent=agents["data_analyst"],
        context=[extract_data],
    )
    write_report = Task(
        description=dedent("Write an executive summary of the report from the analysis. The report must be less than 50 words and presented in markdown."),
        expected_output="A markdown report summarizing the analysis.",
        agent=agents["report_writer"],
        context=[analyze_data],
    )

    # Assemble Crew
    return Crew(
        agents=list(agents.values()),
        tasks=[extract_data, analyze_data, write_report],
        process=Process.sequential,
        verbose=True,
    )

# Create the crew instance once when the app starts
crew = create_crew()

# --- FLASK WEB ROUTES ---

@app.route('/')
def index():
    """Renders the main page with the query form."""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    """Processes the user's query and displays the result."""
    query = request.form.get('query')
    if not query:
        return "Please provide a query.", 400

    inputs = {"query": query}
    
    # Kick off the crew with the user's query
    result = crew.kickoff(inputs=inputs)
    
    return render_template('result.html', query=query, result=result)

if __name__ == '__main__':
    # Running in debug mode is helpful for development
    app.run(debug=True)
