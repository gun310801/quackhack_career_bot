from typing import Dict, List, Any
import numpy as np
import networkx as nx
from ..utils.llm_manager import LLMManager
import random

class CareerTransitionModel:
    """
    Model for simulating career transitions using Markov models.
    """
    
    def __init__(self, llm_manager: LLMManager):
        """Initialize with LLM manager."""
        self.llm_manager = llm_manager
    
    def identify_intermediate_roles(self, current_role: str, target_role: str) -> List[str]:
        """
        Identify potential intermediate roles between current and target roles.
        """
        # Get intermediate roles from LLM
        intermediate_roles = self.llm_manager.get_intermediate_roles(current_role, target_role)
        return intermediate_roles if intermediate_roles else []
    
    def create_career_path_states(self, profile: Dict) -> List[str]:
        """Create possible career states for simulation."""
        current_role = profile["current_role"]
        current_level = profile["current_level"]
        target_role = profile["target_role"]
        
        levels = ["Entry", "Mid", "Senior", "Director"]
        
        try:
            current_level_idx = levels.index(current_level)
        except ValueError:
            current_level_idx = 1  # Default to Mid level
        
        states = []
        
        # Add states for current role at current and higher levels
        for i in range(current_level_idx, len(levels)):
            states.append(f"{current_role}_{levels[i]}")
        
        # Add states for intermediate roles
        if current_role != target_role:
            intermediate_roles = self.identify_intermediate_roles(current_role, target_role)
            
            for role in intermediate_roles:
                # Start intermediate roles at Mid level
                mid_idx = levels.index("Mid")
                for i in range(mid_idx, len(levels)):
                    states.append(f"{role}_{levels[i]}")
        
        # Add states for target role
        for i in range(current_level_idx, len(levels)):
            states.append(f"{target_role}_{levels[i]}")
        
        return states
    
    def simulate_career_paths(self, profile: Dict, n_steps: int = 48, n_simulations: int = 1000) -> Dict:
        """
        Simulate career paths using Markov models.
        """
        # Create transition matrix
        transition_data = self.create_transition_matrix(profile)
        matrix = np.array(transition_data["matrix"])
        states = transition_data["states"]
        
        # Find start state
        start_state_pattern = f"{profile['current_role']}_{profile['current_level']}"
        start_idx = 0
        for i, state in enumerate(states):
            if state == start_state_pattern:
                start_idx = i
                break
        
        # Run simulations
        all_paths = []
        for _ in range(n_simulations):
            current_idx = start_idx
            path = [current_idx]
            
            for step in range(n_steps):
                probs = matrix[current_idx, :]
                next_idx = np.random.choice(len(states), p=probs)
                path.append(next_idx)
                current_idx = next_idx
            
            all_paths.append(path)
        
        # Analyze results
        results = self._analyze_simulation_results(all_paths, states, profile, n_steps)
        results["transition_data"] = transition_data
        
        return results
    
    def create_transition_matrix(self, profile: Dict) -> Dict:
        """Create transition matrix for career simulations."""
        states = self.create_career_path_states(profile)
        n_states = len(states)
        matrix = np.zeros((n_states, n_states))
        
        # Rule-based approach for transition probabilities
        for i, from_state in enumerate(states):
            from_role, from_level = from_state.split('_')
            
            # Set diagonal to 0.7 - 70% chance to stay in current state
            matrix[i, i] = 0.7
            
            # Distribute remaining probability to possible transitions
            remaining_prob = 0.3
            possible_transitions = []
            
            for j, to_state in enumerate(states):
                if i == j:
                    continue
                
                to_role, to_level = to_state.split('_')
                
                # 1. Same role, next level
                if from_role == to_role and self._is_next_level(from_level, to_level):
                    possible_transitions.append((j, 2.0))  # Higher weight
                
                # 2. Different role, same level
                elif from_role != to_role and from_level == to_level:
                    # Check if roles are adjacent via LLM
                    if self._roles_are_adjacent(from_role, to_role, profile):
                        possible_transitions.append((j, 1.0))
                
                # 3. Target role gets higher weight
                if to_role == profile["target_role"]:
                    possible_transitions.append((j, 0.5))  # Additional weight
            
            # Normalize weights
            total_weight = sum(weight for _, weight in possible_transitions)
            if total_weight > 0 and possible_transitions:
                for j, weight in possible_transitions:
                    matrix[i, j] = (weight / total_weight) * remaining_prob
            
            # Ensure rows sum to 1
            row_sum = matrix[i, :].sum()
            if row_sum < 1.0:
                matrix[i, i] += (1.0 - row_sum)
        
        # Ensure all rows sum to 1
        for i in range(n_states):
            row_sum = matrix[i, :].sum()
            if row_sum > 0:
                matrix[i, :] /= row_sum
        
        return {
            "states": states,
            "matrix": matrix.tolist()
        }
    
    def create_career_graph(self, profile: Dict, simulation_results: Dict) -> Dict:
        """Create a graph representation of career paths."""
        states = simulation_results["states"]
        transition_data = simulation_results["transition_data"]
        matrix = np.array(transition_data["matrix"])
        
        G = nx.DiGraph()
        
        # Add nodes
        for state in states:
            role, level = state.split('_')
            G.add_node(state, role=role, level=level)
        
        # Add edges
        for i, from_state in enumerate(states):
            for j, to_state in enumerate(states):
                if matrix[i, j] > 0.05:  # Only add significant transitions
                    G.add_edge(from_state, to_state, probability=matrix[i, j])
        
        # Find paths
        paths_data = []
        
        start_state = f"{profile['current_role']}_{profile['current_level']}"
        target_states = [state for state in states if profile['target_role'] in state]
        
        for target in target_states:
            try:
                # Find paths with at most 5 steps
                simple_paths = list(nx.all_simple_paths(G, start_state, target, cutoff=5))
                
                for path in simple_paths:
                    path_prob = 1.0
                    transitions = []
                    
                    for i in range(len(path)-1):
                        from_idx = states.index(path[i])
                        to_idx = states.index(path[i+1])
                        prob = matrix[from_idx, to_idx]
                        path_prob *= prob
                        
                        transitions.append({
                            "from": path[i],
                            "to": path[i+1],
                            "probability": prob
                        })
                    
                    paths_data.append({
                        "path": path,
                        "overall_probability": path_prob,
                        "transitions": transitions
                    })
            except nx.NetworkXNoPath:
                continue
        
        # Sort paths by probability
        paths_data.sort(key=lambda x: x["overall_probability"], reverse=True)
        
        return {
            "nodes": list(G.nodes()),
            "edges": [(u, v, d) for u, v, d in G.edges(data=True)],
            "paths": paths_data[:5]  # Return top 5 paths
        }
    
    def _is_next_level(self, current_level: str, next_level: str) -> bool:
        """Check if next_level is the next career level after current_level."""
        levels = ["Entry", "Mid", "Senior", "Director"]
        try:
            current_idx = levels.index(current_level)
            next_idx = levels.index(next_level)
            return next_idx == current_idx + 1
        except ValueError:
            return False
    
    def _roles_are_adjacent(self, role1: str, role2: str, profile: Dict) -> bool:
        """Check if two roles are adjacent in typical career paths."""
        # Use LLM to determine if roles are adjacent
        next_roles = self.llm_manager.get_intermediate_roles(role1, profile.get("target_role", ""))
        return role2 in next_roles
    
    def _analyze_simulation_results(self, paths: List[List[int]], states: List[str], 
                                   profile: Dict, n_steps: int) -> Dict:
        """Analyze simulation results to extract insights."""
        target_role = profile["target_role"]
        total_simulations = len(paths)
        
        # Track how many simulations reach target role at each step
        target_role_counts = np.zeros(n_steps + 1)
        state_counts = np.zeros((n_steps + 1, len(states)))
        
        for path in paths:
            for step, state_idx in enumerate(path):
                state_counts[step, state_idx] += 1
                
                state_name = states[state_idx]
                if target_role in state_name:
                    target_role_counts[step] += 1
        
        # Calculate probabilities
        target_role_probs = target_role_counts / total_simulations
        state_probs = state_counts / total_simulations
        
        # Track transition times
        transition_times = []
        success_paths = []
        
        for path in paths:
            for step, state_idx in enumerate(path):
                state_name = states[state_idx]
                if target_role in state_name:
                    transition_times.append(step)
                    success_paths.append(path)
                    break
        
        # Calculate success metrics
        success_rate = len(transition_times) / total_simulations
        avg_transition_time = np.mean(transition_times) if transition_times else float('inf')
        
        # Sample paths for examples (ensure we have 3 distinct paths)
        sample_paths = []
        if success_paths:
            if len(transition_times) >= 3:
                sorted_indices = np.argsort(transition_times)
                
                # Get quick, medium, and slow transition examples
                # Quick path (around 25th percentile)
                quick_idx = sorted_indices[int(len(sorted_indices) * 0.25)]
                
                # Medium path (around 50th percentile)
                medium_idx = sorted_indices[int(len(sorted_indices) * 0.5)]
                
                # Slow path (around 75th percentile)
                slow_idx = sorted_indices[int(len(sorted_indices) * 0.75)]
                
                # Ensure we have distinct paths by checking if they lead to different roles
                sample_indices = [quick_idx, medium_idx, slow_idx]
                
                # Generate the path data
                for idx in sample_indices:
                    path_indices = success_paths[idx]
                    path_states = [states[i] for i in path_indices]
                    transition_step = transition_times[idx]
                    
                    # Extract roles from path_states for later comparison
                    roles_in_path = []
                    for state in path_states:
                        if '_' in state:
                            role = state.split('_')[0]
                            if role not in roles_in_path:
                                roles_in_path.append(role)
                    
                    sample_paths.append({
                        "indices": path_indices,
                        "states": path_states,
                        "transition_month": transition_step,
                        "final_state": path_states[-1],
                        "roles": roles_in_path
                    })
                
                # If we have fewer than 3 distinct paths, add more from other percentiles
                if len(sample_paths) < 3:
                    # Try other percentiles
                    additional_percentiles = [0.1, 0.33, 0.66, 0.9]
                    for percentile in additional_percentiles:
                        if len(sample_paths) >= 3:
                            break
                            
                        idx = sorted_indices[int(len(sorted_indices) * percentile)]
                        # Check if this path is different from existing ones
                        path_indices = success_paths[idx]
                        path_states = [states[i] for i in path_indices]
                        transition_step = transition_times[idx]
                        
                        # Skip if we already have this path
                        if idx in sample_indices:
                            continue
                            
                        # Extract roles
                        roles_in_path = []
                        for state in path_states:
                            if '_' in state:
                                role = state.split('_')[0]
                                if role not in roles_in_path:
                                    roles_in_path.append(role)
                        
                        # Check if this path has a unique role sequence
                        is_unique = True
                        for existing_path in sample_paths:
                            if set(roles_in_path) == set(existing_path.get("roles", [])):
                                is_unique = False
                                break
                                
                        if is_unique:
                            sample_paths.append({
                                "indices": path_indices,
                                "states": path_states,
                                "transition_month": transition_step,
                                "final_state": path_states[-1],
                                "roles": roles_in_path
                            })
                            sample_indices.append(idx)
            elif len(transition_times) > 0:
                # If we have fewer than 3 successful paths, just use what we have
                for i, idx in enumerate(range(min(len(transition_times), 3))):
                    path_indices = success_paths[idx]
                    path_states = [states[i] for i in path_indices]
                    transition_step = transition_times[idx]
                    
                    # Extract roles
                    roles_in_path = []
                    for state in path_states:
                        if '_' in state:
                            role = state.split('_')[0]
                            if role not in roles_in_path:
                                roles_in_path.append(role)
                    
                    sample_paths.append({
                        "indices": path_indices,
                        "states": path_states,
                        "transition_month": transition_step,
                        "final_state": path_states[-1],
                        "roles": roles_in_path
                    })
        
        # Sort sample paths by transition time (fastest first)
        sample_paths.sort(key=lambda x: x.get("transition_month", float('inf')))
        
        return {
            "success_rate": success_rate,
            "avg_transition_time": avg_transition_time,
            "target_role_probs": target_role_probs.tolist(),
            "state_probs": state_probs.tolist(),
            "transition_times": transition_times,
            "sample_paths": sample_paths,
            "states": states
        }
    
    def get_realistic_transition_time(self, from_role, to_role, years_experience=0, initial_estimate=None):
        """
        Get a realistic transition time estimate between roles.
        
        Args:
            from_role: Starting role
            to_role: Target role
            years_experience: Years of experience the user has
            initial_estimate: Initial estimate in months (if available)
            
        Returns:
            Realistic transition time in months
        """
        # Base minimum times for different types of transitions (in months)
        min_times = {
            "entry_to_entry": 6,
            "entry_to_mid": 12,
            "entry_to_senior": 36,
            "entry_to_management": 48,
            "mid_to_mid": 6,
            "mid_to_senior": 24,
            "mid_to_management": 36,
            "senior_to_senior": 6,
            "senior_to_management": 24,
            "management_to_management": 12,
            "career_change": 18  # Complete career change (e.g., Engineer to Designer)
        }
        
        # Determine type of transition
        transition_type = "entry_to_entry"  # Default
        
        # Check if management roles
        if "manager" in to_role.lower() or "director" in to_role.lower() or "lead" in to_role.lower():
            if "manager" in from_role.lower() or "director" in from_role.lower() or "lead" in from_role.lower():
                transition_type = "management_to_management"
            elif "senior" in from_role.lower():
                transition_type = "senior_to_management"
            elif years_experience >= 5:
                transition_type = "mid_to_management"
            else:
                transition_type = "entry_to_management"
        
        # Check if senior role transition
        elif "senior" in to_role.lower():
            if "senior" in from_role.lower():
                transition_type = "senior_to_senior"
            elif years_experience >= 3:
                transition_type = "mid_to_senior"
            else:
                transition_type = "entry_to_senior"
        
        # Otherwise assume lateral or slight step up
        else:
            if "senior" in from_role.lower():
                transition_type = "senior_to_senior"
            elif years_experience >= 3:
                transition_type = "mid_to_mid"
            else:
                transition_type = "entry_to_entry"
        
        # Check if it's a career change
        from_domain = self._extract_domain(from_role)
        to_domain = self._extract_domain(to_role)
        
        if from_domain != to_domain and from_domain and to_domain:
            transition_type = "career_change"
        
        # Get minimum transition time
        min_time = min_times.get(transition_type, 12)
        
        # If we have an initial estimate, take the max of minimum and estimate
        if initial_estimate:
            return max(min_time, initial_estimate)
        
        # Add a little randomness and experience adjustment
        experience_factor = max(0.5, 1.0 - (years_experience * 0.05))  # More experience means faster transitions
        return int(min_time * experience_factor * (0.9 + 0.2 * random.random()))

    def _extract_domain(self, role):
        """Extract the domain/field from a role title."""
        domains = {
            "engineer": "engineering",
            "software": "engineering",
            "developer": "engineering",
            "data": "data",
            "scientist": "data",
            "analyst": "data",
            "product": "product",
            "design": "design",
            "manager": "management",
            "director": "management",
            "lead": "management",
            "marketing": "marketing",
            "sales": "sales",
            "operations": "operations",
            "finance": "finance",
            "hr": "hr"
        }
        
        for key, domain in domains.items():
            if key in role.lower():
                return domain
        return None 