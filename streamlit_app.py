import streamlit as st
from supabase import create_client
import google.generativeai as genai
from pypdf import PdfReader

# 1. Setup Connections
# These pull from your .streamlit/secrets.toml file
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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
                
                # Step B: Create the Prompt (The "Instructions" for the AI)
                prompt = f"""
                You are a California State Certified English Teacher. 
                Grade this {grade} {standard} essay based on CCSS standards.
                
                Provide the assessment in this format:
                1. SCORES (1-4) for: Organization, Evidence/Analysis, and Conventions.
                2. STRENGTHS: What did the student do well?
                3. NEXT STEPS: Two specific ways to improve based on CCSS.
                
                Essay Content: 
                {essay_text}
                """
                
                # Step C: Ask the AI (The "Brain" part)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt)
                result_text = response.text
                
                # Step D: Show Results on Screen
                st.markdown("---")
                st.markdown(f"### Assessment for {name}")
                st.write(result_text)
                
                # Step E: Save to Supabase Database
                supabase.table("assessments").insert({
                    "student_name": name,
                    "grade_level": f"{grade} - {standard}",
                    "ai_assessment": result_text
                }).execute()
                
                st.success("Successfully saved to your Teacher Dashboard!")

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a name and upload a PDF.")