from typing import Dict, List, Any
from ..utils.data_loader import DataLoader
from ..utils.llm_manager import LLMManager

class SkillModel:
    """
    Model for analyzing skills and skill gaps for career transitions.
    """
    
    def __init__(self, data_loader: DataLoader, llm_manager: LLMManager):
        """Initialize with data loader and LLM manager."""
        self.data_loader = data_loader
        self.llm_manager = llm_manager
    
    def get_role_skills(self, role: str) -> List[str]:
        """Get required skills for a specific role."""
        # Try to get skills from job postings
        job_posting_skills = self.data_loader.extract_skills_from_job_posting(role)
        
        # Get skills from LLM
        llm_skills = self.llm_manager.get_role_skills(role)
        
        # Combine skills from different sources
        if job_posting_skills:
            combined_skills = job_posting_skills.copy()
            
            # Add skills from LLM
            for skill in llm_skills:
                if skill not in combined_skills:
                    combined_skills.append(skill)
            
            return combined_skills
        
        # If no job posting skills, use LLM skills
        return llm_skills
    
    def analyze_skill_gaps(self, profile: Dict) -> Dict:
        """
        Analyze skill gaps between current skills and target role requirements.
        """
        current_role = profile.get("current_role", "")
        target_role = profile.get("target_role", "")
        current_skills = profile.get("current_skills", [])
        
        # Normalize skills for better matching
        current_skills = [skill.strip() for skill in current_skills]
        
        # Get required skills for target role
        target_skills = self.get_role_skills(target_role)
        
        # Normalize for comparison
        normalized_current = [self._normalize_skill(skill) for skill in current_skills]
        normalized_target = [self._normalize_skill(skill) for skill in target_skills]
        
        matching_skills = []
        missing_skills = []
        
        # Find matching and missing skills with more robust matching
        for i, target_skill in enumerate(normalized_target):
            found = False
            for j, current_skill in enumerate(normalized_current):
                if target_skill == current_skill or \
                   (len(target_skill.split()) > 1 and target_skill in current_skill) or \
                   (len(current_skill.split()) > 1 and current_skill in target_skill):
                    matching_skills.append(target_skills[i])
                    found = True
                    break
            if not found:
                missing_skills.append(target_skills[i])
        
        # Calculate match percentage
        skill_match_percent = round(len(matching_skills) / len(target_skills) * 100) if target_skills else 0
        
        # Add additional skill insights using LLM
        skill_insights = ""
        if self.llm_manager.use_llm:
            try:
                skill_insights = self.llm_manager.get_skill_gap_insights(current_skills, target_skills, target_role)
            except Exception as e:
                print(f"Error getting skill gap insights: {str(e)}")
                # Just continue without additional insights
        
        return {
            "current_skills": current_skills,
            "target_skills": target_skills,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "skill_match_percent": skill_match_percent,
            "insights": skill_insights
        }
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize a skill name for better comparison."""
        return skill.lower().strip()
    
    def _generate_skill_development_suggestions(self, missing_skills: List[str]) -> List[Dict[str, str]]:
        """Generate learning resource suggestions for missing skills."""
        suggestions = []
        
        for skill in missing_skills:
            suggestion = {
                "skill": skill,
                "resources": self._suggest_resources_for_skill(skill)
            }
            suggestions.append(suggestion)
            
        return suggestions
    
    def _suggest_resources_for_skill(self, skill: str) -> List[str]:
        """Suggest specific learning resources for a skill."""
        # We could enhance this by having the LLM suggest resources
        return [
            "LinkedIn Learning courses",
            "Udemy courses related to this skill",
            "Practice projects on GitHub"
        ] 