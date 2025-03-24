# chatbot_desktop/core/agent_manager.py

from storage.blackboard import Blackboard
from core.agents.doc_agent import DocAgent
from core.agents.data_agent import DataAgent
from core.agents.general_agent import GeneralAgent
from core.agents.web_agent import WebAgent


class AgentManager:
    def __init__(self):
        self.blackboard = Blackboard()
        self.doc_agent = DocAgent(self.blackboard)
        self.data_agent = DataAgent(self.blackboard)
        self.web_agent = WebAgent(self.blackboard)
        self.general_agent = GeneralAgent(self.blackboard)

        # Active agent can be doc_agent, data_agent, or None
        self.active_agent = None

    def load_document(self, doc_id, text):
        """
        Stores the doc text in blackboard, sets DocAgent as active.
        """
        self.blackboard.documents[doc_id] = text
        # If you want to ingest into Chroma here, you can do:
        # self.doc_agent.ingest_document(doc_id, text)
        self.active_agent = self.doc_agent

    def load_dataframe(self, df_id, df):
        """
        Stores the DataFrame in blackboard, sets DataAgent as active.
        """
        self.blackboard.dataframes[df_id] = df
        self.data_agent.set_active_df(df_id)
        self.active_agent = self.data_agent

    def route_query(self, user_msg):
        """
        Routes user_msg to whichever agent is active, or fallback.
        """
        self.blackboard.conversation_history.append(
            {"role": "user", "content": user_msg}
        )

        lower_msg = user_msg.lower()
        if "fetch http" in lower_msg or "scrape http" in lower_msg:
            response = self.web_agent.handle_query(user_msg)

        elif self.active_agent:
            # If an agent is active, route to it
            response = self.active_agent.handle_query(user_msg)
        else:
            # Fallback to general agent
            response = self.general_agent.handle_query(user_msg)

        self.blackboard.conversation_history.append(
            {"role": "assistant", "content": response}
        )
        return response

    def reset_all(self):
        self.blackboard.conversation_history.clear()
        self.blackboard.documents.clear()
        self.blackboard.dataframes.clear()
        self.blackboard.web_contents.clear()
        self.blackboard.intermediate.clear()
        self.active_agent = None

    def set_active_agent(self, agent_name: str):
        """
        Optional: Manually switch active agent if you like.
        """
        if agent_name.lower() == "doc":
            self.active_agent = self.doc_agent
        elif agent_name.lower() == "data":
            self.active_agent = self.data_agent
        elif agent_name.lower() == "web":
            self.active_agent = self.web_agent
        else:
            self.active_agent = self.general_agent
