import os
import time
import base64
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# --- SETUP AND CONFIGURATION ---
st.set_page_config(
    page_title="AI Resume Roaster",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables
load_dotenv()

# Configure the Gemini API globally for the module
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- CUSTOM CSS ---
def get_base64_of_bin_file(bin_file):
    if not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def inject_custom_css():
    # Check for bg.jpg or bg.jpg.jpg (in case of accidental double extension)
    bg_path = 'bg.jpg.jpg' if os.path.exists('bg.jpg.jpg') else 'bg.jpg'
    bg_base64 = get_base64_of_bin_file(bg_path)
    bg_css_rule = f"background-image: linear-gradient(rgba(10, 10, 15, 0.8), rgba(10, 10, 15, 0.8)), url('data:image/jpeg;base64,{bg_base64}');" if bg_base64 else "background: linear-gradient(-45deg, #050505, #0a0a0f, #11091a, #0d0f12);"

    st.markdown(f"""
        <style>
        .stApp {{
            {bg_css_rule}
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        /* Hide Streamlit default menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Make header transparent so the toggle button is still clickable */
        header {background: transparent !important;}

        /* Sidebar Toggle Button Styling */
        [data-testid="collapsedControl"] {
            background-color: rgba(168, 85, 247, 0.2) !important;
            border: 1px solid rgba(168, 85, 247, 0.5) !important;
            border-radius: 8px !important;
            box-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
            z-index: 99999 !important;
            transition: all 0.3s ease;
        }
        [data-testid="collapsedControl"]:hover {
            background-color: rgba(168, 85, 247, 0.5) !important;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.8);
            transform: scale(1.05);
        }
        [data-testid="collapsedControl"] svg {
            fill: #ffffff !important;
            color: #ffffff !important;
        }
        
        /* Animated Gradient Background */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .stApp {
            /* Background injected dynamically above */
            color: #e0e6ed;
            font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Typography */
        p, span {
            color: #E2E8F0 !important;
        }

        /* The Central Glass Card */
        [data-testid="block-container"] {
            background: rgba(20, 20, 25, 0.4) !important;
            backdrop-filter: blur(20px) saturate(150%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 24px !important;
            padding: 3rem !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6) !important;
            margin-top: 2rem !important;
        }

        /* Headings */
        h1, h2, h3 {
            color: #ffffff;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        /* Main Title styling */
        .main-title {
            font-size: 4.5rem !important;
            background: -webkit-linear-gradient(45deg, #c084fc, #db2777);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
            text-align: center;
            text-shadow: 0 0 20px rgba(219, 39, 119, 0.5);
        }
        
        .sub-title {
            text-align: center;
            font-size: 1.25rem;
            color: #94a3b8;
            margin-top: 0.5rem;
            margin-bottom: 3rem;
            font-weight: 300;
        }

        /* Glassmorphism for Sidebar */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 15, 15, 0.55) !important;
            backdrop-filter: blur(16px) saturate(120%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(120%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
        }

        /* Glassmorphism for File Uploader */
        .stFileUploader > div > div {
            background-color: rgba(15, 15, 15, 0.55) !important;
            backdrop-filter: blur(16px) saturate(120%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(120%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px;
            padding: 2rem;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
        }
        .stFileUploader > div > div:hover {
            border-color: rgba(168, 85, 247, 0.5) !important;
            background-color: rgba(25, 25, 25, 0.65) !important;
            box-shadow: 0 8px 32px 0 rgba(168, 85, 247, 0.25) !important;
        }

        /* 3D Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #a855f7 0%, #6b21a8 100%);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0.8rem 2rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.15rem;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            width: 100%;
            box-shadow: 0 8px 0 #4c1d95, 0 15px 20px rgba(0, 0, 0, 0.4);
            margin-top: 1rem;
            position: relative;
            top: 0;
        }
        
        .stButton > button:hover {
            top: 2px;
            box-shadow: 0 6px 0 #4c1d95, 0 10px 25px rgba(168, 85, 247, 0.6);
            background: linear-gradient(135deg, #b062fc 0%, #7e22ce 100%);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .stButton > button:active {
            top: 8px;
            box-shadow: 0 0 0 #4c1d95, 0 5px 10px rgba(168, 85, 247, 0.8);
        }
        
        /* Glassmorphism for Alerts/Result Boxes */
        .stAlert > div {
            background-color: rgba(15, 15, 15, 0.55) !important;
            backdrop-filter: blur(16px) saturate(120%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(120%) !important;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
        }
        
        /* Secondary / Download Button Styling */
        .stDownloadButton > button {
            background: rgba(30, 33, 40, 0.6);
            color: #e0e6ed;
            border: 1px solid rgba(168, 85, 247, 0.3);
            padding: 0.6rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            font-size: 1rem;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
        }
        .stDownloadButton > button:hover {
            border-color: rgba(168, 85, 247, 0.8);
            background: rgba(168, 85, 247, 0.1);
            color: white;
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.3);
        }

        </style>
    """, unsafe_allow_html=True)

# --- BACKEND LOGIC ---
def extract_text_from_pdf(pdf_file) -> str:
    """Extracts text content from an uploaded PDF file."""
    if not pdf_file:
        raise ValueError("No PDF file provided.")
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = []
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                text_content.append(text)
        extracted_text = "\n".join(text_content).strip()
        if not extracted_text:
            raise ValueError("The PDF appears to be empty or contains unextractable text.")
        return extracted_text
    except PyPDF2.errors.PdfReadError:
        raise ValueError("Invalid or corrupted PDF file.")
    except Exception as e:
        raise Exception(f"An error occurred while extracting text from the PDF: {e}")

def analyze_resume(text: str, roast_level: str) -> str:
    """Analyzes the resume text using the Gemini API, adjusting tone based on roast_level."""
    if not text or not text.strip():
        raise ValueError("No resume text provided for analysis.")
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

    # Using gemini-2.5-flash to use a fresh quota pool since quotas are per-model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    tone_instruction = {
        "Mild": "Keep the roast very light and constructive. Focus mostly on gentle suggestions rather than harsh criticism.",
        "Brutal": "Make the roast sarcastic, sharp, and brutally honest, but still professional. Highlight cliches and vague statements.",
        "Career-Ending": "Hold nothing back. Completely obliterate the resume. Be absolutely ruthless, hilarious, and merciless about every single flaw."
    }.get(roast_level, "Make the roast sarcastic and brutally honest.")

    prompt = (
        f"You are an elite, highly opinionated tech recruiter. The user has provided their resume text below.\n"
        f"Their selected 'Roast Level' is '{roast_level}'. {tone_instruction}\n\n"
        "I want you to do two things:\n\n"
        "1. 'Roast' the resume based on the selected tone.\n"
        "2. Provide exactly 3 highly actionable, specific bullet points to 'fix' it and make it competitive "
        "for top-tier tech jobs (e.g., FAANG/MAANG).\n\n"
        "IMPORTANT: Strictly format your response into two distinct sections separated by exactly '---DIVIDER---'.\n"
        "The first part should be ONLY the Roast. The second part should be ONLY the 3 Fixes.\n\n"
        "Resume Text:\n"
        "-----------------\n"
        f"{text}\n"
        "-----------------\n"
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            if not response.text:
                raise Exception("Received an empty response from the Gemini API.")
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg and attempt < max_retries - 1:
                # Wait before retrying (exponential backoff)
                wait_time = 15 * (attempt + 1)
                # Note: st.warning here will render in the UI, letting the user know it's handling the wait!
                st.warning(f"⏳ API Rate limit hit. Automatically retrying in {wait_time} seconds (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise Exception(f"An error occurred during resume analysis with the Gemini API: {e}")

def generate_portfolio(text: str) -> str:
    """Generates a complete single-file HTML/CSS portfolio from resume text."""
    if not text or not text.strip():
        raise ValueError("No resume text provided for generation.")
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = (
        "You are an elite frontend developer. Take this resume text and generate a complete, "
        "single-file HTML and CSS portfolio website. The design MUST be a premium, modern dark-theme "
        "with glassmorphism effects, neon-pink subtle glowing accents, and flawless typography. "
        "Include sections for About, Experience, and Skills based ONLY on the provided resume data. "
        "Output ONLY the raw HTML code, nothing else.\n\n"
        "Resume Text:\n"
        "-----------------\n"
        f"{text}\n"
        "-----------------\n"
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            if not response.text:
                raise Exception("Received an empty response from the Gemini API.")
            
            code = response.text.strip()
            if code.startswith("```html"):
                code = code[7:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
                
            return code.strip()
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg and attempt < max_retries - 1:
                wait_time = 15 * (attempt + 1)
                st.warning(f"⏳ API Rate limit hit. Automatically retrying in {wait_time} seconds (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise Exception(f"An error occurred during portfolio generation: {e}")

# --- MAIN UI APPLICATION ---
def main():
    inject_custom_css()
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #c084fc;'>🚀 AI Resume Roaster Pro</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin-top: 0;'>", unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        st.radio("Menu", ["Dashboard", "API Access", "Pricing"], label_visibility="collapsed")
        
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        # Roast Settings
        st.markdown("### ⚙️ Roast Settings")
        roast_level = st.selectbox(
            "Roast Level",
            options=["Mild", "Brutal", "Career-Ending"],
            index=1,
            help="Choose how aggressively the AI will tear apart your resume."
        )
        
        st.markdown("<div style='margin-top: 50px; text-align: center; color: #64748b; font-size: 12px;'>v1.0.0 - Premium Tier</div>", unsafe_allow_html=True)

    # --- MAIN CONTENT ---
    st.markdown("<h1 class='main-title'>AI Resume Roaster</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Upload your PDF. Get brutally honest feedback. Land the job.</p>", unsafe_allow_html=True)

    # Layout with columns to center the main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # File Uploader
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf"], help="Only PDF files are supported.")
        
        if uploaded_file is not None:
            if st.button("🔥 Roast My Resume"):
                try:
                    with st.spinner("Extracting text and summoning the elite recruiter..."):
                        # 1. Extract Text
                        resume_text = extract_text_from_pdf(uploaded_file)
                        st.session_state['resume_text'] = resume_text
                        
                        # 2. Analyze
                        time.sleep(0.5) # Slight delay for smooth UI transition feel
                        st.session_state['analysis_result'] = analyze_resume(resume_text, roast_level)
                except ValueError as ve:
                    st.error(f"Validation Error: {ve}", icon="⚠️")
                except Exception as e:
                    st.error(f"System Error: {e}", icon="❌")
            
            # Display results if available in session state
            if 'analysis_result' in st.session_state:
                analysis_result = st.session_state['analysis_result']
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Parse the result into Roast and Fixes
                if "---DIVIDER---" in analysis_result:
                    roast_text, fixes_text = analysis_result.split("---DIVIDER---", 1)
                    
                    # Display Roast in error/warning box
                    st.error("### 🔥 The Roast\n\n" + roast_text.strip(), icon="🚨")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display Fixes in success/green box
                    st.success("### 🛠️ Actionable Fixes\n\n" + fixes_text.strip(), icon="✅")
                    
                    report_content = f"# AI Resume Roaster Report\n\n## 🔥 The Roast\n\n{roast_text.strip()}\n\n## 🛠️ Actionable Fixes\n\n{fixes_text.strip()}"
                else:
                    # Fallback if the AI didn't follow the exact formatting
                    st.warning(analysis_result)
                    report_content = f"# AI Resume Roaster Report\n\n{analysis_result}"
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Download Button
                st.download_button(
                    label="📥 Download Full Report",
                    data=report_content,
                    file_name="Resume_Roast_Report.md",
                    mime="text/markdown"
                )
                
                # --- PORTFOLIO BUILDER ---
                st.divider()
                st.subheader("🚀 Level Up: Instant Portfolio Builder")
                
                if st.button("Generate My Portfolio Website Code"):
                    try:
                        with st.spinner("Coding your premium portfolio..."):
                            if 'resume_text' in st.session_state:
                                r_text = st.session_state['resume_text']
                            else:
                                uploaded_file.seek(0)
                                r_text = extract_text_from_pdf(uploaded_file)
                                st.session_state['resume_text'] = r_text
                                
                            portfolio_code = generate_portfolio(r_text)
                            st.session_state['portfolio_code'] = portfolio_code
                    except Exception as e:
                        st.error(f"System Error: {e}", icon="❌")
                        
                if 'portfolio_code' in st.session_state:
                    st.success("✅ Premium Portfolio successfully generated!")
                    st.code(st.session_state['portfolio_code'], language='html')

if __name__ == "__main__":
    main()
