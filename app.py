import streamlit as st
import openai
import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.schema import Document

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
            splitted_documents = [
                Document(page_content=question_1, metadata={"id": "q1"}),
                Document(page_content=question_2, metadata={"id": "q2"}),
                Document(page_content=question_3, metadata={"id": "q3"}),
                Document(page_content=question_4, metadata={"id": "q4"}),
                Document(page_content=question_5, metadata={"id": "q5"}),
            ]

            turbo = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0.0, max_tokens=4000, streaming=False)

            embeddings = OpenAIEmbeddings(chunk_size=500)
            marketing_retriever = Chroma.from_documents(splitted_documents, embeddings, collection_name="brand")
            marketing_qa_template = """ the user is a marketing agent and he needs answers to some questions about your brand, the questions, and answers in the below context, so provide the answer to his question from the below context as it is in an accurate way, and don't make up answers or add info to the context answer from your mind.

            ===========================

            {context}

            Question: {question}"""

            MARKETING_PROMPT = PromptTemplate(
                template=marketing_qa_template, input_variables=["context", "question"]
            )
            marketing_qa = RetrievalQA.from_chain_type(
                llm=turbo,
                chain_type="stuff",
                retriever=marketing_retriever.as_retriever(search_kwargs={'k': 1}),
                chain_type_kwargs={"prompt": MARKETING_PROMPT, 'verbose': False},
            )

            questionaire_report = ""
            with st.spinner('Processing your answers...'):
                questionaire_report += "Q1- " + question_1 + "\n" + marketing_qa.invoke(question_1)['result'] + "\n\n"
                questionaire_report += "Q2- " + question_2 + "\n" + marketing_qa.invoke(question_2)['result'] + "\n\n"
                questionaire_report += "Q3- " + question_3 + "\n" + marketing_qa.invoke(question_3)['result'] + "\n\n"
                questionaire_report += "Q4- " + question_4 + "\n" + marketing_qa.invoke(question_4)['result'] + "\n\n"
                questionaire_report += "Q5- " + question_5 + "\n" + marketing_qa.invoke(question_5)['result'] + "\n\n"

            marketing_strategy_template = f"""You are a brand called '{BRAND_NAME}', focusing on innovation and leadership within the '{INDUSTRY}' sector. Based on the provided answers to the questionnaire, generate a detailed marketing strategy and campaign.

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

            Generate the marketing strategy and campaign in a cohesive narrative format."""

            main_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.05, max_tokens=3000, streaming=False)
            response = main_model({"context": questionaire_report, "template": marketing_strategy_template})

            st.write(response["choices"][0]["message"]["content"])
        else:
            st.error("Please fill out all the fields.")
