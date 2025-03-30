import os
import pandas as pd
import re
from typing import Dict, List, Any, Optional


class DataLoader:
    """
    Utility for loading and managing data used by the career simulator.
    """
    
    def __init__(self, salary_data_dir: str = "salary_trends_datasets"):
        """Initialize with path to salary data directory."""
        self.salary_data_dir = salary_data_dir
        self.salary_data = None
        self.company_salary_data = None
        self.general_salary_data = None
        
        self.job_postings_data = None
        self.job_postings_loaded = False
        self.job_postings_skills = {}
        
        self._load_salary_data()
        self.load_job_postings_data()
    
    def _load_salary_data(self) -> None:
        """Load salary data from CSV files."""
        try:
            print(f"DataLoader attempting to load salary data from: {self.salary_data_dir}")
            
            # If the path points directly to a CSV file (Level_compensation_by_company.csv)
            if self.salary_data_dir.endswith('.csv') and os.path.exists(self.salary_data_dir):
                file_name = os.path.basename(self.salary_data_dir)
                
                if "Level_compensation_by_company" in file_name:
                    print(f"Loading company compensation data from: {self.salary_data_dir}")
                    self.company_salary_data = pd.read_csv(self.salary_data_dir)
                    
                    # Look for level bucket file in the same directory
                    data_dir = os.path.dirname(self.salary_data_dir)
                    bucket_file = os.path.join(data_dir, 'Level_compensation_by_bucket.csv')
                    if os.path.exists(bucket_file):
                        print(f"Loading bucket compensation data from: {bucket_file}")
                        self.general_salary_data = pd.read_csv(bucket_file)
                elif "Level_compensation_by_bucket" in file_name:
                    print(f"Loading bucket compensation data from: {self.salary_data_dir}")
                    self.general_salary_data = pd.read_csv(self.salary_data_dir)
                    
                    # Look for company file in the same directory
                    data_dir = os.path.dirname(self.salary_data_dir)
                    company_file = os.path.join(data_dir, 'Level_compensation_by_company.csv')
                    if os.path.exists(company_file):
                        print(f"Loading company compensation data from: {company_file}")
                        self.company_salary_data = pd.read_csv(company_file)
                else:
                    print(f"Unrecognized salary data file: {file_name}")
                    
                return
                
            # If it's a directory
            if os.path.isdir(self.salary_data_dir):
                level_company_path = os.path.join(self.salary_data_dir, 'Level_compensation_by_company.csv')
                level_bucket_path = os.path.join(self.salary_data_dir, 'Level_compensation_by_bucket.csv')
                
                if os.path.exists(level_company_path):
                    print(f"Loading company compensation data from: {level_company_path}")
                    self.company_salary_data = pd.read_csv(level_company_path)
                
                if os.path.exists(level_bucket_path):
                    print(f"Loading bucket compensation data from: {level_bucket_path}")
                    self.general_salary_data = pd.read_csv(level_bucket_path)
                    
                return
                
            # Try to find the directory by checking various paths
            print("Trying to find salary data files in various locations...")
            # Original directory-based loading logic
            possible_dirs = [
                self.salary_data_dir,  # Specified directory
                os.path.dirname(self.salary_data_dir) if not os.path.isdir(self.salary_data_dir) else self.salary_data_dir,  # Parent directory if it's a file
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"),  # Project data directory
                os.path.join(os.path.dirname(__file__), "..", "data"),  # Agent data directory
                os.path.abspath(self.salary_data_dir)  # Absolute path
            ]
            
            for directory in possible_dirs:
                if not os.path.exists(directory):
                    continue
                    
                print(f"Checking directory: {directory}")
                level_company_path = os.path.join(directory, 'Level_compensation_by_company.csv')
                level_bucket_path = os.path.join(directory, 'Level_compensation_by_bucket.csv')
                
                if os.path.exists(level_company_path):
                    print(f"Loading company compensation data from: {level_company_path}")
                    self.company_salary_data = pd.read_csv(level_company_path)
                    break
                
                if os.path.exists(level_bucket_path):
                    print(f"Loading bucket compensation data from: {level_bucket_path}")
                    self.general_salary_data = pd.read_csv(level_bucket_path)
                    break
            
            if self.company_salary_data is None and self.general_salary_data is None:
                print(f"Salary data files not found. Using default values.")
                
        except Exception as e:
            print(f"Error loading salary data: {str(e)}")
            print("Using default salary values.")
    
    def load_job_postings_data(self) -> None:
        """Load job postings data from CSV file."""
        try:
            print("Attempting to load job postings data...")
            
            # Determine project root directory
            file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(file_dir, "../../../.."))
            
            # Try various possible locations for the job postings file
            possible_paths = [
                os.path.join(project_root, "data/filtered_job_description.csv"),  # Project data directory
                os.path.join(project_root, "filtered_job_description.csv"),  # Project root
                "filtered_job_description.csv",  # Current directory
                "../filtered_job_description.csv",  # Parent directory
                os.path.join(file_dir, "../../../filtered_job_description.csv"),  # Relative to this file
                os.path.join(file_dir, "../../../data/filtered_job_description.csv"),  # Project data directory
            ]
            
            # If we have company data from a file, check the same directory
            if self.company_salary_data is not None and isinstance(self.salary_data_dir, str) and os.path.exists(self.salary_data_dir):
                data_dir = os.path.dirname(self.salary_data_dir)
                possible_paths.append(os.path.join(data_dir, "filtered_job_description.csv"))
                
                # Also check parent directories
                possible_paths.append(os.path.join(os.path.dirname(data_dir), "data/filtered_job_description.csv"))
                possible_paths.append(os.path.join(os.path.dirname(os.path.dirname(data_dir)), "data/filtered_job_description.csv"))
            
            job_postings_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    job_postings_path = path
                    print(f"Found job postings file at: {path}")
                    break
                    
            if job_postings_path is None:
                print("Job postings file not found. Continuing without job postings data.")
                return
            
            self.job_postings_data = pd.read_csv(job_postings_path, on_bad_lines='skip', 
                                                 encoding='utf-8', low_memory=False)
            if not self.job_postings_data.empty:
                print(f"Job postings data loaded successfully from: {job_postings_path}")
            else:
                print("Job postings data is empty. Continuing without job postings data.")
                return
            
            self.job_postings_data = self.job_postings_data.fillna('')
            self.job_postings_loaded = True
            
            self._preprocess_job_postings()
            
        except Exception as e:
            print(f"Error loading job postings data: {str(e)}")
    
    def _preprocess_job_postings(self) -> None:
        """Preprocess job postings data to normalize titles and prepare for analysis."""
        if not self.job_postings_loaded or self.job_postings_data is None:
            return
        
        title_mapping = {
            'software developer': 'Software Engineer',
            'front end developer': 'Frontend Engineer',
            'backend developer': 'Backend Engineer',
            'full stack developer': 'Full Stack Engineer',
            'data scientist': 'Data Scientist',
            'data analyst': 'Data Analyst',
            'data engineer': 'Data Engineer',
            'machine learning engineer': 'Machine Learning Engineer',
            'devops engineer': 'DevOps Engineer',
            'product manager': 'Product Manager',
            'ux designer': 'UX Designer',
            'ui designer': 'UI Designer'
        }
        
        self.job_postings_data['normalized_title'] = self.job_postings_data['job_title'].str.lower()
        for key, value in title_mapping.items():
            mask = self.job_postings_data['normalized_title'].str.contains(key, na=False)
            self.job_postings_data.loc[mask, 'normalized_title'] = value
        
        self.job_postings_data['normalized_title'] = self.job_postings_data['normalized_title'].str.title()
    
    def extract_skills_from_job_posting(self, role: str) -> List[str]:
        """Extract relevant skills for a job role from job postings."""
        if role in self.job_postings_skills:
            return self.job_postings_skills[role]
        
        if not self.job_postings_loaded or self.job_postings_data is None:
            return []
        
        role_lower = role.lower()
        
        matching_postings = self.job_postings_data[
            self.job_postings_data['normalized_title'].str.lower().str.contains(role_lower) |
            self.job_postings_data['job_title'].str.lower().str.contains(role_lower)
        ]
        
        if matching_postings.empty:
            return []
        
        # Common skill keywords to look for
        skill_keywords = {
            'python', 'java', 'javascript', 'c++', 'sql', 'react', 'aws', 
            'machine learning', 'data analysis', 'cloud', 'agile'
        }
        
        skills = set()
        
        for _, posting in matching_postings.iterrows():
            text = ' '.join([
                str(posting.get('description_text', '')), 
                str(posting.get('qualifications', '')),
                str(posting.get('description', ''))
            ]).lower()
            
            for skill in skill_keywords:
                if skill in text:
                    if skill in ['html', 'css', 'sql', 'aws']:
                        skills.add(skill.upper())
                    elif skill in ['javascript', 'python', 'java', 'c++']:
                        skills.add(skill.capitalize())
                    else:
                        if ' ' in skill:
                            skills.add(' '.join(word.capitalize() for word in skill.split()))
                        else:
                            skills.add(skill.capitalize())
            
            # Extract bullet point skills
            bullet_points = re.findall(r'[•·■◦-]\s*(.*?)(?:\n|$)', text)
            for point in bullet_points:
                words = point.split()
                if 1 <= len(words) <= 5:
                    skills.add(' '.join(word.capitalize() for word in words))
        
        # Filter out common words and very short skills
        filtered_skills = [skill for skill in skills if 
                          len(skill) > 2 and 
                          len(skill.split()) <= 3 and 
                          skill.lower() not in {'the', 'and', 'or', 'with'}]
        
        self.job_postings_skills[role] = filtered_skills
        
        return filtered_skills
    
    def get_job_posting_example(self, role: str) -> Dict[str, str]:
        """Get an example job posting for a role."""
        example = {
            "title": "",
            "company": "",
            "description": "",
            "qualifications": ""
        }
        
        if not self.job_postings_loaded or self.job_postings_data is None:
            return example
        
        role_lower = role.lower()
        
        matching_postings = self.job_postings_data[
            self.job_postings_data['normalized_title'].str.lower().str.contains(role_lower) |
            self.job_postings_data['job_title'].str.lower().str.contains(role_lower)
        ]
        
        if matching_postings.empty:
            return example
        
        # Find a good example with sufficient description
        best_posting = None
        for _, posting in matching_postings.iterrows():
            description = str(posting.get('description_text', ''))
            qualifications = str(posting.get('qualifications', ''))
            
            if len(description) > 200 and len(qualifications) > 100:
                best_posting = posting
                break
        
        if best_posting is None and not matching_postings.empty:
            best_posting = matching_postings.iloc[0]
        
        if best_posting is not None:
            example["title"] = str(best_posting.get('job_title', ''))
            example["company"] = str(best_posting.get('company_name', ''))
            
            description = str(best_posting.get('description_text', ''))
            qualifications = str(best_posting.get('qualifications', ''))
            
            # Truncate long text
            example["description"] = (description[:500] + '...') if len(description) > 500 else description
            example["qualifications"] = (qualifications[:500] + '...') if len(qualifications) > 500 else qualifications
            
        return example 