import streamlit as st
import openai
import os

# Define the CSS to inject
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title('Marketing Strategy and Campaign Generator')

# Read OpenAI API key from environment variable
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    st.error("OpenAI API Key not found in environment variables. Please set the OPENAI_API_KEY environment variable.")
else:
    openai.api_key = openai_key

if openai_key:
    BRAND_NAME = st.text_input("Enter your Brand Name", value="Eco-Friendly Cleaning")
    INDUSTRY = st.text_input("Enter your Industry", value="Cleaning Products")

    question_1 = st.text_input("1. What is the Dilemma? What is the opportunity out there? What is the gap that be filled?",
                               value="The market lacks effective, eco-friendly cleaning products that are affordable and easily accessible.")
    question_2 = st.text_input("2. How will your brand solve the Dilemma? What does the brand promise the consumer?",
                               value="Our brand offers high-quality, eco-friendly cleaning products at competitive prices, ensuring both effectiveness and environmental responsibility.")
    question_3 = st.text_input("3. What products/service do you offer to solve this?",
                               value="We offer a range of cleaning products including all-purpose cleaners, floor cleaners, and specialized cleaners for kitchens and bathrooms.")
    question_4 = st.text_input("4. Why should people believe it? What makes you credible?",
                               value="Our products are certified by leading environmental organizations, and we have received positive reviews from satisfied customers.")
    question_5 = st.text_input("5. What are the trends in the category that inspired you?",
                               value="There is a growing trend towards sustainable living and the use of eco-friendly products as consumers become more environmentally conscious.")

    if st.button('Generate Marketing Strategy and Campaign'):
        if BRAND_NAME and INDUSTRY and question_1 and question_2 and question_3 and question_4 and question_5:
            questionnaire_report = f"""
            Q1: {question_1}
            Q2: {question_2}
            Q3: {question_3}
            Q4: {question_4}
            Q5: {question_5}
            """

            marketing_strategy_template = f"""
            You are a brand called '{BRAND_NAME}', focusing on innovation and leadership within the '{INDUSTRY}' sector. Based on the provided answers
