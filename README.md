# California Procurement AI Assistant

AI-powered assistant for analyzing California State procurement data using natural language queries.

## Features

- Natural language query processing
- MongoDB aggregation pipelines
- Real-time data analysis
- 346,018 procurement records (2012-2015)
- Support for complex queries and aggregations
- Trend analysis and comparisons
- Department and supplier analytics

## Technologies

- **Database**: MongoDB
- **AI Model**: Ollama with Mistral
- **Web Framework**: Streamlit
- **Language**: Python 3.9+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/faisalstd/california-procurement-assistant.git
cd california-procurement-assistant

Install dependencies:

bashpip install -r requirements.txt

Download the dataset from Kaggle
Setup MongoDB and load data:

bashpython data_loader.py

Run Ollama with Mistral:

bashollama run mistral

Launch the application:

bashstreamlit run app.py
Query Examples

"What is the total spending in 2014?"
"Show me the highest spending quarter"
"Most frequently ordered items"
"Compare spending between 2013 and 2014"
"Top 10 most expensive purchases"
"Which department spent the most?"

Demo
Run the demo script to test all features:
bashpython demo_questions.py
Author
Faisal - GitHub
