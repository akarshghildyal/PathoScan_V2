<div align="center">
  <h1>
    PathoScan 🧪
  </h1>
</div>

<p align="center">
  <a href="https://streamlit.io">
    <img src="https://img.shields.io/badge/Streamlit-App-purple?logo=streamlit" alt="Streamlit App"/>
  </a>
  <a href="https://openrouter.ai">
    <img src="https://img.shields.io/badge/Powered%20by-OpenRouter-blue?logo=openai" alt="OpenRouter Powered"/>
  </a>
  <a href="https://youtu.be/Cc8aVHSB5MA">
    <img src="https://img.shields.io/badge/Watch-Demo-red?logo=youtube" alt="Demo"/>
  </a>
</p>

---
<div align="center">
  <img src="https://github.com/user-attachments/assets/c92e643a-a28c-45a7-a721-f10f619c138f" alt="PathoScan Logo" style="width: 250px; max-width: 250px;">
</div>


## 🌱 Why I Built This

Last June, I got my blood test done. Like many people, I received a dense report full of medical jargon and numbers that didn’t mean much to me. I wanted to understand the abnormalities, see what values were connected, and learn what it meant for my body — but in simple language.

That experience led me to create **PathoScan** — a tool to help *anyone* turn medical pathological data into simple to understand report.

---

## 🧠 What is PathoScan?

**PathoScan** is an intelligent blood test analyzer powered by AI. Upload your blood test report, and let it:
- 🧪 **Analyze abnormal values** in your test
- 🩺 **Identify potential health issues**
- 🌿 **Recommend lifestyle changes** based on the data

It’s built using [Streamlit](https://streamlit.io), [LangChain](https://www.langchain.com), and [OpenRouter](https://openrouter.ai) models working together in an **agentic workflow**.

---

## 📽️ Demo

> [*PathoScan_V2*](https://youtu.be/Cc8aVHSB5MA)

---

## 🤖 Behind the Scenes

PathoScan uses a modular, agent-based architecture with 3 core tools:

| Tool | Purpose |
|------|---------|
| `BloodTestAnalyzer` | Extracts and explains abnormal values |
| `HealthIssueIdentifier` | Maps findings to possible health conditions |
| `LifestyleAdvisor` | Recommends simple lifestyle improvements |

The agent evaluates your input and calls each tool only when relevant. All outputs are structured, readable, and optionally extracted as JSON for further use.

---

## 💬 AI Chatbot Assistant

Once your report is analyzed, you can **chat directly with an AI assistant** that knows your blood test insights.

### How it works:
- The chatbot is **context-aware** — it has access to your test insights (blood abnormalities, issues, recommendations).
- Ask follow-up questions like:
  - “What does high LDL mean for me?”
  - “What should I eat to improve liver health?”
  - “Are these thyroid results serious?”

It's a powerful way to get *tailored* answers in natural language — all within your browser.

---

## 🚀 How to Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/akarshghildyal/pathoscan_v2.git
cd pathoscan_v2
```


### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your OpenRouter API key
Create a .env file in the project root with the following content:
```bash
OPENROUTER_API_KEY=your_openrouter_key
```
### 4. Launch the app
```bash
streamlit run app.py
```



## ✅ Features
- Supports standard PDF blood test reports

- Clean, simple Streamlit UI

- Easy-to-understand explanations

- Privacy-first: No data is stored or sent anywhere

- Built-in chatbot for contextual queries

----

### Made with ❤️ to bring clarity to your health.
