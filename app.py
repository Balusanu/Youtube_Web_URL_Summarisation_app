import validators
import streamlit as st
from urllib.parse import urlparse, parse_qs

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredURLLoader,
    YoutubeLoader,
)

# --------------------------------------------------
# Streamlit App Config
# --------------------------------------------------
st.set_page_config(
    page_title="LangChain: Summarize Text From YT or Website",
    page_icon="🦜",
    layout="centered",
)

st.title("🦜 LangChain: Summarize Text From YT or Website")
st.subheader("Summarize URL")

# --------------------------------------------------
# Sidebar – API Key & Options
# --------------------------------------------------
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", type="password")
    summary_length = st.selectbox(
        "Summary Length",
        options=["Short", "Medium", "Long"],
        index=0,
    )

# --------------------------------------------------
# Main Input – URL
# --------------------------------------------------
generic_url = st.text_input("URL", label_visibility="collapsed")

# --------------------------------------------------
# Prompt Templates (TOKEN-SAFE)
# --------------------------------------------------
MAP_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
Summarize the following content concisely.

Content:
{text}
"""
)

REDUCE_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
You are combining multiple partial summaries.

Create a final {length} summary using the content below.

Content:
{text}
"""
)

# --------------------------------------------------
# Helper: Clean YouTube URL
# --------------------------------------------------
def clean_youtube_url(url: str) -> str:
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip("/")
        return f"https://www.youtube.com/watch?v={video_id}"

    if "youtube.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

    return url

# --------------------------------------------------
# Button Action
# --------------------------------------------------
if st.button("Summarize the Content from YT or Website"):

    # ------------------------------
    # Input Validation
    # ------------------------------
    if not groq_api_key.strip():
        st.error("❌ Please enter your Groq API key")
        st.stop()

    if not generic_url.strip():
        st.error("❌ Please enter a URL")
        st.stop()

    if not validators.url(generic_url):
        st.error("❌ Please enter a valid YouTube or website URL")
        st.stop()

    try:
        with st.spinner("⏳ Loading content and generating summary..."):

            # ------------------------------
            # Initialize LLM
            # ------------------------------
            llm = ChatGroq(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                groq_api_key=groq_api_key,
                temperature=0.2,
                max_tokens=512,
            )

            # ------------------------------
            # Load Content
            # ------------------------------
            if "youtube.com" in generic_url or "youtu.be" in generic_url:
                safe_url = clean_youtube_url(generic_url)

                loader = YoutubeLoader.from_youtube_url(
                    safe_url,
                    add_video_info=False,
                    language=["en"],
                )
            else:
                loader = UnstructuredURLLoader(
                    urls=[generic_url],
                    ssl_verify=False,
                    headers={"User-Agent": "Mozilla/5.0"},
                )

            docs = loader.load()

            if not docs or not docs[0].page_content.strip():
                st.error("❌ No content found for this URL")
                st.stop()

            # ------------------------------
            # Split Documents (STRICT TOKEN SAFETY)
            # ------------------------------
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1200,
                chunk_overlap=100,
            )

            split_docs = splitter.split_documents(docs)

            # Hard cap to avoid context overflow in map step
            split_docs = split_docs[:20]

            # ------------------------------
            # Map-Reduce Summarization
            # ------------------------------
            chain = load_summarize_chain(
                llm=llm,
                chain_type="map_reduce",
                map_prompt=MAP_PROMPT,
                combine_prompt=REDUCE_PROMPT,
            )

            summary = chain.run({
                "input_documents":split_docs,
                "length":summary_length.lower(),
            })

            # ------------------------------
            # Output
            # ------------------------------
            st.success(summary)

    except Exception as e:
        st.exception(e)
