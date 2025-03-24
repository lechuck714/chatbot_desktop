# chatbot_desktop/core/agents/data_agent.py

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from .base_agent import BaseAgent


class DataAgent(BaseAgent):
    def __init__(self, blackboard):
        super().__init__(blackboard)
        self.active_df_id = None

    def set_active_df(self, df_id):
        self.active_df_id = df_id

    def handle_query(self, user_msg: str) -> str:
        self.logger.debug("DataAgent handling query.")

        if (not self.active_df_id) or (self.active_df_id not in self.blackboard.dataframes):
            return "No dataframe is currently loaded."

        df = self.blackboard.dataframes[self.active_df_id]

        lower_msg = user_msg.lower()
        # Basic examples of data-related queries
        if "head" in lower_msg:
            return str(df.head())
        elif "describe" in lower_msg:
            return str(df.describe(include="all"))
        elif "plot" in lower_msg:
            return self.make_plot(df)
        else:
            return (
                "DataAgent didn't understand your request. Try keywords like 'head', "
                "'describe', or 'plot'."
            )

    def make_plot(self, df: pd.DataFrame) -> str:
        numeric_cols = df.select_dtypes(include=["float", "int"]).columns
        if len(numeric_cols) < 1:
            return "No numeric columns to plot."

        # For simplicity, plot the first numeric column
        col = numeric_cols[0]
        plt.figure()
        df[col].plot(kind='hist', title=f"Histogram of {col}", bins=20)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        return (
            f"Here is a histogram of '{col}' as a base64 image:\n"
            f"<img src='data:image/png;base64,{img_base64}'/>"
        )
