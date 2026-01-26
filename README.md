# 🛡️ Fiscal Sentinel

**The AI Financial Bodyguard that fights corporate bureaucracy for you.**

Fiscal Sentinel is an autonomous agent that protects users from predatory financial practices. It connects to bank data, identifies "traps" (like hidden fees, price hikes, or unused subscriptions), and actively drafts legal dispute letters to resolve them.

## 🚀 Features

* **Threat Detection:** Automatically scans transaction history for anomalies (e.g., a Netflix subscription that increased by $3 without notice).
* **Legal RAG Brain:** Uses **Retrieval Augmented Generation (RAG)** to search actual PDF laws (FTC Rules, Banking Agreements) to justify its disputes.
* **Auto-Drafting:** Generates formal, legally-sound cancellation or dispute letters ready for the user to sign.
* **Safety Evaluation:** Integrated with **Opik** to track agent performance and ensure compliant, safe financial advice.

## 🛠️ Tech Stack

* **Frontend:** Streamlit (Python)
* **Backend:** FastAPI & Python
* **AI Model:** OpenAI GPT-4o (via API)
* **Knowledge Base:** ChromaDB (Vector Store) + PyPDF
* **Evaluation:** Opik (by Comet) for Tracing & Metrics
* **Data Source:** Mock Plaid Transaction Data

## 📂 Project Structure

```bash
fiscal-sentinel/
├── app/
│   ├── agent/          # OpenAI Logic & Prompts
│   ├── data/           # Mock Data & Vector DB
│   └── evaluation/     # Opik Metrics & Experiments
├── frontend/           # Streamlit UI
├── main.py             # FastAPI Backend
└── requirements.txt    # Dependencies


##⚡ Getting Started
### 1. Clone the Repository
```Bash

git clone [https://github.com/Olajcodes/fiscal-sentinel](https://github.com/Olajcodes/fiscal-sentinel.git)
cd fiscal-sentinel
```

### 2. Set up Environment
Create a .env file in the root directory and add your keys:
```Bash

OPENAI_API_KEY=sk-proj-....
OPIK_API_KEY=.... 
```

### 3. Install Dependencies
```Bash

pip install -r requirements.txt
```

### 4. Ingest Legal Data (Build the Brain)
Before running the app, you need to parse the PDF documents into the vector database:

```Bash

python app/data/vector_db.py 
```
Make sure you have PDFs inside app/data/documents/.

### 5. Run the Application
You need two terminal windows:

Terminal 1 (Backend):

```Bash

python main.py
```

Terminal 2 (Frontend):

```Bash

streamlit run frontend/ui.py
```

### 🧪 Evaluation (Opik)
To run the safety evaluation suite and see the agent's scores:

```Bash

python run_experiment.py
```

Check your Opik Dashboard to see the LegalComplianceScore for each test case.

## 🔮 Roadmap (Upcoming Features)

We are actively working on Version 2.0 for the final hackathon submission:

* **UI Migration:** Moving from Streamlit to a **Next.js/React** dashboard for a polished user experience.
* **Advanced Agentic Loops:** Implementing multi-turn reasoning where the agent can "negotiate" back-and-forth scenarios.
* **Expanded Datasets:** Increasing the test coverage to include credit card fraud detection and insurance claim disputes.

### 📄 License
MIT