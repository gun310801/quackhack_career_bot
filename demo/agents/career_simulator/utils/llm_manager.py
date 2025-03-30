import os
from typing import Dict, List, Any, Callable, Optional
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

# Load environment variables
load_dotenv()

class LLMManager:
    """
    Manages interactions with language models and provides caching.
    """
    
    def __init__(self, use_llm: bool = True):
        """Initialize LLM manager with optional LLM usage."""
        self.use_llm = use_llm
        self.llm = None
        
        # Cache for LLM-generated data
        self._role_skills_cache = {}
        self._default_salaries_cache = {}
        self._career_paths_cache = {}
        
        # Initialize LLM if enabled
        if self.use_llm:
            try:
                # Check if API key is available
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it before running.")
                
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.2,
                    api_key=api_key
                )
            except Exception as e:
                error_msg = f"Error initializing LLM: {str(e)}"
                print(error_msg)
                # Instead of falling back, raise an exception to stop execution
                raise RuntimeError(error_msg)
    
    def get_role_skills(self, role: str) -> List[str]:
        """Get skills for a specific role using LLM."""
        # Check cache
        if role in self._role_skills_cache:
            return self._role_skills_cache[role]
        
        if not self.use_llm or self.llm is None:
            # Instead of fallback, raise an error
            raise RuntimeError("LLM is required but not available. Please check your OpenAI API key.")
        
        try:
            # Define output schema
            skills_schema = ResponseSchema(
                name="skills",
                description="List of key skills required for the role",
                type="list[str]"
            )
            
            output_parser = StructuredOutputParser.from_response_schemas([skills_schema])
            format_instructions = output_parser.get_format_instructions()
            
            # Define prompt
            template = """
            You are a career and job market expert. Based on current industry trends,
            provide a comprehensive list of 10-15 key skills required for the role of {role}.
            
            Include both technical and soft skills where relevant. Be specific and use
            industry-standard terminology.
            
            {format_instructions}
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Generate response
            messages = prompt.format_messages(
                role=role,
                format_instructions=format_instructions
            )
            
            response = self.llm.invoke(messages)
            parsed_response = output_parser.parse(response.content)
            skills = parsed_response.get("skills", [])
            
            # Cache and return
            self._role_skills_cache[role] = skills
            return skills
            
        except Exception as e:
            error_msg = f"Error generating skills for {role}: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
    
    def get_default_salaries(self, level: str) -> Dict[str, float]:
        """Get default salaries for a career level using LLM."""
        # Check cache
        if level in self._default_salaries_cache:
            return self._default_salaries_cache[level]
        
        if not self.use_llm or self.llm is None:
            # Instead of fallback, raise an error
            raise RuntimeError("LLM is required but not available. Please check your OpenAI API key.")
        
        try:
            # Define output schema
            salary_schema = ResponseSchema(
                name="salary_data",
                description="Salary statistics for the given level",
                type="object"
            )
            
            output_parser = StructuredOutputParser.from_response_schemas([salary_schema])
            format_instructions = output_parser.get_format_instructions()
            
            # Define prompt
            template = """
            You are a compensation and job market expert. Based on current industry data for technology roles,
            provide realistic salary statistics for a {level} level position in the US technology industry.
            
            Return values in the following format:
            - mean: average salary (numeric value)
            - median: median salary (numeric value)
            - q1: 1st quartile/25th percentile salary (numeric value)
            - q3: 3rd quartile/75th percentile salary (numeric value)
            
            All values should be in USD without currency symbols or commas.
            
            {format_instructions}
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Generate response
            messages = prompt.format_messages(
                level=level,
                format_instructions=format_instructions
            )
            
            response = self.llm.invoke(messages)
            parsed_response = output_parser.parse(response.content)
            salary_data = parsed_response.get("salary_data", {})
            
            # Cache and return
            self._default_salaries_cache[level] = salary_data
            return salary_data
            
        except Exception as e:
            error_msg = f"Error generating salary data for {level}: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
    
    def get_intermediate_roles(self, current_role: str, target_role: str) -> List[str]:
        """Get potential intermediate roles between current and target roles."""
        # Check cache
        cache_key = f"{current_role}_to_{target_role}"
        if cache_key in self._career_paths_cache:
            return self._career_paths_cache[cache_key]
        
        if not self.use_llm or self.llm is None:
            # Instead of fallback, raise an error
            raise RuntimeError("LLM is required but not available. Please check your OpenAI API key.")
        
        try:
            # Define output schema
            paths_schema = ResponseSchema(
                name="intermediate_roles",
                description="List of intermediate roles between current and target roles",
                type="list[str]"
            )
            
            output_parser = StructuredOutputParser.from_response_schemas([paths_schema])
            format_instructions = output_parser.get_format_instructions()
            
            # Define prompt
            template = """
            You are a career transition expert. For someone looking to transition from {current_role} to {target_role},
            suggest 2-3 intermediate roles that would create a logical stepping stone path.
            
            Consider roles that:
            - Share skills with both the current and target roles
            - Would help build relevant experience for the target role
            - Represent a gradual progression rather than a dramatic leap
            
            {format_instructions}
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Generate response
            messages = prompt.format_messages(
                current_role=current_role,
                target_role=target_role,
                format_instructions=format_instructions
            )
            
            response = self.llm.invoke(messages)
            parsed_response = output_parser.parse(response.content)
            intermediate_roles = parsed_response.get("intermediate_roles", [])
            
            # Cache and return
            self._career_paths_cache[cache_key] = intermediate_roles
            return intermediate_roles
                
        except Exception as e:
            error_msg = f"Error generating intermediate roles: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
    
    def get_job_market_insights(self, role: str) -> Dict[str, Any]:
        """Get job market insights for a role."""
        if not self.use_llm or self.llm is None:
            # Instead of fallback, raise an error
            raise RuntimeError("LLM is required but not available. Please check your OpenAI API key.")
            
        try:
            # Define output schema
            insights_schema = ResponseSchema(
                name="market_insights",
                description="Job market insights for the specified role",
                type="object"
            )
            
            output_parser = StructuredOutputParser.from_response_schemas([insights_schema])
            format_instructions = output_parser.get_format_instructions()
            
            # Define prompt
            template = """
            You are a job market and industry expert. Provide insights about the current job market 
            for the role of {role}. Include the following information:
            
            1. demand_level: Current demand level for this role (Very High, High, Moderate, Low)
            2. avg_salary_range: Average salary range for this role in the US (formatted as $X-$Y)
            3. top_companies: List of 3-5 top companies known for hiring this role
            4. most_requested_skills: List of 5-10 most requested skills for this role
            5. growth_outlook: Brief assessment of future growth prospects (1-2 sentences)
            
            {format_instructions}
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Generate response
            messages = prompt.format_messages(
                role=role,
                format_instructions=format_instructions
            )
            
            response = self.llm.invoke(messages)
            parsed_response = output_parser.parse(response.content)
            market_insights = parsed_response.get("market_insights", {})
            
            return market_insights
            
        except Exception as e:
            error_msg = f"Error generating market insights: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
    
    def get_career_path_description(self, path_roles: List[str], current_role: str, 
                                  target_role: str, path_type: str, time_estimate: str) -> str:
        """
        Generate a description for a career path based on its type and components.
        
        Args:
            path_roles: List of roles in the path
            current_role: Starting role
            target_role: Target role
            path_type: Type of path ('fastest', 'direct', 'skill-focused', or 'management')
            time_estimate: Time estimate string (if available)
            
        Returns:
            A description of the career path
        """
        if not self.use_llm or self.llm is None:
            # Instead of fallback, raise an error
            raise RuntimeError("LLM is required but not available. Please check your OpenAI API key.")
            
        try:
            # Build the path string
            path_str = " → ".join(path_roles)
            
            # Define the prompt based on path type
            template = """
            You are a career transition expert. Provide a concise 2-3 sentence description for the 
            following career path from {current_role} to {target_role}:
            
            Path: {path_str}
            Path type: {path_type}
            {time_str}
            
            Focus on:
            1. The key benefits of this specific path
            2. What skills will be developed
            3. Any tradeoffs or considerations
            
            Keep your description factual, realistic, and encouraging without using cliches.
            Do not include phrases like "this path" or "this approach" at the beginning of your response.
            Do not mention the time estimate in your description unless it's particularly relevant.
            """
            
            # Add time info if available
            time_str = f"Estimated time: {time_estimate}" if time_estimate else ""
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Generate response
            messages = prompt.format_messages(
                current_role=current_role,
                target_role=target_role,
                path_str=path_str,
                path_type=path_type,
                time_str=time_str
            )
            
            response = self.llm.invoke(messages)
            description = response.content.strip()
            
            return description
            
        except Exception as e:
            error_msg = f"Error generating career path description: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
    
    def get_skill_gap_insights(self, current_skills: List[str], target_skills: List[str], 
                             target_role: str) -> str:
        """
        Generate insights about skill gaps and how to address them.
        
        Args:
            current_skills: List of skills the user currently has
            target_skills: List of skills required for the target role
            target_role: The target role
            
        Returns:
            Insights about skill gaps and development strategies
        """
        if not self.use_llm or self.llm is None:
            raise RuntimeError("LLM is required but not available. Please check your OpenAI API key.")
            
        try:
            # Format the skills lists
            current_skills_str = ", ".join(current_skills) if current_skills else "None"
            target_skills_str = ", ".join(target_skills) if target_skills else "Unknown"
            
            # Define the prompt
            template = """
            You are a career development and skills expert. Based on the following information:
            
            Current skills: {current_skills}
            Required skills for {target_role}: {target_skills}
            
            Provide 2-3 sentences of strategic advice on:
            1. Which skills to prioritize developing first and why
            2. The most effective ways to acquire these skills (courses, projects, etc.)
            3. Any insights on how long it might take to develop these skills to a professional level
            
            Be specific, practical, and brief.
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            
            # Generate response
            messages = prompt.format_messages(
                current_skills=current_skills_str,
                target_skills=target_skills_str,
                target_role=target_role
            )
            
            response = self.llm.invoke(messages)
            insights = response.content.strip()
            
            return insights
            
        except Exception as e:
            error_msg = f"Error generating skill gap insights: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
    
    def with_fallbacks(self, llm_method: Callable, *args, max_retries=2, **kwargs) -> Any:
        """
        Call an LLM method with retries and fallbacks.
        
        Args:
            llm_method: The LLM method to call
            max_retries: Maximum number of retries
            *args, **kwargs: Arguments to pass to the method
            
        Returns:
            The result of the LLM method or None if all attempts fail
        """
        if not self.use_llm:
            raise RuntimeError("LLM is required but not available. Please check your OpenAI API key.")
            
        for attempt in range(max_retries):
            try:
                return llm_method(*args, **kwargs)
            except Exception as e:
                print(f"LLM call failed (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Wait a bit before retrying
                    time.sleep(1)
                    
        # If all retries failed, raise an error
        error_msg = f"All LLM calls failed after {max_retries} attempts."
        print(error_msg)
        raise RuntimeError(error_msg) 