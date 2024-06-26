import streamlit as st
import os
import openai

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.schema import Document
from langchain.agents.tools import Tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub

# Define the CSS to inject
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Reduced list of questions
questions = [
    "What is the Dilemma? What is the opportunity out there? What is the gap that be filled?",
    "How will your brand solve the Dilemma? What does the brand promise the consumer?",
    "What products/service do you offer to solve this?",
    "Why should people believe it? What makes you credible?",
    "What are the demographics/psychographics of your audience?"
]

st.title('Marketing Strategy and Campaign Generator')

# Tips section
st.header("Tips for Answering Questions")
st.markdown("""
- **Be Clear and Concise**: Provide straightforward and detailed answers.
- **Provide Examples**: When possible, include examples to support your answers.
- **Focus on the Unique Value**: Highlight what makes your brand or product unique.
- **Think About Your Audience**: Consider the demographics and psychographics of your audience when answering.
""")

openai_key = st.text_input("Enter your OpenAI API Key", type="password")
splitted_documents = []
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
    BRAND_NAME = st.text_input("Enter your Brand Name")
    INDUSTRY = st.text_input("Enter your Industry")

    # Input fields for each question
    document_content = []
    for question in questions:
        answer = st.text_area(question)
        if answer:
            document_content.append((question, answer))

    if st.button('Generate Marketing Strategy and Campaign'):
        if document_content and BRAND_NAME and INDUSTRY:
            for i, (question, answer) in enumerate(document_content):
                doc_id = f"doc_{i}"
                splitted_documents.append(
                    Document(page_content=question + "\n" + answer + "\n\n", metadata={"id": doc_id}))

            if not splitted_documents:
                st.error("No documents found. Please ensure all questions are answered.")
            else:
                turbo = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0.0, max_tokens=4000, streaming=False)
                main_model = ChatOpenAI(model="gpt-4", temperature=0.05, max_tokens=1000, streaming=False)

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
                with st.spinner('Processing answers...'):
                    for i, q_a in enumerate(document_content):
                        questionaire_report += f"Q{i + 1}- " + q_a[0] + "\n" + marketing_qa.invoke(q_a[0])[
                            'result'] + "\n\n"

                prompt = hub.pull("hwchase17/openai-tools-agent")

                tools = [Tool(name="brand_answers", func=lambda q: str(marketing_qa({"query": q})['result']),
                              description="You must use it to get info about the brand that you'll create a marketing strategy for it.",
                              handle_tool_error=True)]

                prompt.messages[
                    0].prompt.template = f"""Upon receiving the command "start", you, as the specialized scout for '{BRAND_NAME}' in the '{INDUSTRY}', are tasked with a crucial mission. Without needing further input, you will autonomously navigate through two pivotal phases to develop a comprehensive market report. Your journey unfolds as follows:

                        - Automatically invoke the "brand_answers" tool to ask the following questions:
                        1. What products/service do you offer?
                        2. Who are your main competitors?

                        Main answer and final report: Conducting In-depth Market Analysis
                        - With the key information in hand, utilize the "brand_answers" tool one time for each step to delve into:
                        1. Current market trends and analysis within the '{INDUSTRY}', identifying opportunities and threats.
                        2. Detailed information of each competitor (maximum 3 competitors or less) (search for one competitor at a time) (put `company` after the company name), revealing potential advantages for '{BRAND_NAME}'.
                        3. Detailed strengths and weaknesses of each competitor (maximum 3 competitors or less) (search for one competitor at a time) (put `company` after the company name).
                        4. Pricing list for competitors' products/services (maximum 3 competitors or less), aiming to pinpoint market positioning opportunities.

                        Your objective is to synthesize the information of 'brand_answers' tool into a very detailed well-structured report that encompasses market trends, competitive analysis, and pricing insights. don't put recommendations on.

                        Embark on this mission with the initiative, utilizing your tools to their fullest potential without further prompts. Your findings will forge the path for '{BRAND_NAME}' to navigate the competitive landscape and seize market opportunities with precision and insight."""

                sec_agent = create_openai_tools_agent(main_model, tools, prompt)
                sec_agent_executor = AgentExecutor(agent=sec_agent, tools=tools, verbose=True, max_iterations=500,
                                                   max_tokens=3000)

                online_report = ""
                with st.spinner('Generating in-depth market analysis...'):
                    online_report = sec_agent_executor.invoke(({"input": "start"}))['output']
                questionaire_report += "\n\n" + online_report

                prompt.messages[
                    0].prompt.template = f"""As a marketing bot armed with the detailed insights from {BRAND_NAME}'s survey responses and the comprehensive online report, your mission is to construct a Matter Pyramid that captures the brand's core identity within the {INDUSTRY}. Your output will be a pyramid divided into three tiers, each one echoing a key aspect of the brand's DNA: Functional Benefit, Culture and Values, and Emotional Benefit.

                1. **Functional Benefit**: Delve into the brand's offerings and the unique solutions it provides for customer challenges. From this, determine and define the foundational differentiators that establish {BRAND_NAME} as a leader in the {INDUSTRY}. Summarize this under 'Functional Benefit,' showcasing the intelligent decisions the brand makes regarding environmental stewardship, investment value, and familial care.

                2. **Culture and Values**: Reflect on {BRAND_NAME}'s internal ethos, its commitments, and the values it upholds. Under 'Culture and Values,' draft a narrative that puts the brand's consideration for its partners and stakeholders at the forefront, emphasizing a commitment to adding value and enriching every interaction.

                3. **Emotional Benefit**: Glean from the survey and report the emotional threads that bind the customers to the brand. In 'Emotional Benefit,' narrate how {BRAND_NAME} offers peace of mind, illustrating a deep understanding of customer needs and the trust they place in the brand, ensuring they are perpetually 'in safe hands.'

                Craft a response that creatively distills these three tiers into a compelling and brief narrative. This narrative should align with {BRAND_NAME}'s market position and articulate the unique story of how it stands out in the {INDUSTRY}."""

                main_tools = [Tool(name="nothing", func=lambda q: "", description="never use me",
                                   handle_tool_error=True)]
                main_model.max_tokens = 2000
                agent_1 = create_openai_tools_agent(main_model, main_tools, prompt)
                agent_executor_1 = AgentExecutor(agent=agent_1, tools=main_tools, verbose=True, max_iterations=500,
                                                 max_tokens=3000)
                with st.spinner('Creating matter pyramid...'):
                    matter_pyramid = agent_executor_1.invoke(({"input": questionaire_report}))['output']

                prompt.messages[
                    0].prompt.template = f"""You are a brand called '{BRAND_NAME}', focusing on innovation and leadership within the '{INDUSTRY}' sector. you have been provided answers to the questionnaire and an online report for your brand, and use all the information within it to deliver a very long, very detailed, and creative marketing strategy and campaign about yourself as a cohesive narrative that not only outlines the tactical approach but also tells the story of '{BRAND_NAME}' and its journey to redefine '{BRAND_NAME}' in its industry.

                1. **Brand Insights**: Deeply analyze the input on {BRAND_NAME}'s market dilemma, solutions, product offerings, and credibility. Identify the core opportunities {BRAND_NAME} aims to capture and how it differentiates itself in addressing customer needs, and present it like you are talking about youself.

                2. **Competitor Analysis**: Examine {BRAND_NAME}'s main competitors, their strengths, weaknesses, and market positions. Highlight {BRAND_NAME}'s competitive advantage based on this analysis.

                3. **Target Audience**: Define {BRAND_NAME}'s primary and secondary target audiences based on the demographics and psychographics provided. Outline strategies for engaging these audiences.

                4. **Marketing Strategy**:
                    - **Brand Positioning**: Summarize {BRAND_NAME}'s market position and unique value proposition.
                    - **Engagement Channels**: Identify the most effective channels for reaching {BRAND_NAME}'s target audience, considering both digital and traditional platforms.
                    - **Content and Messaging**: Suggest key messages that resonate with {BRAND_NAME}'s brand promise and audience's expectations.

                5. **Campaign Concept**: Propose a campaign that embodies {BRAND_NAME}'s strategic goals, including a creative titles, objectives, key activities, and expected outcomes.

                6. **Implementation Plan**: Outline steps for executing the marketing strategy and campaign, including timelines and key milestones.

                7. **Evaluation Metrics**: Specify how to measure the success of the marketing strategy and campaign, focusing on KPIs related to audience engagement, brand awareness, and sales performance.

                DON'T USE ANY TOOL."""

                agent_2 = create_openai_tools_agent(main_model, main_tools, prompt)
                agent_executor_2 = AgentExecutor(agent=agent_2, tools=main_tools, verbose=True, max_iterations=500,
                                                 max_tokens=3000)
                output = ""
                with st.spinner('Generating marketing strategy and campaign...'):
                    output = agent_executor_2.invoke({"input": questionaire_report})

                st.write(matter_pyramid + "\n\n" + output['output'])
        else:
            if not document_content:
                st.error("Please answer all the questions.")
            if not BRAND_NAME:
                st.error("Please enter the brand name.")
            if not INDUSTRY:
                st.error("Please enter the industry of your brand.")
