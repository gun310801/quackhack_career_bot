from langchain_core.tools import tool
import pandas as pd

# Load benchmark dataset
BUCKET_DATA = pd.read_csv("bls/Level_compensation_by_bucket.csv")

# @tool(name="get_salary_summary")
@tool
def get_salary_summary(level_bucket: str = None) -> dict:
    """
    Returns summary stats for a given level bucket (e.g., Entry, Mid, Senior).
    Returns a dictionary with assistant_message and missing_fields.
    """
    if not level_bucket:
        return {
            "assistant_message": "To get salary summary, I need the level bucket (e.g., Entry, Mid, Senior).",
            "missing_fields": ["level_bucket"]
        }

    row = BUCKET_DATA[BUCKET_DATA["level_bucket"].str.lower() == level_bucket.lower()]

    if row.empty:
        return {
            "assistant_message": f"Sorry, I couldn't find data for the level bucket '{level_bucket}'.",
            "missing_fields": []
        }

    r = row.iloc[0]
    return {
        "assistant_message": (
            f"For {level_bucket} level roles, the average compensation is ${r['mean']}, "
            f"median is ${r['median']}, with Q1 at ${r['Q1']} and Q3 at ${r['Q3']}."
        ),
        "missing_fields": []
    }
