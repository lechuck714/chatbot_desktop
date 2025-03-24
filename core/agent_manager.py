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

        self.active_agent = None

    def load_document(self, doc_id, text):
        self.blackboard.documents[doc_id] = text
        self.doc_agent.set_active_doc(doc_id)
        self.active_agent = self.doc_agent

    def load_dataframe(self, df_id, df):
        self.blackboard.dataframes[df_id] = df
        self.data_agent.set_active_df(df_id)
        self.active_agent = self.data_agent

    def route_query(self, user_msg):
        self.blackboard.conversation_history.append({"role": "user", "content": user_msg})

        lower_msg = user_msg.lower()
        if "fetch http" in lower_msg or "scrape http" in lower_msg:
            response = self.web_agent.handle_query(user_msg)
        elif self.active_agent:
            response = self.active_agent.handle_query(user_msg)
        else:
            response = self.general_agent.handle_query(user_msg)

        self.blackboard.conversation_history.append({"role": "assistant", "content": response})
        return response

    def reset_all(self):
        self.blackboard.conversation_history.clear()
        self.blackboard.documents.clear()
        self.blackboard.dataframes.clear()
        self.blackboard.web_contents.clear()
        self.blackboard.intermediate.clear()
        self.active_agent = None
