import streamlit as st
from streamlit_chat import message
import re
import json
import os
import google.generativeai as genai
from validation import validate_name, validate_email, validate_phone, sanitize_input
from data_handler import save_candidate_data
import plotly.graph_objects as go
import random
from login import auth_flow

# ---------------------- API Key Setup ----------------------
API_KEY = "AIzaSyBBkqHLQImyULPx8ta6JXS2sTBJj1Mc6e0"  # Replace with your actual API key
os.environ["GOOGLE_API_KEY"] = API_KEY
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# ---------------------- UI Enhancements ----------------------
st.set_page_config(page_title="HireSense AI Assistant", layout="wide")

# Custom CSS for a more modern look similar to Swiggy chatbot
st.markdown(
    """
    <style>
    .main {
        background-color: transparent !important;
        padding: 20px;
        border-radius: 10px;
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-container {
        background-color: transparent !important;
        box-shadow: none !important; /* Remove shadow if needed */
        max-width: 10px;
        margin: 0 10px;
        border-radius: 50px;   
    }
    .highlight-text {
        font-weight: bold;
        background-color: yellow;
        padding: 2px 5px;
        border-radius: 5px;
    }
    .user-message {
        font-family: 'Courier New', monospace !important;  /* User message font */
        font-size: 16px !important;
        color: #00bfff !important;  /* Light blue text */
        background-color: transparent !important; /* Light blue for user messages */
        border-radius: 20px 20px 0 20px !important;
        padding: 12px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
    }
    .assistant-message {
        font-family: 'Georgia', serif !important;  /* Assistant message font */
        font-size: 18px !important;
        color: white !important;  /* Green text */
        background-color: transparent !important; /* Light gray for assistant messages */
        border-radius: 20px 20px 20px 0 !important;
        padding: 100px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
    }
    .stTextInput > div > div > input {
        background-color: transparent !important;
        color: white !important; /* Change text color if needed */
        border-radius: 30px;
        border: 1px solid white;
        font-size: 16px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    .stTextInput > div {
        background-color: transparent !important;
    }
    .sidebar .sidebar-content {
        background-color: #1c6758; /* Dark green background for sidebar */
        color: white;
    }
    .sidebar h1, .sidebar h2, .sidebar h3 {
        color: #fff;
    }
    /* Add custom scrollbar */
    .scrollable-container {
        overflow-y: auto;
        max-height: 600px; /* Adjust the height as needed */
        padding: 10px;
    }
    /* Style for the scrollbar track */
    .scrollable-container::-webkit-scrollbar {
        width: 6px; /* Adjust the width as needed */
    }
    /* Style for the scrollbar thumb */
    .scrollable-container::-webkit-scrollbar-thumb {
        background-color: #c0c0c0; /* Color of the thumb */
        border-radius: 10px; /* Roundness of the thumb */
    }
    /* Style for the scrollbar track when hovered */
    .scrollable-container::-webkit-scrollbar-track:hover {
        background-color: #f0f0f0; /* Color of the track when hovered */
    }
    /* Header styling */
    .header {
        display: flex;
        align-items: center;
        padding: 20px;
        background-color: #1c6758;
        color: white;
        border-radius: 20px 20px 0 0;
        margin-bottom: 20px;
    }
    .header-logo {
        width: 40px;
        height: 40px;
        margin-right: 15px;
        background-color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #1c6758;
    }
    .header-title {
        font-size: 20px;
        font-weight: bold;
    }
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 10px;
        color: #888;
        font-size: 12px;
        margin-top: 20px;
    }
    /* Gauge chart styling */
    .gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
        margin-bottom: 20px;
        padding: 20px;
        background-color: white;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .gauge-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #1c6758;
    }
    .gauge-subtitle {
        font-size: 14px;
        color: #666;
        margin-bottom: 20px;
        text-align: center;
    }
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        padding: 10px;
        margin-bottom: 15px;
    }
    .typing-indicator span {
        height: 10px;
        width: 10px;
        float: left;
        margin: 0 1px;
        background-color: #9E9EA1;
        display: block;
        border-radius: 50%;
        opacity: 0.4;
    }
    .typing-indicator span:nth-of-type(1) {
        animation: 1s blink infinite 0.3333s;
    }
    .typing-indicator span:nth-of-type(2) {
        animation: 1s blink infinite 0.6666s;
    }
    .typing-indicator span:nth-of-type(3) {
        animation: 1s blink infinite 0.9999s;
    }
    @keyframes blink {
        50% {
            opacity: 1;
        }
    }
    /* Button styling */
    .stButton > button {
        border-radius: 30px;
        background-color: #1c6758;
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #134e4a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for additional information/settings
# Enhanced sidebar with interactive elements
with st.sidebar:
    # Logo and title area
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("""
        <div style="background-color: #1c6758; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 20px;">
            HS
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("<h1 style='margin-bottom: 0; color: #1c6758; font-size: 24px;'>HireSense AI</h1>",
                    unsafe_allow_html=True)
        st.markdown("<p style='margin-top: 0; color: #fff; font-size: 14px;'>Smart Recruitment Assistant</p>",
                    unsafe_allow_html=True)

    st.markdown("---")

    # Interview progress tracker
    if "current_step" in st.session_state and "candidate_data" in st.session_state:
        steps = ["greeting", "name", "email", "phone", "years_experience", "desired_positions", "tech_stack",
                 "technical_questions", "conclusion", "exit"]
        current_step_index = steps.index(st.session_state.current_step) if st.session_state.current_step in steps else 0
        progress_percentage = min(100, int((current_step_index / (len(steps) - 1)) * 100))

        st.subheader("Interview Progress")
        st.progress(progress_percentage / 100)
        st.caption(f"{progress_percentage}% complete")

        # Show candidate profile if available
        if st.session_state.candidate_data.get("full_name"):
            st.subheader("Candidate Profile")
            with st.expander("View Details", expanded=False):
                st.markdown(f"**Name:** {st.session_state.candidate_data.get('full_name', 'N/A')}")
                st.markdown(f"**Email:** {st.session_state.candidate_data.get('email', 'N/A')}")
                st.markdown(f"**Experience:** {st.session_state.candidate_data.get('years_experience', 'N/A')} years")

                if st.session_state.candidate_data.get("tech_stack"):
                    st.markdown("**Tech Stack:**")
                    for tech in st.session_state.candidate_data.get("tech_stack", [])[:5]:
                        st.markdown(f"- {tech}")
                    if len(st.session_state.candidate_data.get("tech_stack", [])) > 5:
                        st.caption(f"+ {len(st.session_state.candidate_data.get('tech_stack', [])) - 5} more")

    # Interactive help section
    st.markdown("---")
    st.subheader("Need Help?")
    help_options = st.selectbox(
        "Select a topic:",
        ["Choose a topic", "How the interview works", "Technical questions", "Evaluation process", "Contact support"]
    )

    if help_options == "How the interview works":
        st.info(
            "The interview process consists of collecting your basic information, followed by technical questions based on your declared skills. At the end, you'll receive a hiring probability score.")
    elif help_options == "Technical questions":
        st.info(
            "Questions are dynamically generated based on the technologies you list in your tech stack. Be specific and detailed in your answers for the best evaluation.")
    elif help_options == "Evaluation process":
        st.info(
            "Your responses are evaluated based on accuracy, depth of knowledge, and practical application. The hiring probability considers your experience and how well your skills match the desired positions.")
    elif help_options == "Contact support":
        st.info("Email: support@HireSense .ai\nPhone: +1-555-123-4567")

    # Footer
    st.markdown("---")

    st.caption("© 2025 HireSense  AI")

    # Debug mode for developers
    with st.expander("Developer Tools", expanded=False):
        if st.button("Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ---------------------- Enhanced AI Responses ----------------------
def get_greeting_phrases():
    greetings = [
        "Hi there! I'm Sensei, your AI interviewer from Hiresense. Ready to showcase your tech skills?",
        "Welcome to HireSense! I'm here to learn about your technical expertise. Let's get started!",
        "Hello! I'm your HireSense AI assistant. I'm excited to discover your technical talents!",
        "Greetings! I'm HireSense, your AI interviewer. Let's explore your technical abilities together!",
        "Welcome aboard! I'm Hiresense, your AI recruiter. I'm here to understand your technical background."
    ]
    return random.choice(greetings)

def get_encouragement_phrases():
    encouragements = [
        "Great answer! Let's continue exploring your skills.",
        "Excellent! I'm getting a good sense of your expertise.",
        "That's insightful! Moving on to the next question.",
        "Well explained! Let's dive deeper into your technical knowledge.",
        "Thanks for sharing that! I'm impressed with your understanding."
    ]
    return random.choice(encouragements)

def get_transition_phrases():
    transitions = [
        "Now, let's talk about your professional background.",
        "Let's shift gears and discuss your work experience.",
        "Next, I'd like to learn about your technical expertise.",
        "Great! Now I'd like to understand more about your skills.",
        "Fantastic! Let's move on to discuss your technical capabilities."
    ]
    return random.choice(transitions)

def get_conclusion_phrases():
    conclusions = [
        "Thank you for sharing your expertise with me today. I've analyzed your responses and have your results ready!",
        "You've done a great job with the technical screening! I've prepared your evaluation based on your responses.",
        "Thanks for completing the interview! Based on your answers, I've calculated your hiring probability.",
        "Great job with the technical questions! I've analyzed your responses and prepared your results.",
        "The technical screening is complete! I've analyzed your responses and have your hiring probability ready."
    ]
    return random.choice(conclusions)

def get_feedback_phrases(probability):
    if probability == 100:
        return "🎉 Congratulations! You have demonstrated exceptional technical skills. You will be contacted soon regarding the next round. Keep up the great work!"
    elif probability >= 80:
        return "⭐ Outstanding performance! Your technical skills are highly impressive. You are a top candidate and have a strong chance of moving forward!"
    elif probability >= 60:
        return "✅ Great job! You have solid technical expertise and are a competitive candidate. Some minor improvements could make you even stronger!"
    elif probability >= 40:
        return "👍 Good effort! You have demonstrated some technical knowledge, but there are areas to improve. A bit more practice will boost your chances!"
    elif probability >= 20:
        return "⚠️ You have shown some understanding, but your technical skills need significant improvement. Consider revisiting key concepts and practicing further."
    elif probability > 0:
        return "❌ Unfortunately, your technical skills do not meet our current requirements. Consider strengthening your fundamentals and gaining more experience."
    else:  # Probability == 0
        return "🚫 No chances at this time. Your responses indicate a lack of necessary technical skills. A structured learning path will help you progress."


# ---------------------- Gemini API Integration ----------------------
def generate_questions(roles, technology, years, num_questions=5):
    """
    Generates technical interview questions based on the specified technology and experience level,
    incorporating knowledge from the provided GeeksforGeeks and InterviewBit links.
    """
    # Validate that the technology is from the suggested list
    if hasattr(st.session_state, 'suggested_tech_stack') and technology not in st.session_state.suggested_tech_stack:
        st.warning(f"{technology} is not in the suggested technology list. Please select from the suggested technologies.")
        return []
   
    if years == 0:
        print("hiii")
        experience_level = "beginner-level"
        context_prompt = f"""
        
        Generate {num_questions} technical interview questions about {technology} for {roles} screening.
        Considering beginner-level knowledge in {technology} as found in the following resources:
        - https://www.geeksforgeeks.org/{technology.lower()}-interview-questions/
        - https://www.interviewbit.com/{technology.lower()}-interview-questions/

        Now i want you study the above links thoroughly and ask or generate the questions by keeping the above links as you reference
        and generate the questions as a list,one question per line, without explanations or answers. Start with a number for each question.
        And also make sure the questions are from the mentioned technology only and it should focus on practical knowledge and real-world applications.
        Please make sure you do not include scenario based qustions...i need you to generate only the questions that are from the
        reference link and even related from that links 

    
        """
    elif 1 <= years <= 4:
        experience_level = "intermediate-level"
        context_prompt = f"""
        Generate {num_questions} technical interview questions on {technology}, suitable for screening {roles} 
        candidates 
        with approximately {years} years of hands-on experience. The questions must focus on:
            - Intermediate-level concepts and practical usage of {technology}
            - Slightly challenging or tricky scenarios that require problem-solving, deeper understanding, or creative thinking
            
            - Topics referenced in:
    - https://www.geeksforgeeks.org/{technology.lower()}-interview-questions/
    - https://www.interviewbit.com/{technology.lower()}-interview-questions/
    - https://www.simplilearn.com/tutorials/angular-tutorial/angular-interview-questions/

Format:
- Present questions as a numbered list, one per line
- Do NOT include answers or explanations
- Focus strictly on {technology}-related knowledge (avoid generic programming topics)
- Questions should challenge the candidate to think critically and apply their knowledge in slightly complex or unusual scenarios.
"""
    elif years > 4:
        experience_level = "advanced-level"
        context_prompt = f"""
        Generate {num_questions} **scenario-based** technical interview questions on {technology}, 
        suitable for senior-level {roles} with {years} years of experience. Focus on:

        - Deep understanding, architecture, optimization, and real-world scalability challenges
        - Questions derived from practical experience in production-grade systems
        - Advanced topics referenced in:
            - https://www.geeksforgeeks.org/{technology.lower()}-interview-questions/
            - https://www.interviewbit.com/{technology.lower()}-interview-questions/
            - https://codewithpawan.medium.com/angular-interview-questions-from-beginners-to-advance-part-1-7f135fe92de3

        Format:
        - Numbered list
        - Do NOT include explanations or answers
        - Stay specific to {technology} (no generic CS theory)
        """

    # ✅ Define base_prompt here
    base_prompt = "You are an expert interviewer generating technical questions for software developers."

    # Now combine base_prompt with context
    full_prompt = f"""{base_prompt}
The questions should be suitable for candidates with {years} years of experience ({experience_level}).
{context_prompt}
"""

    try:
        response = model.generate_content(full_prompt)
        response.resolve()
        content = response.text
        print(content)

        # Process the content to extract individual questions
        questions = []
        question_number = 1
        for line in content.strip().split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line[0] == "-"):
                question = line.split(".", 1)[-1].strip() if "." in line else line[1:].strip()
                questions.append(f"{question_number}. {question}")
                question_number += 1

        return questions

    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

# ---------------------- Ses--- Session State Initialization ----------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "current_step" not in st.session_state:
    st.session_state.current_step = "greeting"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {
        "full_name": "",
        "email": "",
        "phone": "",
        "years_experience": 0,
        "desired_positions": [],
        "tech_stack": [],
        "responses": {},
        "final_comments": ""
    }
if "questions" not in st.session_state:
    st.session_state.questions = {}
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "probability" not in st.session_state:
    st.session_state.probability = 0
if "show_typing" not in st.session_state:
    st.session_state.show_typing = False


# ---------------------- Helper Functions ----------------------
def add_message(role, content):
    st.session_state.conversation.append({"role": role, "content": content})


def get_next_question():
    if st.session_state.current_step == "technical_questions":
        all_questions = []
        for tech in st.session_state.candidate_data["tech_stack"]:
            if tech in st.session_state.questions:
                all_questions.extend([(tech, q) for q in st.session_state.questions[tech]])
        if st.session_state.current_question_index < len(all_questions):
            tech, question = all_questions[st.session_state.current_question_index]
            return f"{question}"
        else:
            st.session_state.current_step = "conclusion"
            return get_conclusion_phrases()
    return None


# ---------------------- Create Interactive Gauge Chart ----------------------
def create_gauge_chart(probability):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Hiring Probability", 'font': {'size': 24, 'color': '#1c6758'}},
        delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#1c6758"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#ffcccb'},
                {'range': [30, 60], 'color': '#fffacd'},
                {'range': [60, 100], 'color': '#d0f0c0'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        font=dict(color="black", family="Arial")
    )
    return fig


# ---------------------- Input Processing Logic ----------------------
def process_input():
    user_input = sanitize_input(st.session_state.user_input)  # Sanitize the input first

    if user_input.lower() == "exit":
        save_candidate_data(st.session_state.candidate_data)
        add_message("assistant",
                    "Thank you for your time! Your information has been saved. The HireSense team will be in touch soon. Have a great day! 👋")
        st.session_state.current_step = "exit"
        st.session_state.user_input = ""  # Clear the input field
        return

    # Add user's input as a message in the conversation
    add_message("user", user_input)

    if st.session_state.current_step == "greeting":
        add_message("assistant", "Great! Let's start with your full name (First Last):")
        st.session_state.current_step = "name"
    elif st.session_state.current_step == "name":
        if validate_name(user_input):
            st.session_state.candidate_data["full_name"] = user_input
            add_message("assistant", f"Thank you, {user_input.split()[0]}! Please provide your email address:")
            st.session_state.current_step = "email"
        else:
            add_message("assistant", "I need your full name to proceed. Please enter a valid full name (First Last):")
    elif st.session_state.current_step == "email":
        if validate_email(user_input):
            st.session_state.candidate_data["email"] = user_input
            add_message("assistant",
                        "Perfect! Now, please provide your phone number (including country code, e.g., +1-555-123-4567):")
            st.session_state.current_step = "phone"
        else:
            add_message("assistant", "That doesn't look like a valid email. Please enter a valid email address:")
    elif st.session_state.current_step == "phone":
        if validate_phone(user_input):
            st.session_state.candidate_data["phone"] = user_input
            add_message("assistant",
                        f"{get_transition_phrases()} How many years of professional experience do you have?")
            st.session_state.current_step = "years_experience"
        else:
            add_message("assistant",
                        "That doesn't seem right. Please enter a valid phone number (including country code, e.g., +1-555-123-4567):")
    elif st.session_state.current_step == "years_experience":
        try:
            years = int(user_input)
            if 0 <= years <= 30:
                st.session_state.candidate_data["years_experience"] = years
                experience_response = "Impressive! " if years > 10 else "Great! "
                add_message("assistant",
                            f"{experience_response}Which positions are you interested in? Please provide a comma-separated list from:\n\n"
                            "[Software Engineer, Frontend Developer, Backend Developer, Full-Stack Developer, "
                            "DevOps Engineer, Data Engineer, Machine Learning Engineer, AI Researcher, "
                            "Cybersecurity Analyst, Cloud Architect, Database Administrator, QA Engineer, "
                            "Product Manager, UI/UX Designer, Mobile App Developer, Embedded Systems Engineer]")
                st.session_state.current_step = "desired_positions"
            else:
                add_message("assistant", "Please enter a number between 0 and 30:")
        except ValueError:
            add_message("assistant", "I need a number to proceed. Please enter a valid number of years:")

    # Role Selection & Tech Stack Generation
    elif st.session_state.current_step == "desired_positions":
        positions = [pos.strip() for pos in user_input.split(",")]
        valid_positions = [
            "Software Engineer", "Frontend Developer", "Backend Developer", "Full-Stack Developer",
            "DevOps Engineer", "Data Engineer", "Machine Learning Engineer", "AI Researcher",
            "Cybersecurity Analyst", "Cloud Architect", "Database Administrator", "QA Engineer",
            "Product Manager", "UI/UX Designer", "Mobile App Developer", "Embedded Systems Engineer"
        ]

        if any(pos in valid_positions for pos in positions):
            st.session_state.candidate_data["desired_positions"] = [pos for pos in positions if pos in valid_positions]

            # Use AI to generate the tech stack based on the selected role
            selected_role = ", ".join(st.session_state.candidate_data["desired_positions"])
            prompt = (
                f"List the most important programming languages, tools, and frameworks a {selected_role} should know."
                f" Return a clean list of maximum 20 things, without additional text or formatting. No bold texts or symbols !")

            try:
                response = model.generate_content(prompt)
                response.resolve()
                suggested_tech_stack = response.text.split("\n")  # Split response into list

                # Store the AI-generated tech stack
                st.session_state.suggested_tech_stack = [tech.strip() for tech in suggested_tech_stack if tech.strip()]

                add_message("assistant",
                            f"For the role of {selected_role}, the most relevant technologies are: \n\n {', '.join(st.session_state.suggested_tech_stack)}.")
                add_message("assistant", "Please select the technologies you are proficient in from the list above.")
                st.session_state.current_step = "select_tech_stack"

            except Exception as e:
                st.error(f"Error generating tech stack: {e}")
                add_message("assistant",
                            "There was an error generating the tech stack. Please enter your known technologies manually.")
                st.session_state.current_step = "tech_stack"
        else:
            add_message("assistant",
                        "Please select a valid position from the list: " + ", ".join(valid_positions) + ".")

    # Tech Stack Selection (Fix for Questions Not Generating)
    elif st.session_state.current_step == "select_tech_stack":
        selected_tech = [tech.strip() for tech in user_input.split(",")]

        if selected_tech:
            st.session_state.candidate_data["tech_stack"] = selected_tech
            add_message("assistant",
                        f"Great choice! Now, I'll ask you some technical questions based on your expertise in {', '.join(selected_tech)}.")

            # Generate technical questions
            for tech in selected_tech:
                print("in loop...")
                questions = generate_questions(st.session_state.candidate_data["desired_positions"],tech,st.session_state.candidate_data["years_experience"])
                if questions:
                    st.session_state.questions[tech] = questions
                else:
                    st.session_state.questions[tech] = []  # Ensure an empty list if no questions are generated

            st.session_state.current_step = "technical_questions"
            next_question = get_next_question()
            if next_question:
                add_message("assistant", next_question)
        else:
            add_message("assistant", "Please select at least one technology from the suggested list.")

    elif st.session_state.current_step == "technical_questions":
        all_questions = []
        for tech in st.session_state.candidate_data["tech_stack"]:
            if tech in st.session_state.questions:
                all_questions.extend([(tech, q) for q in st.session_state.questions[tech]])

        if st.session_state.current_question_index < len(all_questions):
            tech, question = all_questions[st.session_state.current_question_index]

            if tech not in st.session_state.candidate_data["responses"]:
                st.session_state.candidate_data["responses"][tech] = {}

            st.session_state.candidate_data["responses"][tech][question] = user_input
            st.session_state.current_question_index += 1
            next_question = get_next_question()

            if next_question:
                add_message("assistant", f"{next_question}")
            else:
                st.session_state.current_step = "conclusion"
                add_message("assistant", get_conclusion_phrases())

    elif st.session_state.current_step == "conclusion":
        st.session_state.candidate_data["final_comments"] = user_input

        # Calculate time taken

        # Send data to Gemini API for final evaluation
        evaluation_prompt = f"""
                Evaluate strictly candidate based on the following data:
                - Full Name: {st.session_state.candidate_data["full_name"]}
                - Email: {st.session_state.candidate_data["email"]}
                - Phone: {st.session_state.candidate_data["phone"]}
                - Years of Experience: {st.session_state.candidate_data["years_experience"]} 
                - Desired Positions: {', '.join(st.session_state.candidate_data["desired_positions"])}
                - Tech Stack: {', '.join(st.session_state.candidate_data["tech_stack"])}
                - Responses: {json.dumps(st.session_state.candidate_data["responses"], indent=4)} Important feature, evaluate with respect to question !

                Simply return a hiring probability percentage with respect to Technical answers between 0 and 100. Return only the number.
                """

        try:
            response = model.generate_content(evaluation_prompt)
            response.resolve()
            content = response.text

            # Extract the final probability from the response
            probability_match = re.search(r'(\d+)', content)
            probability = int(
                probability_match.group(1)) if probability_match else 0  # Default probability if not found

            # Ensure probability is within 0-100 range
            probability = max(0, min(100, probability))

            # Store probability in session state
            st.session_state.probability = probability
            st.session_state.candidate_data["hiring_probability"] = probability

            # Add feedback based on probability
            feedback = get_feedback_phrases(probability)
            add_message("assistant", feedback)
            st.session_state.candidate_data["assistant_feedback"] = feedback
            save_candidate_data(st.session_state.candidate_data)
        except Exception as e:
            st.error(f"Error generating final evaluation: {e}")
            add_message("assistant",
                        "I couldn't generate your final evaluation. But we've saved your responses and our team will review them.")
            st.session_state.probability = 0  # Default value in case of error

        st.session_state.current_step = "exit"
    else:
        # Fallback response
        add_message("assistant", "Let's focus on your tech evaluation. Could you clarify?")

        # Clear the input field after processing and hide typing indicator
    st.session_state.show_typing = False
    st.session_state.user_input = ""



# ---------------------- Main Application ----------------------
def main():
    st.markdown("<div class='main'>", unsafe_allow_html=True)  # Apply the main style

    # Custom header
    st.markdown("""
        <div class="header">
            <div class="header-logo">HS</div>
            <div class="header-title">HireSense AI Assistant</div>
        </div>
        """, unsafe_allow_html=True)

    # Container for the chat with scrollbar

    if st.session_state.current_step != "exit" or not st.session_state.conversation:
        if not st.session_state.conversation:
            greeting = get_greeting_phrases()
            add_message("assistant", f"{greeting} \n Type 'exit' anytime to end the interview.")
            add_message("assistant", "Great! Let's start with your full name (First Last):")
            st.session_state.current_step = "name"

        # Display conversation using streamlit-chat with custom styles
        for i, msg in enumerate(st.session_state.conversation):
            if msg["role"] == "user":
                message(msg["content"], is_user=True, key=str(i), avatar_style="adventurer",
                        seed=hash(st.session_state.candidate_data["email"]) if st.session_state.candidate_data[
                            "email"] else 1)  # User message with avatar
            else:
                message(msg["content"], is_user=False, key=str(i) + "_ai", avatar_style="bottts",
                        seed=2)  # Assistant message

        # Typing indicator
        if st.session_state.show_typing:
            st.markdown("""
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                """, unsafe_allow_html=True)

        # Input text bar always after the convo and clear it after answering
        st.text_input("", key="user_input", on_change=process_input, value="", placeholder="Type your response here...")


    # Display gauge chart if in exit state and we have a probability score
    # Display gauge chart and assistant feedback after completion
    if st.session_state.current_step == "exit":

        st.markdown(f"<div class='gauge-title'>Your Hiring Probability</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='assistant-message'><b>Thank you for your time. Your information has been saved. The HireSense team will be in touch soon.</b></div>",
            unsafe_allow_html=True)

        # Display the probability gauge chart
        fig = create_gauge_chart(st.session_state.probability)
        st.plotly_chart(fig, use_container_width=True)
        # Show the assistant's feedback immediately below the chart
        feedback = st.session_state.candidate_data.get("assistant_feedback", "No feedback available.")
        st.markdown(f"<div class='assistant-message'><b>Feedback:</b> {feedback}</div>", unsafe_allow_html=True)
        # Add restart button
        if st.button("Start New Interview"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # Close chat container

    # Footer
    st.markdown("""
        <div class="footer">
            HireSense AI • Intelligent Recruitment Assistant • © 2025
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close main container


if __name__ == "__main__":
    # ---------------------- Authentication Check ----------------------
    # Check if user is authenticated at the beginning of the app
    authenticated = auth_flow()

    # Only show the main application if authenticated
    if authenticated:
        main()