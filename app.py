import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import re

# Import the function from your other file
# Ensure panels.py exists in the same directory
from panels import comparrisonPanel

# 1. Load the secret API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# 2. Set up the AI model
try:
    # Using 1.5-flash as it is the most stable for production OCR in 2026
    model = genai.GenerativeModel('gemini-2.5-flash') 
except Exception as e:
    st.error(f"Model setup failed: {e}")

# 3. Build the User Interface
st.set_page_config(page_title="Customs Validator", page_icon="🚢", layout="wide")

# Sidebar for branding and settings
with st.sidebar:
    st.title("🚢 BOC Validator")
    st.info("System Version: 2026.1.0 (AI-Audit)")
    st.markdown("---")
    input_mode = st.radio("Input Method:", ["Camera (Mobile/Live)", "Upload (File)"])

st.title("🚢 Customs Green Lane Validator")
st.subheader("Philippine Port Authority - AI Document Audit")

# --- STEP A: Input Selection ---
invoice_file = None
bol_file = None

col_input1, col_input2 = st.columns(2)

with col_input1:
    if input_mode == "Camera (Mobile/Live)":
        invoice_file = st.camera_input("📷 Scan Commercial Invoice", key="cam_inv")
    else:
        invoice_file = st.file_uploader("📂 Upload Invoice", type=['png', 'jpg', 'jpeg'], key="up_inv")

with col_input2:
    if input_mode == "Camera (Mobile/Live)":
        bol_file = st.camera_input("📷 Scan Bill of Lading", key="cam_bol")
    else:
        bol_file = st.file_uploader("📂 Upload BoL", type=['png', 'jpg', 'jpeg'], key="up_bol")

# --- STEP B: Analysis Logic ---
if invoice_file and bol_file:
    # Pre-analysis Previews
    prev1, prev2 = st.columns(2)
    with prev1:
        st.image(invoice_file, caption="Invoice Preview", use_container_width=True)
    with prev2:
        st.image(bol_file, caption="BoL Preview", use_container_width=True)

    if st.button("🚀 Run Customs Analysis", type="primary"):
        with st.spinner("AI is examining documents and checking PH Customs regulations..."):
            try:
                invoice_img = Image.open(invoice_file)
                bol_img = Image.open(bol_file)
                
                # We ask the AI to provide a 'Data Block' at the end for our Panel
                prompt = """
                Role: Philippine Customs Document Auditor.
                Analyze the Commercial Invoice and Bill of Lading (BoL).
                
                AUDIT RULES:
                1. Check if Consignee names match (Allow for minor abbreviations).
                2. Weight Tolerance: Allow <3% difference between documents.
                3. Search for restricted keywords: Firearms, explosive, chemical, narcotic, used clothing (Ukay-ukay).
                4. Extract HS Codes if visible.
                
                FORMAT FOR REPORT:
                ## [LANE COLOR]
                - **Consignee:** [Match/Mismatch Detail]
                - **Weight/Value:** [Inv Weight] vs [BoL Weight]
                - **HS Code/Commodity:** [Detected category]
                - **Risk Assessment:** [Short note]

                CRITICAL: At the very end of your response, add this exact block:
                ---
                FINAL_SCORE: [Number 0-100]
                FINAL_LANE: [GREEN/YELLOW/RED]
                """
                
                response = model.generate_content([prompt, invoice_img, bol_img])
                full_text = response.text
                
                # --- NEW: DEFINE FINDINGS BEFORE USE ---
                # Split text into lines to create a list of points
                analysis_points = full_text.split("\n")
                # Filter to keep only lines with bullets or bold text for a cleaner panel
                clean_findings = [line for line in analysis_points if "**" in line or "-" in line]
                
                # --- DATA EXTRACTION FOR PANEL ---
                score = 50
                lane = "YELLOW"
                
                try:
                    score_match = re.search(r"FINAL_SCORE:\s*(\d+)", full_text)
                    lane_match = re.search(r"FINAL_LANE:\s*(\w+)", full_text)
                    
                    if score_match: score = int(score_match.group(1))
                    if lane_match: lane = lane_match.group(1).upper()
                except:
                    pass 

                # --- DISPLAY THE SEPARATE PANEL ---
                st.markdown("---")
                # Now analysis_points and clean_findings are defined and ready!
                comparrisonPanel(score=score, status=lane, findings_list=clean_findings)
                
                # Display the full detailed report below the panel
                #st.markdown(full_text.split("---")[0]) 
                
                if "GREEN" in lane:
                    st.balloons()

            except Exception as e:
                st.error(f"Critical Error: {e}")
else:
    st.info("💡 Please provide both an Invoice and a Bill of Lading to begin validation.")