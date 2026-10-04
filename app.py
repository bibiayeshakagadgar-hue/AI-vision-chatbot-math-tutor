import os
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from streamlit_cropper import st_cropper
import pypdf

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Vision Math Tutor", page_icon="📐", layout="wide")
st.title("📐 AI Vision Math & Homework Tutor")

# ---------------------------------------------------------
# 1. Initialize State & Client
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Check Render Environment Variables first, fallback to Streamlit secrets locally
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please set it in Render Environment Variables or .streamlit/secrets.toml file.")
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# 2. Reset App Control
# ---------------------------------------------------------
col1, col2 = st.columns([0.85, 0.15])
with col2:
    if st.button("🔄 Reset App"):
        st.session_state.chat_messages = []
        st.rerun()

# ---------------------------------------------------------
# 3. File Upload & Pre-Processing
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a handwritten problem (Image or PDF)", 
    type=["png", "jpg", "jpeg", "jfif", "webp", "pdf"]
)

processed_image = None

if uploaded_file is not None:
    if uploaded_file.name.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
        st.info("📄 PDF text extracted successfully.")
    else:
        raw_image = Image.open(uploaded_file).convert("RGB")
        # Downscale image to max 1024px to accelerate payload transmission
        raw_image.thumbnail((1024, 1024))
        
        st.subheader("✂️ Crop to the Specific Equation")
        processed_image = st_cropper(
            raw_image, 
            realtime_update=False,  # Prevents unnecessary re-runs while moving crop box
            box_color='#00FF00', 
            aspect_ratio=None
        )

# ---------------------------------------------------------
# 4. Initial Image Analysis (Streaming)
# ---------------------------------------------------------
if processed_image is not None:
    user_question = st.text_input(
        "Optional question or comment:", 
        placeholder="e.g., I'm stuck on step 2, where did I go wrong?"
    )
    
    if st.button("Analyze & Get Hint"):
        prompt = user_question if user_question else "Please transcribe this problem and help me check my work."
        st.subheader("Tutor Feedback")
        
        collected_chunks = []
        
        for model_name in FAST_MODELS:
            try:
                stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=[processed_image, prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.2
                    )
                )
                
                def stream_generator():
                    for chunk in stream:
                        if chunk.text:
                            collected_chunks.append(chunk.text)
                            yield chunk.text

                st.write_stream(stream_generator)
                break
            except Exception as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    continue
                else:
                    st.error(f"Error: {e}")
                    break

        full_response = "".join(collected_chunks)
        if full_response:
            st.session_state.chat_messages.append({"role": "assistant", "content": full_response})
            st.session_state.history.append({
                "question": prompt,
                "feedback": full_response,
                "image": processed_image
            })

# ---------------------------------------------------------
# 5. Multi-Turn Follow-Up Chat (Streaming)
# ---------------------------------------------------------
if st.session_state.chat_messages:
    st.markdown("---")
    st.subheader("💬 Tutor Conversation")
    
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if follow_up := st.chat_input("Ask a follow-up question..."):
        st.session_state.chat_messages.append({"role": "user", "content": follow_up})
        with st.chat_message("user"):
            st.markdown(follow_up)

        with st.chat_message("assistant"):
            contents = [processed_image, follow_up] if processed_image else [follow_up]
            collected_chat_chunks = []
            
            for model_name in FAST_MODELS:
                try:
                    stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.2
                        )
                    )
                    
                    def chat_stream_generator():
                        for chunk in stream:
                            if chunk.text:
                                collected_chat_chunks.append(chunk.text)
                                yield chunk.text

                    st.write_stream(chat_stream_generator)
                    break
                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        continue
                    else:
                        st.error(f"Error generating response: {e}")
                        break

            full_chat_response = "".join(collected_chat_chunks)
            if full_chat_response:
                st.session_state.chat_messages.append({"role": "assistant", "content": full_chat_response})

# ---------------------------------------------------------
# 6. Sidebar History & Markdown Export
# ---------------------------------------------------------
st.sidebar.header("📜 Tutor Session History")

if st.session_state.history:
    summary_md = "# Vision Math Tutor - Session Summary\n\n"
    for idx, item in enumerate(st.session_state.history, start=1):
        summary_md += f"## Problem #{idx}\n"
        summary_md += f"**User Question:** {item['question']}\n\n"
        summary_md += f"**Tutor Feedback:**\n{item['feedback']}\n\n"
        summary_md += "---\n\n"

    st.sidebar.download_button(
        label="📥 Export Summary (.md)",
        data=summary_md,
        file_name="math_tutor_session_summary.md",
        mime="text/markdown"
    )

    if st.sidebar.button("Clear History"):
        st.session_state.history = []
        st.session_state.chat_messages = []
        st.rerun()

    for idx, item in enumerate(reversed(st.session_state.history)):
        with st.sidebar.expander(f"Problem #{len(st.session_state.history) - idx}"):
            if item["image"]:
                st.image(item["image"], use_container_width=True)
            st.write(f"**Question:** {item['question']}")
            st.write(f"**Feedback:** {item['feedback']}")
else:
    st.sidebar.info("No prior problems in history.")