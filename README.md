🧠 AI Career Advisor - Multi-Agent Chatbot
Team YOGS
Team Members:

Sneha Dharne – sdharne@stevens.edu

Gunik Luthra – gluthra@stevens.edu

Yash Gandhi – ygandhi3@stevens.edu

Om Gandhi – ogandhi@stevens.edu

📌 Problem Statement
Your task is to build an AI-powered system that answers tough career questions, identifies earning potential, and visualizes future growth—all through natural conversations.

💡 Project Description
We have developed a Multi-Agent AI Chatbot that responds to career-related questions in a conversational manner. The system is powered by intelligent agents trained on ChatGPT and enriched with datasets collected from online sources such as BLS, Levels.fyi, and LinkedIn.

The chatbot takes in user inputs such as:

Profession

Years of experience

Current salary

Location

Based on this information, it delivers insightful career advice. For example, it can answer questions like:

“Should I switch my career?”

“Where will I be paid more based on location?”

“What is my career path to earn more?”

And many more...

🛠️ Technologies Used
AI Agents

LangGraph

Python

Markov Decision Models

React.js

FastAPI

🧩 Project Architecture Overview
This project is designed as an AI-powered career advisory system that helps users make informed career decisions using real-time data and intelligent agents.

The architecture consists of multiple interconnected components, each serving a specific role in delivering insights, recommendations, and simulations. The UI Interface Agent is the central component that coordinates all activities between the user and backend agents.

1️⃣ UI Interface Agent
Acts as the main orchestrator that:

Understands user queries and intent.

Asks relevant follow-up questions to gather missing data.

Routes queries to the appropriate backend agents.

This modular design keeps the interface lightweight and scalable.

2️⃣ Career Planning Agent (AI Agent)
Provides:

Structured short-term and long-term career plans based on the user's current role and aspirations.

Fast pitch decks and visual representations of career progression.

3️⃣ Upskilling Recommendation Agent
Helps bridge skill gaps by:

Scraping job postings to understand market demands.

Recommending relevant skills, certifications, and courses.

Allowing resume upload to identify gaps.

4️⃣ Comparative Salary Agent
Provides salary benchmarking using:

BLS data

Levels.fyi compensation insights

LinkedIn job postings

Factors considered:

Seniority

Role complexity

Location

This ensures users receive accurate and industry-aligned salary estimates.

5️⃣ Simulator Agent
Uses a Markov model to simulate career switching. It includes:

Transition probabilities between roles and industries.

Data from Levels.fyi to support realistic simulations.

Career paths based on common job-switching patterns.

This enables users to predict possible outcomes before making a transition.

🔁 Flow Summary
User interacts with the UI Interface Agent via natural language.

The UI Agent routes the query to the most relevant AI agent.

The selected agent processes the request and fetches required data.

The UI Interface Agent compiles and returns the result in an intuitive, actionable format.
