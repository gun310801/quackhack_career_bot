#!/usr/bin/env python3
"""
Example script demonstrating the usage of the modular CareerSimulatorAgent.
"""

import sys
import os
import json
# Add parent directory to path so we can import the agents module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.career_simulator.career_simulator_agent import CareerSimulatorAgent

def main():
    print("Career Simulator Agent Demo")
    print("=" * 70)
    
    # Get the absolute path to the project root directory (assuming we're in demo/examples)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    # Try both possible locations for the data file
    possible_paths = [
        os.path.join(project_root, "demo/agents/career_simulator/data/Level_compensation_by_company.csv"),
        os.path.join(project_root, "data/Level_compensation_by_company.csv")
    ]
    
    # Find which path exists
    salary_data_path = None
    for path in possible_paths:
        if os.path.exists(path):
            salary_data_path = path
            print(f"Found data file at: {path}")
            break
    
    if not salary_data_path:
        print("ERROR: Could not find the required data file. Please ensure it exists.")
        return
    
    # Also look for the job postings file
    job_postings_file = os.path.join(project_root, "data/filtered_job_description.csv")
    if os.path.exists(job_postings_file):
        print(f"Found job postings file at: {job_postings_file}")
    
    # Initialize agent (use_llm=True enables LLM-based dynamic data generation)
    agent = CareerSimulatorAgent(salary_data_dir=salary_data_path, use_llm=True)
    
    # Example input
    user_profile = {
        "current_role": "Data Engineer",
        "current_level": "Entry",
        "years_experience": 0,
        "current_skills": ["Python", "JavaScript", "React", "SQL", "Git", "Docker"],
        "target_role": "SWE",
        "location": "Mountain View",
        "current_company": "Oncology Reference Inc.",
        "target_companies": ["Pfizer", "Merck", "Johnson & Johnson", "Novartis", "GSK"],
        "n_steps": 48,
        "n_simulations": 1000
    }
    
    
    
    print("\nProcessing career transition simulation...")
    result = agent.process(user_profile)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("\nCareer Transition Results:")
        print(f"- Success Rate: {result['simulation']['success_percentage']}%")
        
        # Format transition time
        years = result['simulation']['transition_time_years']
        months = result['simulation']['transition_time_months']
        time_str = ""
        if years > 0:
            time_str += f"{years} year{'s' if years > 1 else ''}"
        if months > 0:
            if time_str:
                time_str += " "
            time_str += f"{months} month{'s' if months > 1 else ''}"
        print(f"- Avg Transition Time: {time_str}")
        print(f"- Difficulty: {result['simulation']['difficulty'].capitalize()}")
        
        print("\nIntermediate Roles:")
        int_roles = result.get('intermediate_roles', [])
        if int_roles:
            path = " → ".join([user_profile["current_role"]] + int_roles + [user_profile["target_role"]])
            print(f"Recommended path: {path}")
        else:
            print("Direct transition recommended")
        
        # Print skills analysis
        skills = result.get('skills', {})
        print(f"\nSkill Match: {skills.get('match_percentage', 0)}%")
        
        print("\nMatching Skills:")
        for skill in skills.get('matching_skills', [])[:5]:
            print(f"- {skill}")
            
        print("\nSkills to Develop:")
        for skill in skills.get('missing_skills', [])[:5]:
            print(f"- {skill}")
        
        # Print job market insights
        market = result.get('market', {})
        print("\nJob Market Insights:")
        print(f"- Demand Level: {market.get('demand_level', 'Unknown')}")
        print(f"- Salary Range: {market.get('salary_range', 'Not available')}")
        print(f"- Growth Outlook: {market.get('growth_outlook', 'No data available')}")
        
        # Print career paths
        print("\nCareer Path Options:")
        for i, path in enumerate(result.get('career_paths', []), 1):
            path_type = path.get('type', 'unknown').capitalize()
            roles = path.get('roles', [])
            if roles:
                path_str = " → ".join(roles)
                print(f"\nOption {i}: {path_type} Path")
                print(f"Path: {path_str}")
                
                time = path.get('transition_time')
                if time is not None:
                    years = int(time // 12)
                    months = int(time % 12)
                    time_str = ""
                    if years > 0:
                        time_str += f"{years} year{'s' if years > 1 else ''}"
                    if months > 0:
                        if time_str:
                            time_str += " and "
                        time_str += f"{months} month{'s' if months > 1 else ''}"
                    if time_str:
                        print(f"Estimated Time: {time_str}")
                        
                        # Add context about typical transitions
                        if path.get('type') == 'management' and years >= 3:
                            print("Note: Management transitions typically take 3-5+ years in most industries")
                        elif path.get('type') == 'skill' and years >= 1:
                            print("Note: Skill-focused transitions often require 1-2+ years to build expertise")
        
        # Print that simulation completed successfully
        print("\nSimulation completed successfully. Data ready for chatbot.")
        
        # Print the raw JSON
        print("\nFull structured data available for chatbot integration:")
        # Uncomment to print the whole data structure
   
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 