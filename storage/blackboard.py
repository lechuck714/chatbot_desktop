# chatbot_desktop/storage/blackboard.py

class Blackboard:
    def __init__(self):
        self.conversation_history = []
        self.documents = {}
        self.dataframes = {}
        self.web_contents = {}
        self.intermediate = {}
