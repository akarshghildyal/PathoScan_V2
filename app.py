import streamlit as st
import json, os, re
import pandas as pd
from pathoscan_backend import (
    extract_text_from_pdf,
    process_blood_test_report,
    personalized_chat,
    extract_sections_from_agent_response
)

st.set_page_config(
    page_title="🧬 PathoScan", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def display_json_as_table(json_data, key_col="Parameter", value_col="Value"):
    """Convert JSON to DataFrame and display as table"""
    if isinstance(json_data, list):
        df = pd.DataFrame(json_data)
        st.dataframe(df, use_container_width=True)
    elif isinstance(json_data, dict):
        rows = []
        for k, v in json_data.items():
            if isinstance(v, dict) or isinstance(v, list):
                v = json.dumps(v)
            rows.append({key_col: k, value_col: v})
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

def main():
    st.title("🧬 PathoScan")
    st.markdown("""
    ### AI-powered Blood Test Analysis System
    Upload a blood test report PDF and get insights from an AI agent that analyzes your results,
    identifies potential health issues, and provides lifestyle recommendations.
    """)
    
    with st.sidebar:
        st.header("About PathoScan")
        st.markdown("""
        PathoScan uses an AI agent system to:
        1. 🔬 Analyze blood test parameters
        2. 🧬 Identify potential health issues
        3. 🌱 Provide lifestyle recommendations
        
        **Disclaimer:** This tool is for educational purposes only.
        Always consult with healthcare professionals for medical advice.
        """)

    uploaded_file = st.file_uploader("Upload your blood test report (PDF)", type=["pdf"])

    if uploaded_file:
        with st.spinner("📄 Extracting text from PDF..."):
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            extracted_text = extract_text_from_pdf("temp_uploaded.pdf")
            st.session_state.extracted_text = extracted_text

        st.success("✅ PDF text extracted successfully")
        
        with st.expander("View Extracted Text"):
            st.code(extracted_text)

        st.markdown("---")

        col1, col2 = st.columns([1, 3])
        with col1:
            analyze_button = st.button("🧠 Run Agentic Analysis", use_container_width=True)
        
        if analyze_button:
            with st.status("🔍 Agent working: Analyzing your blood test report...", expanded=True) as status:
                try:
                    agent_response = process_blood_test_report(extracted_text)
                    st.session_state.agent_response = agent_response
                    st.session_state.sections = extract_sections_from_agent_response(agent_response)
                    status.update(label="✅ Analysis complete!", state="complete")
                except Exception as e:
                    st.error(f"Agent execution failed: {str(e)}")
                    status.update(label="❌ Analysis failed", state="error")
                    st.stop()

        if "agent_response" in st.session_state:
            st.markdown("## 📊 Analysis Results")
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "🧪 Blood Test Analysis", 
                "🔬 Health Issues",
                "🌱 Lifestyle Recommendations",
                "📝 Full Report"
            ])
            
            sections = st.session_state.sections
            
            with tab1:
                st.markdown("### Blood Test Analysis")
                if "blood_analysis" in sections:
                    st.markdown(sections["blood_analysis"])
                    if "blood_analysis_json" in sections:
                        with st.expander("View as structured data"):
                            if "abnormal_values" in sections["blood_analysis_json"]:
                                st.subheader("Abnormal Values")
                                display_json_as_table(sections["blood_analysis_json"]["abnormal_values"])
                            else:
                                display_json_as_table(sections["blood_analysis_json"])
                else:
                    st.markdown(st.session_state.agent_response)
            
            with tab2:
                st.markdown("### Health Issues")
                if "health_issues" in sections:
                    st.markdown(sections["health_issues"])
                    if "health_issues_json" in sections:
                        with st.expander("View as structured data"):
                            if "potential_health_issues" in sections["health_issues_json"]:
                                display_json_as_table(sections["health_issues_json"]["potential_health_issues"])
                            else:
                                display_json_as_table(sections["health_issues_json"])
                else:
                    st.markdown("No structured health issues section found.")
            
            with tab3:
                st.markdown("### Lifestyle Recommendations")
                if "lifestyle_recommendations" in sections:
                    st.markdown(sections["lifestyle_recommendations"])
                    if "lifestyle_recommendations_json" in sections:
                        with st.expander("View as structured data"):
                            if "lifestyle_recommendations" in sections["lifestyle_recommendations_json"]:
                                display_json_as_table(sections["lifestyle_recommendations_json"]["lifestyle_recommendations"])
                            else:
                                display_json_as_table(sections["lifestyle_recommendations_json"])
                else:
                    st.markdown("No structured lifestyle recommendations section found.")
            
            with tab4:
                st.markdown("### Full Agent Report")
                st.markdown(st.session_state.agent_response)
            
            st.markdown("---")
            st.markdown("## 💬 Ask Questions About Your Results")
            
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            for i, (role, message) in enumerate(st.session_state.chat_history):
                if role == "user":
                    st.markdown(f"**You:** {message}")
                else:
                    st.markdown(f"**AI:** {message}")
            
            user_question = st.text_input(
                "Ask a question about your blood test results:",
                placeholder="E.g., What do my cholesterol levels mean?",
                key="user_question"
            )
            
            if st.button("Send", use_container_width=True) and user_question:
                st.session_state.chat_history.append(("user", user_question))
                
                with st.spinner("Thinking..."):
                    try:
                        response = personalized_chat(
                            question=user_question,
                            context=extracted_text,
                            report_analysis=st.session_state.agent_response
                        )
                        st.session_state.chat_history.append(("ai", response))
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to answer: {str(e)}")

if __name__ == "__main__":
    main()