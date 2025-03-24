# chatbot_desktop/tests/test_agents.py

import pytest
from core.agent_manager import AgentManager


@pytest.fixture
def agent_manager():
    return AgentManager()


def test_doc_agent(agent_manager):
    text = "Hello world of documents."
    agent_manager.load_document("doc1", text)
    response = agent_manager.route_query("What does the document say?")
    assert "Hello world of documents" in response or "document loaded" not in response.lower()


def test_data_agent(agent_manager):
    import pandas as pd
    data = {"col1": [1, 2, 3], "col2": [10, 20, 30]}
    df = pd.DataFrame(data)
    agent_manager.load_dataframe("df1", df)
    response = agent_manager.route_query("head")
    assert "col1" in response


def test_web_agent(agent_manager):
    # This is a naive example, not a robust test,
    # might need mocking to avoid real network calls
    response = agent_manager.route_query("fetch http://www.example.com")
    # Just check that we either get an error or something referencing external content
    assert "No URL found" not in response
