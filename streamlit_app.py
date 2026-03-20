import streamlit as st
from supabase import create_client
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="CA Essay Grader", page_icon="🍎")
st.title("🍎 CA Standard Essay Grader")

# 2. PDF Extraction Helper
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 3. Sidebar / Inputs
with st.sidebar:
    st.header("Settings")
    grade = st.selectbox("Grade Level", ["6th Grade", "7th Grade", "8th Grade", "High School"])
    standard = st.selectbox("Standard", ["Argumentative", "Informational", "Narrative"])

name = st.text_input("Student Name")
uploaded_file = st.file_uploader("Upload Student Essay (PDF)", type=['pdf'])

# 4. Processing
if st.button("Analyze Essay"):
    if name and uploaded_file:
        with st.spinner("Reading PDF and grading..."):
            # Step A: Convert PDF to text
            essay_text = extract_text_from_pdf(uploaded_file)
            
            # Step B: AI Assessment
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # This prompt is "Expert Level" for CA Standards
            prompt = f"""
            You are a California State Certified English Teacher. 
            Grade this {grade} {standard} essay.
            
            Provide the assessment in this format:
            1. SCORES (1-4) for: Organization, Evidence/Analysis, and Conventions.
            2. STRENGTHS: What did the student do well?
            3. NEXT STEPS: Two specific ways to improve based on CCSS.
            
            Essay Content: {essay_text}
            """
            
            response = model.generate_content(prompt)
            result_text = response.text
            
            # Step C: Show Results
            st.markdown("---")
            st.markdown(f"### Assessment for {name}")
            st.write(result_text)
            
            # Step D: Save to Supabase
            supabase.table("assessments").insert({
                "student_name": name,
                "grade_level": f"{grade} - {standard}",
                "ai_assessment": result_text
            }).execute()
            
            st.success("Successfully saved to your Teacher Dashboard!")
    else:
        st.warning("Please enter a student name and upload a PDF file.")