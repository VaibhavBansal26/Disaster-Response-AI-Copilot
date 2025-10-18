# Disaster Response Starter Pack

This bundle contains:
- `data/events.csv` — sample incidents (map these in your Streamlit dashboard).
- `data/events_train.csv` — labeled samples for training a tiny severity classifier in Azure ML.
- `docs/*.txt` — guidance documents for RAG grounding in Azure AI Foundry (you can upload as-is or print to PDF).

## How to use

### In Azure AI Foundry (Agent)
1. Create an Agent.
2. Upload the files from `docs/` to your Project.
3. Enable **File Search** tool.
4. (Later) Add **Azure AI Search** for better retrieval if you build a search index.

### In Streamlit
- Read `data/events.csv` and plot latitude/longitude on a map.
- Add a form to submit a new incident; send text to your Agent.
- Show citations in the chat answers.

### In Azure ML (optional for Phase 3)
- Use `data/events_train.csv` to train a small classifier that predicts priority and category.
- Deploy as a REST endpoint and register it as a tool in your Agent.
