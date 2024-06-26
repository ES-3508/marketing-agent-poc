import streamlit as st
import openai
import os

# Define the CSS to inject
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.title('Marketing Strategy and Campaign Generator')

openai_key = st.text_input("Enter your OpenAI API Key", type="password")
if st.button('Confirm API Key'):
    if openai_key:
        st.session_state['openai_key'] = openai_key
        st.session_state['key_confirmed'] = True
        st.success('API Key confirmed. Please proceed.')
        os.environ["OPENAI_API_KEY"] = st.session_state['openai_key']
        openai.api_key = st.session_state['openai_key']
    else:
        st.error("Please enter the OpenAI key to proceed.")

if st.session_state.get('key_confirmed', False):
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
            You are a brand called '{BRAND_NAME}', focusing on innovation and leadership within the '{INDUSTRY}' sector. Based on the provided answers to the questionnaire, generate a detailed marketing strategy and campaign.

            1. **Brand Insights**: Analyze the market dilemma, solutions, product offerings, and credibility. Identify core opportunities and how the brand differentiates itself.
            2. **Competitor Analysis**: Examine main competitors, their strengths, weaknesses, and market positions. Highlight the brand's competitive advantage.
            3. **Target Audience**: Define primary and secondary target audiences based on the demographics and psychographics. Outline strategies for engaging these audiences.
            4. **Marketing Strategy**:
                - **Brand Positioning**: Summarize the brand's market position and unique value proposition.
                - **Engagement Channels**: Identify the most effective channels for reaching the target audience.
                - **Content and Messaging**: Suggest key messages that resonate with the brand promise and audience's expectations.
            5. **Campaign Concept**: Propose a campaign that embodies strategic goals, including creative titles, objectives, key activities, and expected outcomes.
            6. **Implementation Plan**: Outline steps for executing the marketing strategy and campaign, including timelines and key milestones.
            7. **Evaluation Metrics**: Specify how to measure the success of the marketing strategy and campaign.

            Generate the marketing strategy and campaign in a cohesive narrative format.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": marketing_strategy_template},
                    {"role": "user", "content": questionnaire_report}
                ]
            )

            st.write(response['choices'][0]['message']['content'])
        else:
            st.error("Please fill out all the fields.")
