# agents/data_agent.py

import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from chatbot import ask_chatgpt

class DataAgent:
    def __init__(self, blackboard):
        self.blackboard = blackboard
        self.active_df_id = None

    def set_active_df(self, df_id):
        self.active_df_id = df_id

    def handle_query(self, user_msg):
        """
        A flexible data analysis approach that can:
        - Summarize stats
        - Group by a column
        - Plot a column if user says 'plot <col>'
        - Actually generate .png charts and return [PLOT]path[/PLOT] placeholders
        Then we ask GPT for expert commentary on partial results.
        """
        print("DEBUG: DataAgent is handling the query!")
        self.blackboard.conversation_history.append(
            {"role":"system","content":"(DataAgent analyzing your CSV...)"}
        )

        if not self.active_df_id or self.active_df_id not in self.blackboard.dataframes:
            return "No DataFrame active in DataAgent."

        df = self.blackboard.dataframes[self.active_df_id]
        user_lower = user_msg.lower()
        columns = list(df.columns)

        analysis_result = ""
        created_plots = []

        # 1) Stats / describe
        if any(kw in user_lower for kw in ["stats","describe","summary"]):
            desc_str = df.describe(include='all').to_string()
            analysis_result += f"**DataFrame describe**:\n{desc_str}\n\n"

        # 2) Group by
        group_match = re.search(r"group\s+by\s+(\S+)", user_lower)
        if group_match:
            col_group = group_match.group(1)
            if col_group in columns:
                grouped_txt = df.groupby(col_group).describe().to_string()
                analysis_result += f"(Group by '{col_group}'):\n{grouped_txt}\n\n"
            else:
                analysis_result += f"(No column '{col_group}' found for group by.)\n\n"

        # 3) Plot / chart
        #   - parse pattern: 'plot <col>' or 'chart <col>'
        #   - physically create .png with make_plot()
        plot_match = re.search(r"(plot|chart)\s+(\S+)", user_lower)
        if plot_match:
            col_plot = plot_match.group(2)
            if col_plot in columns:
                plot_path = self.make_plot(df, col_plot)
                created_plots.append(plot_path)
                analysis_result += f"Created a plot for column '{col_plot}': [PLOT]{plot_path}[/PLOT]\n"
            else:
                analysis_result += f"(No column '{col_plot}' found for plotting.)\n"
        elif "plot" in user_lower or "chart" in user_lower:
            # user wants a plot but didn't specify which column
            # let's do a general snippet, or maybe we make a plot of all numeric columns
            numeric_cols = df.select_dtypes(include='number').columns
            plot_path = self.make_multi_plot(df, numeric_cols)
            created_plots.append(plot_path)
            analysis_result += f"Created a multi-col plot: [PLOT]{plot_path}[/PLOT]\n"

        # If no analysis done, fallback
        if not analysis_result.strip():
            analysis_result = "No specific 'describe','group by','plot' keywords detected.\n"\
                              f"Available columns: {columns}\n"

        # Summon GPT for final commentary
        final_prompt = (
            f"User query: {user_msg}\n\n"
            f"Partial data analysis:\n{analysis_result}\n"
            "Please provide an expert-level commentary."
        )
        commentary = ask_chatgpt(final_prompt)
        return f"{analysis_result}\n**Expert Commentary**:\n{commentary}"

    def make_plot(self, df, col):
        """
        Physically create a line plot for the given column, store in temp folder, return path.
        """
        os.makedirs("temp", exist_ok=True)
        fname = f"plot_{col}.png"
        path = os.path.join("temp", fname)

        plt.figure()
        plt.plot(df.index, df[col], label=col)
        plt.title(f"Line plot of '{col}'")
        plt.xlabel("Index")
        plt.ylabel(col)
        plt.legend()
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return path

    def make_multi_plot(self, df, numeric_cols):
        """
        Plot all numeric columns on separate subplots or a single figure.
        For demonstration, let's do them all in one figure, stacked.
        """
        os.makedirs("temp", exist_ok=True)
        path = os.path.join("temp", "plot_all_numeric.png")

        if len(numeric_cols) == 0:
            return path  # no numeric columns => empty plot

        plt.figure(figsize=(6, 4 + len(numeric_cols)*1.5))
        for i, col in enumerate(numeric_cols, start=1):
            plt.subplot(len(numeric_cols), 1, i)
            plt.plot(df.index, df[col], label=col)
            plt.title(col)
            plt.tight_layout()

        plt.savefig(path)
        plt.close()
        return path
