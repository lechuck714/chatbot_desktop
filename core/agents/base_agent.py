# chatbot_desktop/core/agents/base_agent.py

import logging
from storage.blackboard import Blackboard


class BaseAgent:
    """
    Abstract/base class for all agents.
    """

    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self.logger = logging.getLogger(self.__class__.__name__)

    def handle_query(self, user_message: str) -> str:
        """
        Subclasses must implement how queries are handled.
        """
        raise NotImplementedError("handle_query must be overridden by subclasses.")
