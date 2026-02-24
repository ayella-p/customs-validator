import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image  # This is the new tool that handles images!

# 1. Load the secret API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. Set up the AI model
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Build the User Interface
st.title("Customs Green Lane Validator")
st.write("Upload the Commercial Invoice and Bill of Lading images to check if they match.")

# Create File Uploaders (Instead of text boxes)
invoice_file = st.file_uploader("Upload Commercial Invoice Image", type=["jpg", "jpeg", "png"])
bol_file = st.file_uploader("Upload Bill of Lading Image", type=["jpg", "jpeg", "png"])

# 4. The Analyze Button
if st.button("Analyze Documents"):
    if invoice_file and bol_file:
        with st.spinner("Checking documents..."):
            
            # Open the uploaded images so the AI can see them
            invoice_img = Image.open(invoice_file)
            bol_img = Image.open(bol_file)
            
            # The Brain: Tell the AI what to do
            prompt = """
            You are a Philippine Customs Document Validator. 
            Look at the attached images of the Commercial Invoice and Bill of Lading.
            
            Tasks:
            1. Extract the 'Consignee Name', 'Total Value' (or Weight), and 'Commodity Description' from both.
            2. Compare them.
            
            Rules:
            - If Consignee names match perfectly and there are no restricted items (like firearms or chemicals), say "🟢 GREEN LANE: Approved".
            - If names mismatch or data is missing, say "🟡 YELLOW LANE: Document Review Required".
            - If there are restricted items, say "🔴 RED LANE: Physical Inspection Required".
            
            Give a short explanation for your decision, showing the extracted data.
            """
            
            # Send the prompt AND the two images to Gemini
            response = model.generate_content([prompt, invoice_img, bol_img])
            
            st.success("Analysis Complete!")
            st.write(response.text)
    else:
        st.warning("Please upload BOTH images first.")