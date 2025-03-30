from typing import Dict, Any
import re
from ..utils.data_loader import DataLoader
from ..utils.llm_manager import LLMManager

class MarketModel:
    """
    Model for providing job market insights for career transitions.
    """
    
    def __init__(self, data_loader: DataLoader, llm_manager: LLMManager):
        """Initialize with data loader and LLM manager."""
        self.data_loader = data_loader
        self.llm_manager = llm_manager
    
    def get_job_market_insights(self, role: str) -> Dict[str, Any]:
        """
        Get job market insights for a specific role, combining data sources and LLM.
        """
        # Get base insights from job postings data
        base_insights = self._get_job_market_insights_from_data(role)
        
        # Get an example job posting
        example_posting = self.data_loader.get_job_posting_example(role)
        
        # Get LLM-generated insights if available
        llm_insights = {}
        if self.llm_manager.use_llm:
            llm_insights = self.llm_manager.get_job_market_insights(role)
        
        # Combine all insights, prioritizing real data over LLM-generated data
        insights = {
            "demand_level": base_insights.get("demand_level") or llm_insights.get("demand_level", "Unknown"),
            "top_companies": base_insights.get("top_companies") or llm_insights.get("top_companies", []),
            "avg_salary_range": base_insights.get("avg_salary_range") or llm_insights.get("avg_salary_range", "Not available"),
            "most_requested_skills": base_insights.get("most_requested_skills") or llm_insights.get("most_requested_skills", []),
            "example_job_posting": example_posting,
            "growth_outlook": llm_insights.get("growth_outlook", "No data available")
        }
        
        return insights
    
    def _get_job_market_insights_from_data(self, role: str) -> Dict[str, Any]:
        """Extract job market insights from job postings data."""
        insights = {
            "demand_level": "Unknown",
            "top_companies": [],
            "avg_salary_range": "Not available",
            "most_requested_skills": []
        }
        
        if not self.data_loader.job_postings_loaded or self.data_loader.job_postings_data is None:
            return insights
            
        role_lower = role.lower()
        
        # Find matching job postings
        matching_postings = self.data_loader.job_postings_data[
            self.data_loader.job_postings_data['normalized_title'].str.lower().str.contains(role_lower) |
            self.data_loader.job_postings_data['job_title'].str.lower().str.contains(role_lower)
        ]
        
        if matching_postings.empty:
            return insights
        
        # Determine demand level based on number of postings
        num_postings = len(matching_postings)
        if num_postings >= 100:
            insights["demand_level"] = "Very High"
        elif num_postings >= 50:
            insights["demand_level"] = "High"
        elif num_postings >= 20:
            insights["demand_level"] = "Moderate"
        elif num_postings > 0:
            insights["demand_level"] = "Low"
        
        # Get top companies
        if 'company_name' in matching_postings.columns:
            company_counts = matching_postings['company_name'].value_counts().head(5)
            insights["top_companies"] = [{"name": company, "job_count": count} 
                                        for company, count in company_counts.items()]
        
        # Get skills
        skills = self.data_loader.extract_skills_from_job_posting(role)
        insights["most_requested_skills"] = skills[:10] if skills else []
        
        # Extract salary ranges if available
        if 'salary_formatted' in matching_postings.columns:
            salary_data = matching_postings[matching_postings['salary_formatted'].str.len() > 0]['salary_formatted']
            if not salary_data.empty:
                salary_values = []
                for salary_str in salary_data:
                    if isinstance(salary_str, str):
                        numbers = re.findall(r'\$?([\d,]+)', salary_str)
                        if len(numbers) >= 2:
                            min_val = int(numbers[0].replace(',', ''))
                            max_val = int(numbers[1].replace(',', ''))
                            salary_values.append((min_val, max_val))
                
                if salary_values:
                    avg_min = sum(min_val for min_val, _ in salary_values) // len(salary_values)
                    avg_max = sum(max_val for _, max_val in salary_values) // len(salary_values)
                    insights["avg_salary_range"] = f"${avg_min:,} - ${avg_max:,}"
        
        return insights 