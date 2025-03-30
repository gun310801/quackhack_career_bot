from langchain.tools import tool
import pandas as pd

# Load datasets
INFO_DATA = pd.read_csv("bls/information_state_quarterwise_salary.csv")
PROF_DATA = pd.read_csv("bls/professional_state_quarterwise_salary.csv")

@tool
def compare_state_industries(state: str = None) -> dict:
    """
    Compare weekly salaries in Information vs Professional Services industries in a given state.
    Returns a dictionary with assistant_message and missing_fields.
    """
    if not state:
        return {
            "assistant_message": "To compare industries, I need the state name.",
            "missing_fields": ["state"]
        }

    info_row = INFO_DATA[INFO_DATA["state"].str.lower() == state.lower()]
    prof_row = PROF_DATA[PROF_DATA["state"].str.lower() == state.lower()]

    if info_row.empty or prof_row.empty:
        return {
            "assistant_message": f"Sorry, I couldn't find complete salary data for {state} in both industries.",
            "missing_fields": []
        }

    info_avg = round((info_row.iloc[0]["Q1"] + info_row.iloc[0]["Q2"] + info_row.iloc[0]["Q3"]) / 3, 2)
    prof_avg = round((prof_row.iloc[0]["Q1"] + prof_row.iloc[0]["Q2"] + prof_row.iloc[0]["Q3"]) / 3, 2)

    comparison = "higher than" if info_avg > prof_avg else "lower than"
    diff = abs(info_avg - prof_avg)

    return {
        "assistant_message": (
            f"In {state}, the Information industry pays approximately ${info_avg}/week, "
            f"which is {comparison} the Professional Services industry at ${prof_avg}/week. "
            f"The difference is around ${diff}/week."
        ),
        "missing_fields": []
    }
