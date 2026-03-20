import streamlit as st
from supabase import create_client
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup Connections
# This configuration is the most stable for 2026
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="CA Essay Grader", page_icon="🍎")
st.title("🍎 CA Standard Essay Grader")

# 2. PDF Extraction Helper Function
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 3. Sidebar for Settings
with st.sidebar:
    st.header("Grading Settings")
    grade = st.selectbox("Grade Level", ["6th Grade", "7th Grade", "8th Grade", "High School"])
    standard = st.selectbox("Standard Type", ["Argumentative", "Informational", "Narrative"])

# 4. Main Interface
name = st.text_input("Student Name")
uploaded_file = st.file_uploader("Upload Student Essay (PDF)", type=['pdf'])

# 5. The Analysis Engine
if st.button("Analyze Essay"):
    if name and uploaded_file:
        with st.spinner("Teacher AI is reading and grading..."):
            try:
                # Step A: Convert PDF to text
                essay_text = extract_text_from_pdf(uploaded_file)
                
                # Step B: Create the Prompt
                prompt = f"""
                You are a California State Certified English Teacher. 
                Grade this {grade} {standard} essay based on CCSS standards.
                
                Format:
                1. SCORES (1-4): Organization, Evidence, Conventions.
                2. STRENGTHS: What did the student do well?
                3. NEXT STEPS: Two specific ways to improve.
                
                Essay Content: 
                {essay_text}
                """
                
                # Step C: Ask the AI 
                # Using the full 'models/' path to bypass the v1beta 404 error
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                response = model.generate_content(prompt)
                result_text = response.text
                
                # Step D: Show Results
                st.markdown("---")
                st.markdown(f"### Assessment for {name}")
                st.write(result_text)
                
                # Step E: Save to Database
                supabase.table("assessments").insert({
                    "student_name": name,
                    "grade_level": f"{grade} - {standard}",
                    "ai_assessment": result_text
                }).execute()
                
                st.success("Saved to Teacher Dashboard!")

            except Exception as e:
                # This helps us see EXACTLY what is still failing
                st.error(f"AI Error: {e}")
    else:
        st.warning("Please enter a name and upload a PDF.")