from langchain_core.tools import tool
import pandas as pd

# Load benchmark dataset once (you can optimize to cache/load externally)
BUCKET_DATA = pd.read_csv("bls/Level_compensation_by_bucket.csv")

# @tool(name="compare_to_market")
@tool
def compare_to_market(current_role: str = None, level_bucket: str = None, current_salary: int = None) -> dict:
    """
    Compare user's current salary to industry medians from level bucket dataset.
    Returns a dictionary with assistant_message and optionally missing_fields.
    """
    missing = []
    if not level_bucket:
        missing.append("level_bucket")
    if current_salary is None:
        missing.append("current_salary")

    if missing:
        return {
            "assistant_message": "I need your " + " and ".join(missing) + " to give a proper comparison.",
            "missing_fields": missing
        }

    row = BUCKET_DATA[BUCKET_DATA["level_bucket"].str.lower() == level_bucket.lower()]

    if row.empty:
        return {"assistant_message": f"Sorry, I couldn't find benchmark data for level: {level_bucket}.", "missing_fields": []}

    median = row.iloc[0]["median"]

    try:
        median = int(median.replace(",", ""))
    except:
        return {"assistant_message": "The dataset has invalid median format.", "missing_fields": []}

    diff = current_salary - median
    percent = round((diff / median) * 100, 2)

    if percent > 0:
        result = f"Your salary is about {percent}% **above** the industry median (${median:,}) for the {level_bucket} level."
    elif percent < 0:
        result = f"Your salary is about {abs(percent)}% **below** the industry median (${median:,}) for the {level_bucket} level."
    else:
        result = f"Your salary is exactly equal to the industry median (${median:,}) for the {level_bucket} level."

    return {"assistant_message": result, "missing_fields": []}