import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()

st.set_page_config(
    page_title="Fashion Style Advisor",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #FF3131;
    }
    .suggestion-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #333;
    }
    .section-content {
        margin-left: 1rem;
        line-height: 1.6;
    }
    .section-item {
        margin-bottom: 0.5rem;
        display: flex;
        align-items: flex-start;
    }
    .section-item:before {
        content: "•";
        margin-right: 0.5rem;
        color: #FF4B4B;
    }
    .stImage > img {
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please create a .env file with your GEMINI_API_KEY")
    st.stop()

genai.configure(api_key=api_key)

def initialize_model():
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192
        }
    )

def analyze_image(image_data, model):
    chat = model.start_chat(history=[])
    img_byte_arr = io.BytesIO()
    image_data.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    content_parts = [
        """Analyze this image and provide styling suggestions in the following format:

        🎯 OUTFIT COMBINATIONS
        - [Detail combinations with emojis]

        👔 OCCASIONS
        - [List suitable occasions]

        🎨 COLOR COORDINATION
        - [Suggest color matches]

        ✨ ACCESSORIES
        - [Recommend accessories]

        If not a clothing image or person with the style, kindly request a fashion/clothing image instead.
        """,
        {"mime_type": "image/jpeg", "data": img_byte_arr}
    ]
    
    response = chat.send_message(content_parts)
    return response.text

def format_suggestions(text):
    # Split the response into sections
    sections = text.lower().split('\n\n')
    formatted_sections = []
    
    for section in sections:
        if not section.strip():
            continue
            
        if '🎯 outfit combinations' in section.lower():
            title = '🎯 Outfit Combinations'
            content = section.split('\n', 1)[1] if '\n' in section else ''
        elif '👔 occasions' in section.lower():
            title = '👔 Occasions'
            content = section.split('\n', 1)[1] if '\n' in section else ''
        elif '🎨 color coordination' in section.lower():
            title = '🎨 Color Coordination'
            content = section.split('\n', 1)[1] if '\n' in section else ''
        elif '✨ accessories' in section.lower():
            title = '✨ Accessories'
            content = section.split('\n', 1)[1] if '\n' in section else ''
        else:
            continue

        items = [item.strip() for item in content.split('\n') if item.strip()]
        items_html = '\n'.join([f'<div class="section-item">{item}</div>' for item in items])
        
        formatted_section = f"""
        <div class="suggestion-box">
            <div class="section-title">{title}</div>
            <div class="section-content">
                {items_html}
            </div>
        </div>
        """
        formatted_sections.append(formatted_section)
    
    return '\n'.join(formatted_sections)

def main():
    st.markdown("<h1>✨ Fashion Style Advisor</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <p style='text-align: center; color: #666; margin-bottom: 2rem;'>
        Upload a clothing image to get personalized styling suggestions
        </p>
    """, unsafe_allow_html=True)
    
    model = initialize_model()
    
    uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns([1, 1])
        
        with col1:

            st.image(image, caption="", use_column_width=True)
        
        if st.button("✨ Get Style Suggestions"):
            with st.spinner("🎨 Analyzing your image..."):
                try:
                    analysis = analyze_image(image, model)
                    with col2:
                        st.markdown(format_suggestions(analysis), unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()