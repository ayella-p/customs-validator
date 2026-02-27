import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import re

# Import your custom component from panels.py
from panels import comparrisonPanel

# 1. Setup API Configuration
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# 2. Initialize the Model
try:
    model = genai.GenerativeModel('gemini-2.5-flash') 
except Exception as e:
    st.error(f"Model setup failed: {e}")

# 3. UI Configuration
st.set_page_config(page_title="PH Customs Validator", page_icon="🚢", layout="wide")

with st.sidebar:
    st.title("BOC Validator")
    st.info("System Version: 2026.1.0 (AI-Audit)")
    st.markdown("---")
    input_mode = st.radio("Input Method:", ["Camera (Mobile/Live)", "Upload (File)"])

st.title("Customs Green Lane Validator")
st.subheader("Philippine Port Authority - AI Document Audit")

# --- STEP A: File Inputs ---
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
    prev1, prev2 = st.columns(2)
    with prev1:
        st.image(invoice_file, caption="Invoice Preview", use_container_width=True)
    with prev2:
        st.image(bol_file, caption="BoL Preview", use_container_width=True)

    if st.button("🚀 Run Customs Analysis", type="primary"):
        with st.spinner("AI is auditing documents..."):
            try:
                invoice_img = Image.open(invoice_file)
                bol_img = Image.open(bol_file)
                
                prompt = """
                Role: Philippine Customs Document Auditor.
                Analyze the Commercial Invoice and Bill of Lading (BoL).
                
                AUDIT RULES:
                1. Check if Consignee names match.
                2. Weight Tolerance: Match weights.
                3. Check HS Codes.
                
                FORMAT FOR REPORT:
                - **Consignee:** [Match/Mismatch Detail]
                - **Weight/Value:** [Inv Weight] vs [BoL Weight]
                - **HS Code/Commodity:** [Detected category]
                - **Risk Assessment:** [Short note]

                CRITICAL: At the very end of your response, add this exact block:
                ---
                FINAL_SCORE: [Number 0-100]
                FINAL_LANE: [GREEN/YELLOW/RED]
                
                If the images are NOT an Invoice or BoL (e.g. a person, a research paper, or a blank page), 
                state "I cannot perform the audit" and set FINAL_LANE: RED and FINAL_SCORE: 0.
                """
                
                response = model.generate_content([prompt, invoice_img, bol_img])
                full_text = response.text
                
                # --- STEP C: PARSING ---
                analysis_block = full_text.split("---")[0].strip()
                clean_findings = [line.strip() for line in analysis_block.split('\n') if line.strip()]
                
                # Initialize default values
                score = 0
                lane = "RED"

                # Improved Logic: Only look for scores if the AI actually found documents
                if "cannot perform the audit" not in full_text.lower():
                    score_match = re.search(r"FINAL_SCORE:\s*(\d+)", full_text)
                    lane_match = re.search(r"FINAL_LANE:\s*(\w+)", full_text)
                    
                    if score_match: 
                        score = int(score_match.group(1))
                    if lane_match: 
                        lane = lane_match.group(1).upper()

                # --- STEP D: PASS TO PANEL ---
                st.markdown("---")
                comparrisonPanel(score=score, status=lane, findings_list=clean_findings)
                
                if "GREEN" in lane:
                    st.balloons()

            except Exception as e:
                st.error(f"Analysis failed: {e}")
else:
    st.info("💡 Please provide both an Invoice and a Bill of Lading to begin.")