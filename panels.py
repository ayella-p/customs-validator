import streamlit as st

def comparrisonPanel(score, status, findings_list):
    with st.container(border=True):
        st.subheader("📊 Document Comparison Result")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Match Confidence", value=f"{score}%", delta=f"{score-100}%")
        with col2:
            emoji = "🟢" if "GREEN" in status.upper() else "🟡" if "YELLOW" in status.upper() else "🔴"
            st.metric(label="Assigned Lane", value=f"{emoji} {status}")
        with col3:
            st.metric(label="Audit Status", value="Verified" if score > 90 else "Review Required")

        st.progress(score / 100)
        
        with st.expander("See Detailed Mismatch Analysis"):
            for item in findings_list:
                st.write(item)