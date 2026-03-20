import streamlit as st
from supabase import create_client
import google.generativeai as genai

# Setup
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="CA Essay Grader", page_icon="🍎")
st.title("🍎 CA Standard Essay Grader")

# Inputs
name = st.text_input("Student Name")
grade = st.selectbox("Grade Level", ["6th Grade", "7th Grade", "8th Grade", "High School"])
essay_text = st.text_area("Paste Student Essay Here", height=300)

if st.button("Generate Assessment"):
    if name and essay_text:
        with st.spinner("Analyzing against California State Standards..."):
            # The AI Logic
            model = genai.GenerativeModel('gemini-1.5-pro')
            prompt = f"Grade this {grade} essay based on California Common Core standards. Provide a score and feedback: {essay_text}"
            
            response = model.generate_content(prompt)
            result_text = response.text
            
            # Show result to teacher
            st.markdown("### Assessment Result")
            st.write(result_text)
            
            # Save to Supabase
            supabase.table("assessments").insert({
                "student_name": name,
                "grade_level": grade,
                "ai_assessment": result_text
            }).execute()
            st.success("Saved to Database!")
    else:
        st.warning("Please enter a name and paste an essay.")