from langchain.tools import tool
import pandas as pd

# Load state salary data
INFO_DATA = pd.read_csv("bls/information_state_quarterwise_salary.csv")
PROF_DATA = pd.read_csv("bls/professional_state_quarterwise_salary.csv")

@tool
def get_state_salary(state: str = None, industry: str = None) -> dict:
    """
    Return the average state-wise salary for a given industry (information or professional).
    Returns a dictionary with assistant_message and missing_fields.
    """
    missing = []
    if not state:
        missing.append("state")
    if not industry:
        missing.append("industry")

    if missing:
        return {
            "assistant_message": "To fetch state-wise salary, I need your " + " and ".join(missing) + ".",
            "missing_fields": missing
        }

    industry = industry.lower()
    df = INFO_DATA if industry == "information" else PROF_DATA if industry == "professional" else None

    if df is None:
        return {
            "assistant_message": "Industry must be either 'information' or 'professional'.",
            "missing_fields": []
        }

    match = df[df["state"].str.lower() == state.lower()]
    if match.empty:
        return {
            "assistant_message": f"Sorry, I couldn't find data for {industry} industry in {state}.",
            "missing_fields": []
        }

    row = match.iloc[0]
    avg = round((row["Q1"] + row["Q2"] + row["Q3"]) / 3, 2)
    return {
        "assistant_message": f"In {state}, the average weekly salary for the {industry} industry is approximately ${avg}. (Based on Q1-Q3 data)",
        "missing_fields": []
    }
