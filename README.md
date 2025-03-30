# 🧠 AI Career Advisor - DuckRouter  
**Team YOGS**

## 👥 Team Members
- Sneha Dharne – [sdharne@stevens.edu](mailto:sdharne@stevens.edu)  
- Gunik Luthra – [gluthra@stevens.edu](mailto:gluthra@stevens.edu)  
- Yash Gandhi – [ygandhi3@stevens.edu](mailto:ygandhi3@stevens.edu)  
- Om Gandhi – [ogandhi@stevens.edu](mailto:ogandhi@stevens.edu)  

---

## 📌 Problem Statement  
Navigating careers is tough. Our goal is to build an AI-powered system that can answer complex career questions, assess earning potential, and visualize growth trajectories—all through natural, conversational interactions.

---

## 💡 Project Description  
We’ve developed **DuckRouter**, a multi-agent AI chatbot designed to give personalized career advice. It uses ChatGPT-based agents enhanced with real-world data from **BLS**, **Levels.fyi**, and **LinkedIn** to generate meaningful insights.

### ✅ The chatbot accepts inputs like:
- Profession  
- Years of Experience  
- Current Salary  
- Location  

Based on this, users can ask:
- “Should I switch careers?”  
- “Where will I be paid more based on location?”  
- “What’s my optimal path to earning more?”  
...and much more.

---

## 🛠️ Technologies Used  
- **AI Agents (LangGraph + ChatGPT)**  
- **Python**  
- **Markov Decision Models**  
- **FastAPI**  
- **React.js**

---

## 🧩 Architecture Overview  
DuckRouter is modular by design, featuring a multi-agent architecture to ensure scalability and intelligent decision-making.

### 🔹 1️⃣ UI Interface Agent  
Acts as the **central coordinator** that:  
- Interprets user intent  
- Gathers missing inputs via follow-ups  
- Routes queries to appropriate backend agents  
- Returns final insights in a clean, actionable format  

---

### 🔹 2️⃣ Career Planning Agent  
Delivers:
- Personalized short-term and long-term career plans  
- Visual pitch decks outlining career progression  

---

### 🔹 3️⃣ Upskilling Recommendation Agent  
Bridges skill gaps by:  
- Scraping job postings to identify in-demand skills  
- Recommending courses and certifications  
- Analyzing resumes to detect improvement areas  

---

### 🔹 4️⃣ Comparative Salary Agent  
Provides accurate benchmarking using:  
- **BLS statistics**  
- **Levels.fyi compensation data**  
- **LinkedIn job insights**  

Factors considered:
- Role seniority  
- Geographic location  
- Job complexity  

---

### 🔹 5️⃣ Career Switch Simulator Agent  
Predicts career transitions using a **Markov Model**, including:  
- Transition probabilities across roles/industries  
- Real-world career switching trends  
- Simulated outcomes for informed decision-making  

---

## 🔁 Flow Summary  
1. **User initiates** a conversation via the UI Agent  
2. **UI Agent interprets** and collects missing inputs  
3. **Query is routed** to the relevant backend agent  
4. **Backend agent processes** the request and pulls data  
5. **UI Agent returns** results in an intuitive format  

---

