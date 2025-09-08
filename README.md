# Agentic AI – Hands-On

<details>
<summary>📅 Day 1</summary>

## ✅ Day 1 Activities
- Discussed **Cloud vs Local models**
- Called the **Ollama API** using `curl`
- Called the **OpenAI API** using `curl`
- Created the framework from scratch
- Successfully ran the `agents.testcase_agent`

## 💡 Prerequisites
Before running the agent, set up the environment:

```bash
python -m venv venv
pip install -r requirements.txt
python -m src.agents.testcase_agent --input data/requirements/login.txt
```

##  🚀  Output
![Project Screenshot](./images/day1.1.png)

## CMD-compatible curl command to test Ollama

```
curl http://localhost:11434/api/generate -d "{ \"model\": \"mistral:latest\", \"prompt\": \"Explain what is regression testing in simple terms.\", \"raw\": true, \"stream\": false }"
```

![Project Screenshot](./images/day1.2.png)


### Assignment for edgecase_agent is completed

![Project Screenshot](./images/day1.3.png)

</details>

---

<details>
<summary>📅 Day 2</summary>

### ✅ Key Learnings
- Log Analyzer AI Agent


### 🚀 Hands-on
```
python -m src.agents.log_analyzer --inputs data/log/app_startup_short.log
```
![Project Screenshot](./images/day2.1.png)



### 💡 Notes
- 

</details>

---

<details>
<summary>📅 Day 3</summary>

### ✅ Key Learnings
- Log Analyzer AI Agent with Logging

### 🚀 Hands-on
- 
![Project Screenshot](./images/day2.2.png)

### 💡 Notes
- 

</details>

---

<details>
<summary>📅 Day 4</summary>

### ✅ Key Learnings
- 

### 🚀 Hands-on
- 


### 💡 Notes
- 

</details>
