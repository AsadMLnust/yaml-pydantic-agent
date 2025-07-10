# AI-Powered Data Analysis System

> Transform your financial data into actionable insights with the power of AI agents! 🚀

A sophisticated Flask web application that leverages CrewAI's multi-agent system to analyze financial statements and generate executive reports. Simply ask questions in natural language, and watch as our AI team of specialists work together to deliver comprehensive financial insights.

## ✨ What Makes This Special?

🤖 **Three AI Specialists Agent Working in Harmony:**
- **SQL Developer** - Master of database queries and data extraction
- **Data Analyst** - Expert in financial data interpretation
- **Report Writer** - Specialist in creating clear, executive-level summaries

🧠 **Powered by Advanced AI:**
- Groq's Llama 3.3 70B model for intelligent processing
- LangChain tools for seamless database operations
- CrewAI framework for coordinated agent collaboration

🎯 **User-Friendly Design:**
- Clean web interface - just type your question!
- Natural language queries (no SQL knowledge required)
- Instant markdown reports perfect for presentations

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:
- Python 3.8+ installed
- A Groq API key (get one [here](https://console.groq.com/keys))
- Your financial data in CSV format

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/AsadMLnust/yaml-pydantic-agent.git
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up your environment:**
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

4. **Prepare your data:**
- Place your financial statements CSV file in the project root
- Name it `Financial Statements.csv`
- The system will automatically process and create a SQLite database

5. **Launch the application:**
```bash
python app.py
```

6. **Start analyzing!**
Open your browser and go to `http://localhost:5000`

## 🎮 How to Use

1. **Ask Natural Questions:**
   - "What was the total revenue last quarter?"
   - "Show me the profit margins by month"
   - "Which expenses increased the most this year?"

2. **Get Instant Insights:**
   - Our SQL Developer extracts the relevant data
   - The Data Analyst provides detailed analysis
   - The Report Writer creates an executive summary

3. **Receive Professional Reports:**
   - Clean markdown formatting
   - Executive-level summaries
   - Ready for presentations or decision-making

## 🛠️ Project Structure

```
financial-analysis-system/
├── app.py                 # Main Flask application
├── config.yaml           # Agent configuration
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (you create this)
├── Financial Statements.csv  # Your financial data (you provide this)
├── templates/
│   ├── index.html        # Main query interface
│   └── result.html       # Results display
└── README.md            # This file
```

## ⚙️ Configuration & Validation

### Pydantic Schema Validation

The system uses **Pydantic** for robust configuration management:

```python
from pydantic import BaseModel, Field
from typing import List

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
```

### Agent Customization
Edit config.yaml to customize your AI agents (validated by Pydantic):
agents:
  - name: "sql_dev"
    role: "Senior Database Developer"
    goal: "Construct and execute SQL queries for any type of data analysis"
    backstory: >
      You are an experienced database engineer who works with diverse datasets.
      Whether it's sales data, HR records, inventory, or financial statements,
      you can quickly understand any schema and extract the right information.
    tools:
      - "list_tables"
      - "tables_schema"
      - "execute_sql"
      - "check_sql"
    allow_delegation: false

### Adding New Tools

The system is designed to be extensible. Add new tools in `app.py`:

```python
@tool("your_new_tool")
def your_new_tool(input: str) -> str:
    """Your tool description"""
    # Your tool logic here
    return result
```

## 🔧 Technical Details

### Core Technologies
- **Flask** - Web framework for the user interface
- **CrewAI** - Multi-agent orchestration framework
- **LangChain** - Tools for database operations
- **Groq** - Lightning-fast LLM inference
- **SQLite** - Lightweight database for financial data
- **Pandas** - Data manipulation and CSV processing

### Agent Workflow
1. **SQL Developer** uses database tools to understand schema and extract data
2. **Data Analyst** receives the data and provides detailed analysis
3. **Report Writer** creates executive summaries from the analysis

### Database Schema
The system automatically processes your CSV and creates a SQLite database with:
- Cleaned column names (spaces replaced with underscores)
- Proper data types and indexing
- Ready for complex financial queries

## 🎯 Example Queries

Try these sample questions to see the system in action:

**Revenue Analysis:**
- "What's our total revenue for the last quarter?"
- "Show me revenue trends by month"

**Expense Management:**
- "Which expense category had the highest increase?"
- "Compare operating expenses year-over-year"

**Profitability:**
- "Calculate our profit margins for each product line"
- "What's driving our profitability changes?"

##  Acknowledgments

- **CrewAI** for the amazing multi-agent framework
- **Groq** for lightning-fast LLM inference
- **LangChain** for powerful database tools
- **Flask** for the elegant web framework

