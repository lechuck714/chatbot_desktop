# agents/web_agent.py

import requests
from services.ai_service import ask_chatgpt

class WebAgent:
    def __init__(self, blackboard):
        self.blackboard = blackboard

    def handle_query(self, user_msg):
        print("DEBUG: WebAgent handling query!")
        self.blackboard.conversation_history.append(
            {"role":"system","content":"(WebAgent fetching a URL...)"}
        )

        # naive parse for 'http' or 'https'
        words = user_msg.split()
        url = None
        for w in words:
            if w.startswith("http://") or w.startswith("https://"):
                url = w
                break

        if not url:
            return "No URL found in your request. Try 'fetch http://...' or 'scrape https://...'"

        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                page_text = resp.text
                truncated = page_text[:3000]

                # flatten conversation so far
                conv_text = ""
                for c in self.blackboard.conversation_history:
                    role = c["role"]
                    content = c["content"]
                    conv_text += f"{role.capitalize()}: {content}\n"

                prompt = (
                    f"{conv_text}\n\n"
                    f"Fetched webpage:\n{truncated}\n\n"
                    f"User asked: {user_msg}"
                )
                interpretation = ask_chatgpt(prompt)
                return interpretation
            else:
                return f"Failed to fetch {url}. HTTP status {resp.status_code}"
        except Exception as e:
            return f"Error fetching {url}: {e}"
