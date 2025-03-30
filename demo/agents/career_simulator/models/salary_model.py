from typing import Dict
from ..utils.data_loader import DataLoader
from ..utils.llm_manager import LLMManager

class SalaryModel:
    """
    Model for providing salary data and analysis for career transitions.
    """
    
    def __init__(self, data_loader: DataLoader, llm_manager: LLMManager):
        """Initialize with data loader and LLM manager."""
        self.data_loader = data_loader
        self.llm_manager = llm_manager
        
        # Default salaries as fallback
        self.default_salaries = {
            "Entry": {"mean": 85000, "median": 80000, "q1": 70000, "q3": 95000},
            "Mid": {"mean": 120000, "median": 115000, "q1": 100000, "q3": 135000},
            "Senior": {"mean": 170000, "median": 160000, "q1": 140000, "q3": 190000},
            "Director": {"mean": 250000, "median": 230000, "q1": 200000, "q3": 300000}
        }
    
    def get_salary_data(self, role: str, level: str = "Mid", company: str = None) -> Dict:
        """Get salary data for a specific role, level, and company."""
        salary_stats = {
            "mean": 0,
            "median": 0,
            "q1": 0,
            "q3": 0,
            "source": "default"
        }
        
        # Try to get company-specific data
        if self.data_loader.company_salary_data is not None and company is not None:
            company_data = self.data_loader.company_salary_data[
                (self.data_loader.company_salary_data['company'].str.lower() == company.lower()) & 
                (self.data_loader.company_salary_data['level_bucket'] == level)
            ]
            
            if not company_data.empty:
                salary_stats["mean"] = company_data['mean'].values[0]
                salary_stats["median"] = company_data['median'].values[0]
                salary_stats["q1"] = company_data['Q1'].values[0]
                salary_stats["q3"] = company_data['Q3'].values[0]
                salary_stats["source"] = f"company_{company}"
                return salary_stats
        
        # Try to get general market data by level
        if self.data_loader.general_salary_data is not None:
            level_data = self.data_loader.general_salary_data[
                self.data_loader.general_salary_data['level_bucket'] == level
            ]
            
            if not level_data.empty:
                salary_stats["mean"] = level_data['mean'].values[0]
                salary_stats["median"] = level_data['median'].values[0]
                salary_stats["q1"] = level_data['Q1'].values[0]
                salary_stats["q3"] = level_data['Q3'].values[0]
                salary_stats["source"] = f"level_bucket_{level}"
                return salary_stats
        
        # Try to get dynamic salary data from LLM
        if self.llm_manager.use_llm:
            dynamic_salaries = self.llm_manager.get_default_salaries(level)
            if dynamic_salaries:
                salary_stats.update(dynamic_salaries)
                salary_stats["source"] = f"llm_generated_{level}"
                return salary_stats
        
        # Use predefined default salaries
        if level in self.default_salaries:
            salary_stats.update(self.default_salaries[level])
        
        return salary_stats 