import os
from typing import Dict, List, Any

from .models.transition_model import CareerTransitionModel
from .models.salary_model import SalaryModel
from .models.skill_model import SkillModel
from .models.market_model import MarketModel
from .utils.llm_manager import LLMManager
from .utils.data_loader import DataLoader

class CareerSimulatorAgent:
    """
    Career simulator agent that uses models to simulate career transitions.
    This agent takes structured input and provides three different career path simulations:
    1. An ideal/easy path - the most direct route to the target role
    2. A skill-focused alternative - emphasizing technical expertise development
    3. A management-focused path - oriented toward leadership positions
    
    Each simulation includes detailed transition steps, timeline estimates, and rationales.
    """
    
    def __init__(self, salary_data_dir: str = "salary_trends_datasets", use_llm: bool = True):
        """
        Initialize CareerSimulatorAgent with necessary components.
        """
        # Print the exact path being used (for debugging)
        print(f"Initializing CareerSimulatorAgent with salary_data_dir: {salary_data_dir}")
        
        # Initialize data loader
        self.data_loader = DataLoader(salary_data_dir)
        
        # Initialize LLM manager if enabled
        self.llm_manager = LLMManager(use_llm)
        
        # Initialize models
        self.transition_model = CareerTransitionModel(self.llm_manager)
        self.salary_model = SalaryModel(self.data_loader, self.llm_manager)
        self.skill_model = SkillModel(self.data_loader, self.llm_manager)
        self.market_model = MarketModel(self.data_loader, self.llm_manager)
    
    def load_profile_from_dict(self, profile_dict: Dict) -> Dict:
        """
        Load user profile from a structured dictionary input.
        """
        profile = {
            "current_role": "Unknown",
            "current_level": "Entry",
            "years_experience": 0,
            "current_skills": [],
            "target_role": "Unknown",
            "location": "Unknown",
            "current_salary": 0,
            "current_company": None,
            "target_companies": []
        }
        
        # Update with provided values
        for key in profile_dict:
            if key in profile:
                profile[key] = profile_dict[key]
        
        # Adjust level based on experience if needed
        if profile["current_level"] == "Mid" and "years_experience" in profile_dict:
            years = profile_dict["years_experience"]
            if years < 2:
                profile["current_level"] = "Entry"
            elif years > 8:
                profile["current_level"] = "Senior"
        
        return profile
    
    def process(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user profile and return career transition simulations and insights.
        Returns structured data only, with no hardcoded text.
        """
        # Load and validate user profile
        user_profile = self.load_profile_from_dict(input_dict)
        
        if not user_profile.get('current_role') or not user_profile.get('target_role'):
            return {
                "error": "Missing required fields"
            }
        
        # Get simulation parameters
        n_steps = input_dict.get('n_steps', 48)
        n_simulations = input_dict.get('n_simulations', 1000)
        
        # Get intermediate roles
        intermediate_roles = self.transition_model.identify_intermediate_roles(
            user_profile['current_role'],
            user_profile['target_role']
        )
        
        # Analyze skill gaps
        skill_gap_analysis = self.skill_model.analyze_skill_gaps(user_profile)
        
        # Get job market insights
        market_insights = self.market_model.get_job_market_insights(user_profile['target_role'])
        
        # Run simulation
        simulation_results = self.transition_model.simulate_career_paths(
            user_profile, n_steps, n_simulations
        )
        
        # Create career graph
        career_graph = self.transition_model.create_career_graph(user_profile, simulation_results)

        # Calculate basic stats
        success_rate = simulation_results.get('success_rate', 0)
        avg_months = simulation_results.get('avg_transition_time', 0)
        years = int(avg_months // 12)
        months = int(avg_months % 12)
        
        # Get sample career paths for each strategy
        sample_paths = simulation_results.get('sample_paths', [])
        
        # Process career paths
        career_paths = []
        
        # Option 1: Fastest path
        if sample_paths and len(sample_paths) > 0:
            fastest_path = self._extract_path_data(sample_paths[0], "fastest", user_profile['current_role'], user_profile['target_role'])
            # Make sure the fastest path has a reasonable minimum time (at least 6 months)
            if fastest_path['transition_time'] < 6:
                fastest_path['transition_time'] = 6
            career_paths.append(fastest_path)
        else:
            career_paths.append({
                "type": "fastest",
                "roles": [user_profile['current_role'], user_profile['target_role']],
                "transition_time": max(6, avg_months)  # At least 6 months
            })
        
        # Option 2: Skill-focused path
        if sample_paths and len(sample_paths) > 1:
            skill_path = self._extract_path_data(sample_paths[1], "skill", user_profile['current_role'], user_profile['target_role'])
            # Make skill path take longer (at least 1 year, typically 1.5-2x the fastest path)
            if 'transition_time' in skill_path and skill_path['transition_time'] is not None:
                skill_path['transition_time'] = max(12, int(skill_path['transition_time'] * 1.5))
            else:
                skill_path['transition_time'] = 18  # Default to 1.5 years
            career_paths.append(skill_path)
        elif intermediate_roles and len(intermediate_roles) > 0:
            career_paths.append({
                "type": "skill",
                "roles": [user_profile['current_role'], intermediate_roles[0], user_profile['target_role']],
                "transition_time": 24  # Default to 2 years for skill-focused path
            })
        
        # Option 3: Management path
        if sample_paths and len(sample_paths) > 2:
            mgmt_path = self._extract_path_data(sample_paths[2], "management", user_profile['current_role'], user_profile['target_role'])
            # Management paths should take much longer (minimum 3-5 years)
            base_time = 36  # 3 years minimum
            if 'transition_time' in mgmt_path and mgmt_path['transition_time'] is not None:
                mgmt_path['transition_time'] = max(base_time, int(mgmt_path['transition_time'] * 3))
            else:
                mgmt_path['transition_time'] = base_time
            # Add "Senior" or "Lead" prefixes to intermediate roles if not already present
            if len(mgmt_path['roles']) > 2:
                for i in range(1, len(mgmt_path['roles']) - 1):
                    role = mgmt_path['roles'][i]
                    if "senior" not in role.lower() and "lead" not in role.lower():
                        mgmt_path['roles'][i] = f"Senior {role}"
            career_paths.append(mgmt_path)
        elif intermediate_roles and len(intermediate_roles) > 1:
            career_paths.append({
                "type": "management",
                "roles": [user_profile['current_role'], f"Senior {user_profile['current_role']}", intermediate_roles[1], f"Manager, {user_profile['target_role']}"],
                "transition_time": 48  # Default to 4 years for management path
            })
        else:
            # Create a more realistic management path if we don't have simulation data
            career_paths.append({
                "type": "management",
                "roles": [user_profile['current_role'], f"Senior {user_profile['current_role']}", f"Team Lead, {user_profile['current_role']}", f"Manager, {user_profile['target_role']}"],
                "transition_time": 60  # Default to 5 years
            })
        
        # Determine difficulty level
        difficulty = None
        success_percentage = success_rate * 100
        if success_percentage >= 80:
            difficulty = "easy"
        elif success_percentage >= 60:
            difficulty = "moderate"
        elif success_percentage >= 40:
            difficulty = "challenging"
        elif success_percentage >= 20:
            difficulty = "difficult"
        else:
            difficulty = "very_difficult"
        
        # Return structured data
        return {
            "profile": {
                "current_role": user_profile['current_role'],
                "target_role": user_profile['target_role'],
                "current_level": user_profile['current_level'],
                "years_experience": user_profile['years_experience'],
                "location": user_profile.get('location', None)
            },
            "simulation": {
                "success_rate": success_rate,
                "success_percentage": f"{success_rate * 100:.1f}",
                "avg_transition_time": avg_months,
                "transition_time_years": years,
                "transition_time_months": months,
                "difficulty": difficulty,
                "n_simulations": n_simulations
            },
            "skills": {
                "match_percentage": skill_gap_analysis.get('skill_match_percent', 0),
                "matching_skills": skill_gap_analysis.get('matching_skills', []),
                "missing_skills": skill_gap_analysis.get('missing_skills', [])
            },
            "market": {
                "demand_level": market_insights.get('demand_level', None),
                "salary_range": market_insights.get('avg_salary_range', None),
                "growth_outlook": market_insights.get('growth_outlook', None),
                "top_companies": market_insights.get('top_companies', [])[:5]
            },
            "career_paths": career_paths,
            "intermediate_roles": intermediate_roles
        }
    
    def _extract_path_data(self, path_data: Dict, path_type: str, current_role: str, target_role: str) -> Dict:
        """
        Extract structured data from a path simulation.
        """
        states = path_data.get('states', [])
        
        # Extract roles
        roles = []
        for state in states:
            if '_' in state:
                role = state.split('_')[0]
                if role not in roles:
                    roles.append(role)
            else:
                if state not in roles:
                    roles.append(state)
        
        # If path type is management, modify target
        if path_type == "management" and roles:
            roles[-1] = f"Manager, {roles[-1]}"
            
        # Get transition time
        months = path_data.get('transition_month', 0)
        
        # Get more realistic transition time based on the path type
        years_experience = self.load_profile_from_dict({}).get('years_experience', 0)
        
        if path_type == "fastest":
            # Fastest paths should still be somewhat realistic
            months = self.transition_model.get_realistic_transition_time(
                current_role, target_role, years_experience, months
            )
        elif path_type == "skill":
            # Skill paths take longer than fastest
            months = self.transition_model.get_realistic_transition_time(
                current_role, target_role, years_experience, max(months, 12)
            )
            months = max(months, 12)  # At least 1 year
        elif path_type == "management":
            # Management paths take much longer
            months = self.transition_model.get_realistic_transition_time(
                current_role, f"Manager, {target_role}", years_experience, max(months, 36)
            )
            months = max(months, 36)  # At least 3 years
            
        return {
            "type": path_type,
            "roles": roles,
            "transition_time": months
        }
    
    def _generate_response(self, user_profile, simulation_results, 
                          skill_analysis, intermediate_roles, 
                          career_graph, market_insights) -> str:
        """
        Generate a human-readable response from analysis results.
        """
        current_role = user_profile.get('current_role', 'your current role')
        target_role = user_profile.get('target_role', 'your target role')
        success_rate = simulation_results.get('success_rate', 0) * 100
        avg_months = simulation_results.get('avg_transition_time', 0)
        
        years = int(avg_months // 12)
        months = int(avg_months % 12)
        timing_str = f"{years} years" if years > 0 else ""
        timing_str += f" {months} months" if months > 0 or years == 0 else ""
        
        skill_match = skill_analysis.get('skill_match_percent', 0)
        
        response = f"""# Career Transition Analysis: {current_role} → {target_role}

## Overall Assessment

Based on your profile and our simulation of {simulation_results.get('n_simulations', 1000)} potential career paths:

- **Success Probability**: {success_rate:.1f}% chance of transitioning successfully
- **Average Transition Time**: {timing_str.strip()}
- **Skill Match**: {skill_match}% of required skills already in your profile

"""
        # Determine difficulty level
        difficulty = "Very Difficult"
        if success_rate >= 80:
            difficulty = "Easy"
        elif success_rate >= 60:
            difficulty = "Moderate"
        elif success_rate >= 40:
            difficulty = "Challenging"
        elif success_rate >= 20:
            difficulty = "Difficult"
        
        response += f"**Overall Difficulty**: {difficulty}\n\n"
        
        # Job Market Insights
        response += f"""## Job Market Insights for {target_role}

- **Demand Level**: {market_insights.get('demand_level', 'Unknown')}
- **Salary Range**: {market_insights.get('avg_salary_range', 'Not available')}
"""

        # Top Companies
        top_companies = market_insights.get('top_companies', [])
        if top_companies:
            response += "\n**Top Companies Hiring**:\n"
            for i, company in enumerate(top_companies[:5], 1):
                if isinstance(company, dict):
                    response += f"  {i}. {company.get('name', 'Unknown')}\n"
                else:
                    response += f"  {i}. {company}\n"
        
        # Skill Analysis
        response += f"""
## Skill Analysis

**Current Skill Match**:
"""
        matching_skills = skill_analysis.get('matching_skills', [])
        if matching_skills:
            for skill in matching_skills[:5]:
                response += f"- ✓ {skill}\n"
        else:
            response += "- No direct skill matches found\n"
        
        response += "\n**Skills to Develop**:\n"
        missing_skills = skill_analysis.get('missing_skills', [])
        if missing_skills:
            for skill in missing_skills[:7]:
                response += f"- {skill}\n"
        
        # Career Path Options (three different options)
        response += f"""
## Career Path Options

"""
        # Get sample paths from simulation results
        sample_paths = simulation_results.get('sample_paths', [])
        
        # Create career paths with different focuses
        career_paths = []
        
        # Option 1: Fastest path 
        option1_title = f"Option 1: Fastest Path to {target_role}"
        if sample_paths and len(sample_paths) > 0:
            fastest_path = sample_paths[0]
            path_states = fastest_path.get('states', [])
            
            # Extract role names (remove level suffixes)
            clean_path = []
            for state in path_states:
                if '_' in state:
                    role = state.split('_')[0]
                    if role not in clean_path:
                        clean_path.append(role)
                else:
                    if state not in clean_path:
                        clean_path.append(state)
            
            if clean_path:
                path_str = " → ".join(clean_path)
                months = fastest_path.get('transition_month', 0)
                years = int(months // 12)
                remainder_months = int(months % 12)
                time_str = f"{years} years" if years > 0 else ""
                time_str += f" {remainder_months} months" if remainder_months > 0 or years == 0 else ""
                
                # Use LLM to generate description or craft a dynamic description
                path_description = self._generate_path_description(
                    clean_path, 
                    current_role, 
                    target_role, 
                    "fastest", 
                    time_str.strip()
                )
                
                career_paths.append({
                    "title": option1_title,
                    "path": path_str,
                    "time": time_str.strip(),
                    "description": path_description
                })
            else:
                path_str = f"{current_role} → {target_role}"
                # Use LLM to generate description or craft a dynamic description
                path_description = self._generate_path_description(
                    [current_role, target_role], 
                    current_role, 
                    target_role, 
                    "direct", 
                    timing_str.strip()
                )
                
                career_paths.append({
                    "title": option1_title,
                    "path": path_str,
                    "time": timing_str.strip(),
                    "description": path_description
                })
        elif intermediate_roles:
            path_roles = [current_role] + intermediate_roles[:1] + [target_role]
            path_str = " → ".join(path_roles)
            
            # Use LLM to generate description or craft a dynamic description
            path_description = self._generate_path_description(
                path_roles, 
                current_role, 
                target_role, 
                "direct", 
                timing_str.strip()
            )
            
            career_paths.append({
                "title": option1_title,
                "path": path_str,
                "time": timing_str.strip(),
                "description": path_description
            })
        else:
            path_str = f"{current_role} → {target_role}"
            # Use LLM to generate description or craft a dynamic description
            path_description = self._generate_path_description(
                [current_role, target_role], 
                current_role, 
                target_role, 
                "direct", 
                timing_str.strip()
            )
            
            career_paths.append({
                "title": option1_title,
                "path": path_str,
                "time": timing_str.strip(),
                "description": path_description
            })
            
        # Option 2: Skill-focused alternative path
        option2_title = "Option 2: Skill-Focused Alternative Path"
        if intermediate_roles and len(intermediate_roles) > 1:
            alt_intermediate = intermediate_roles[1] if len(intermediate_roles) > 1 else intermediate_roles[0]
            path_roles = [current_role, alt_intermediate, target_role]
            path_str = " → ".join(path_roles)
            
            # Use LLM to generate description or craft a dynamic description
            path_description = self._generate_path_description(
                path_roles, 
                current_role, 
                target_role, 
                "skill-focused", 
                ""
            )
            
            career_paths.append({
                "title": option2_title,
                "path": path_str,
                "time": "",
                "description": path_description
            })
        elif sample_paths and len(sample_paths) > 1:
            medium_path = sample_paths[1]
            path_states = medium_path.get('states', [])
            
            # Extract role names (remove level suffixes)
            clean_path = []
            for state in path_states:
                if '_' in state:
                    role = state.split('_')[0]
                    if role not in clean_path:
                        clean_path.append(role)
                else:
                    if state not in clean_path:
                        clean_path.append(state)
            
            if clean_path:
                path_str = " → ".join(clean_path)
                months = medium_path.get('transition_month', 0)
                years = int(months // 12)
                remainder_months = int(months % 12)
                time_str = f"{years} years" if years > 0 else ""
                time_str += f" {remainder_months} months" if remainder_months > 0 or years == 0 else ""
                
                # Use LLM to generate description or craft a dynamic description
                path_description = self._generate_path_description(
                    clean_path, 
                    current_role, 
                    target_role, 
                    "skill-focused", 
                    time_str.strip()
                )
                
                career_paths.append({
                    "title": option2_title,
                    "path": path_str,
                    "time": time_str.strip(),
                    "description": path_description
                })
            else:
                # Specialize in current role before transition
                path_str = f"{current_role} (specialized) → {target_role}"
                
                # Use LLM to generate description or craft a dynamic description
                path_description = self._generate_path_description(
                    [f"{current_role} (specialized)", target_role], 
                    current_role, 
                    target_role, 
                    "skill-focused", 
                    ""
                )
                
                career_paths.append({
                    "title": option2_title,
                    "path": path_str,
                    "time": "",
                    "description": path_description
                })
        else:
            # Create a skill-based alternative using specialized skills
            path_str = f"{current_role} (with specialized skills) → {target_role}"
            
            # Use LLM to generate description or craft a dynamic description
            path_description = self._generate_path_description(
                [f"{current_role} (specialized)", target_role], 
                current_role, 
                target_role, 
                "skill-focused", 
                ""
            )
            
            career_paths.append({
                "title": option2_title,
                "path": path_str,
                "time": "",
                "description": path_description
            })
        
        # Option 3: Management-focused path
        option3_title = "Option 3: Management-Focused Path"
        if intermediate_roles:
            management_intermediate = f"Senior {current_role}"
            if len(intermediate_roles) > 2:
                management_intermediate = intermediate_roles[2]
            
            path_roles = [current_role, management_intermediate, f"Manager, {target_role}"]
            path_str = " → ".join(path_roles)
            
            # Use LLM to generate description or craft a dynamic description
            path_description = self._generate_path_description(
                path_roles, 
                current_role, 
                f"Manager, {target_role}", 
                "management", 
                ""
            )
            
            career_paths.append({
                "title": option3_title,
                "path": path_str,
                "time": "",
                "description": path_description
            })
        elif sample_paths and len(sample_paths) > 2:
            slow_path = sample_paths[2]
            path_states = slow_path.get('states', [])
            
            # Extract role names (remove level suffixes)
            clean_path = []
            for state in path_states:
                if '_' in state:
                    role = state.split('_')[0]
                    if role not in clean_path:
                        clean_path.append(role)
                else:
                    if state not in clean_path:
                        clean_path.append(state)
            
            # Add management title to final role
            if clean_path and len(clean_path) > 1:
                clean_path[-1] = f"Manager, {clean_path[-1]}"
                path_str = " → ".join(clean_path)
                
                months = slow_path.get('transition_month', 0)
                years = int(months // 12)
                remainder_months = int(months % 12)
                time_str = f"{years} years" if years > 0 else ""
                time_str += f" {remainder_months} months" if remainder_months > 0 or years == 0 else ""
                
                # Use LLM to generate description or craft a dynamic description
                path_description = self._generate_path_description(
                    clean_path, 
                    current_role, 
                    clean_path[-1], 
                    "management", 
                    time_str.strip()
                )
                
                career_paths.append({
                    "title": option3_title,
                    "path": path_str,
                    "time": time_str.strip(),
                    "description": path_description
                })
            else:
                # Create a management path with Team Lead
                path_str = f"{current_role} → Team Lead → {target_role}"
                
                # Use LLM to generate description or craft a dynamic description
                path_description = self._generate_path_description(
                    [current_role, "Team Lead", target_role], 
                    current_role, 
                    target_role, 
                    "management", 
                    ""
                )
                
                career_paths.append({
                    "title": option3_title,
                    "path": path_str,
                    "time": "",
                    "description": path_description
                })
        else:
            # Create a standard management path
            path_str = f"{current_role} → Senior {current_role} → Team Lead → {target_role}"
            
            # Use LLM to generate description or craft a dynamic description
            path_description = self._generate_path_description(
                [current_role, f"Senior {current_role}", "Team Lead", target_role], 
                current_role, 
                target_role, 
                "management", 
                ""
            )
            
            career_paths.append({
                "title": option3_title,
                "path": path_str,
                "time": "",
                "description": path_description
            })
        
        # Render all career paths
        for i, path in enumerate(career_paths):
            response += f"""### {path['title']}

**Path**: {path['path']}
"""
            if path['time']:
                response += f"\n**Estimated Time**: {path['time']}\n"
            
            response += f"\n{path['description']}\n"
            
            # Add a space between paths
            if i < len(career_paths) - 1:
                response += "\n"
        
        # Next Steps

        
        return response
        
    def _generate_path_description(self, path_roles: List[str], current_role: str, 
                                   target_role: str, path_type: str, time_estimate: str) -> str:
        """
        Generate a dynamic description for a career path based on its type and components.
        
        Args:
            path_roles: List of roles in the path
            current_role: Starting role
            target_role: Target role
            path_type: Type of path ('fastest', 'direct', 'skill-focused', or 'management')
            time_estimate: Time estimate string (if available)
            
        Returns:
            A description of the career path
        """
        # First try using LLM if available
        if self.llm_manager.use_llm:
            description = self.llm_manager.get_career_path_description(
                path_roles, current_role, target_role, path_type, time_estimate
            )
            if description:
                return description
        
        # Otherwise, generate a dynamic description based on the path type
        if path_type == "fastest" or path_type == "direct":
            if len(path_roles) <= 2:
                return (f"This direct transition from {current_role} to {target_role} is the most efficient " 
                        f"path based on our simulations. It requires focused skill development and networking "
                        f"to make the jump successfully.")
            else:
                intermediate = ", ".join(path_roles[1:-1])
                return (f"This path through {intermediate} represents the fastest route to {target_role} based on "
                        f"our analysis. The intermediate role(s) provide essential experience while minimizing "
                        f"overall transition time.")
        elif path_type == "skill-focused":
            skills_focus = ""
            if len(path_roles) > 2:
                skills_focus = ", ".join(path_roles[1:-1])
                return (f"This skill-focused path emphasizes building deeper technical expertise through {skills_focus}. "
                        f"While it may take longer than a direct transition, it builds a stronger foundation of "
                        f"skills that can lead to better long-term outcomes and higher compensation potential.")
            else:
                return (f"This approach focuses on building specialized technical skills within your current role "
                        f"before transitioning to {target_role}. Developing deeper expertise makes you a stronger "
                        f"candidate and can lead to better long-term outcomes.")
        elif path_type == "management":
            if "Manager" in target_role or "manager" in target_role:
                return (f"This leadership-oriented path develops both technical and management skills, "
                        f"ultimately leading to a management position. This trajectory typically leads to "
                        f"higher compensation and broader organizational impact, though it generally "
                        f"takes longer to achieve.")
            else:
                return (f"This path focuses on developing leadership and management skills alongside technical "
                        f"expertise. This approach can open more senior-level opportunities and potentially "
                        f"lead to higher compensation, though it typically requires more time investment.")
        else:
            # Generic fallback
            return (f"This career path from {current_role} to {target_role} offers a balance of skill "
                    f"development and career progression opportunities.") 