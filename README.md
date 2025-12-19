# 🦜 LangChain: Summarize Text from YouTube or Website

A Streamlit app that leverages **LangChain** and **Groq LLM** to summarize content from YouTube videos or any web page. This project demonstrates token-efficient summarization using text splitting and map-reduce chains.

---

## Features

- Input any **YouTube URL** or **web page URL**.
- Generate **Short, Medium, or Long** summaries.
- Uses **Groq LLM** (`meta-llama/llama-prompt-guard-2-86m`) for safe token usage.
- Splits long content into smaller chunks to prevent context overflow.
- Provides concise summaries using a **Map-Reduce summarization chain**.

---

## Installation
1. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Enter your **Groq API key** in the sidebar.
3. Select **summary length**: Short, Medium, or Long.
4. Paste a **YouTube or web page URL**.
5. Click **"Summarize the Content from YT or Website"**.
6. View the generated summary in the main panel.

---

## Folder Structure

```
langchain-summarizer/
│
├─ app.py                  # Main Streamlit app
├─ requirements.txt        # Python dependencies
├─ README.md               # Project documentation
└─ .streamlit/
   └─ config.toml          # Streamlit cloud configuration
```

---

## Notes

* Groq API has **token limits**, so very long content may need truncation.
* Supports primarily **English content**.
* Designed for **token-efficient summarization** with map-reduce chains.
* Provides error handling for invalid URLs or empty content.

---

## License

This project is open-source and free to use under the **MIT License**.
