from langchain_core.tools import tool
import pandas as pd

# Load company-level salary data
COMPANY_DATA = pd.read_csv("bls/Level_compensation_by_company.csv")

# @tool(name="get_company_salary_data")
@tool
def get_company_salary_data(company: str, level_bucket: str) -> str:
    """
    Return salary summary for a given company and level bucket (e.g., Mid, Senior).
    """
    match = COMPANY_DATA[
        (COMPANY_DATA["company"].str.lower() == company.lower()) &
        (COMPANY_DATA["level_bucket"].str.lower() == level_bucket.lower())
    ]

    if match.empty:
        return f"Sorry, I couldn't find salary data for {company} at {level_bucket} level."

    row = match.iloc[0]
    return (
        f"At {company}, {level_bucket} level roles have an average salary of ${row['mean']}, "
        f"median of ${row['median']}, with Q1 at ${row['Q1']} and Q3 at ${row['Q3']}."
    )
