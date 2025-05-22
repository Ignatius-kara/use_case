import streamlit as st
import json
import random
import re
from datetime import datetime, timedelta
import hashlib

# Page configuration
st.set_page_config(
    page_title="TalkSafe - Mental Health Support",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Nigerian-inspired styling
@st.cache_data
def load_css():
    return """
    <style>
    .main {
        background: linear-gradient(135deg, #006633 0%, #228B22 50%, #FFFFFF 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .header-container {
        background: rgba(0, 102, 51, 0.95);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 2px solid #006633;
        max-height: 450px;
        overflow-y: auto;
    }
    
    .user-message {
        background: linear-gradient(135deg, #006633 0%, #228B22 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 5px 18px;
        margin: 8px 0;
        margin-left: 15%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        word-wrap: break-word;
        font-size: 14px;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #FF8C00 0%, #FFB347 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 5px;
        margin: 8px 0;
        margin-right: 15%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        word-wrap: break-word;
        font-size: 14px;
    }
    
    .crisis-message {
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
        border: 2px solid #B22222;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(220, 20, 60, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(220, 20, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(220, 20, 60, 0); }
    }
    
    .language-selector {
        background: rgba(255, 255, 255, 0.9);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .mood-indicator {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 2px;
        font-size: 12px;
    }
    
    .mood-good { background: #90EE90; color: #006400; }
    .mood-okay { background: #FFD700; color: #B8860B; }
    .mood-bad { background: #FFB6C1; color: #8B0000; }
    
    div.stButton > button {
        background: linear-gradient(135deg, #006633 0%, #228B22 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 100%;
        margin: 5px 0;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }
    
    .quick-help-btn {
        font-size: 12px !important;
        padding: 8px 12px !important;
    }
    
    .stSelectbox label {
        color: #006633 !important;
        font-weight: bold;
    }
    </style>
    """

# Multilingual response templates with Nigerian cultural context
@st.cache_data
def load_cultural_responses():
    return {
        "english": {
            "greetings": {
                "patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how are you"],
                "responses": [
                    "Hello! Welcome to TalkSafe. I'm here to listen and support you. How are you feeling today? 🛡️",
                    "Hi there! This is your safe space to share what's on your mind. What's happening with you today?",
                    "Hey! I'm glad you're here. Whether you're feeling great or going through a tough time, I'm here to chat. What's up?"
                ]
            },
            "academic_stress": {
                "patterns": ["exam", "test", "study", "school", "university", "assignment", "project", "result", "grade", "academic"],
                "responses": [
                    "Academic pressure can be really overwhelming, especially in our Nigerian universities. Remember, your grades don't define your worth as a person. Have you tried breaking your study time into smaller chunks? Maybe 30 minutes study, 10 minutes break?",
                    "I understand exam stress can feel like too much. Many Nigerian students face this same challenge. Consider reaching out to your departmental counselor or academic advisor - they're there to help you succeed, not judge you.",
                    "School wahala can really stress someone out! But you know what? You've made it this far, which shows you're stronger than you think. What specific subject or assignment is giving you the most trouble right now?"
                ]
            },
            "anxiety": {
                "patterns": ["anxious", "anxiety", "worry", "nervous", "panic", "overwhelmed", "scared", "fear"],
                "responses": [
                    "Anxiety can feel really overwhelming, but you're not alone in this. Many Nigerian students experience this. Let's try a quick breathing exercise: breathe in for 4 counts, hold for 4, breathe out for 6. Can you try this with me?",
                    "I hear you. Anxiety can make everything feel too much. In our culture, we sometimes feel pressure to 'be strong' all the time, but it's okay to acknowledge when you're struggling. What's been triggering your anxiety lately?",
                    "Feeling anxious is completely normal, especially with all the pressures of university life in Nigeria. Your feelings are valid. Have you tried talking to a trusted friend or family member about what you're experiencing?"
                ]
            },
            "depression": {
                "patterns": ["depressed", "sad", "hopeless", "empty", "worthless", "tired", "down", "heavy heart"],
                "responses": [
                    "I'm really glad you felt comfortable sharing this with me. Depression can make everything feel heavy and difficult. You're not alone, and seeking help shows incredible strength. How have you been taking care of yourself lately?",
                    "Thank you for trusting me with these feelings. Depression affects many Nigerian students, but there's often shame around discussing it. You're brave for reaching out. What's been the hardest part of your day recently?",
                    "I hear the pain in your words. Depression can make us feel isolated, but you're not alone. Many students at Nigerian universities experience this. Have you considered speaking with a counselor or therapist?"
                ]
            },
            "relationships": {
                "patterns": ["relationship", "boyfriend", "girlfriend", "family", "friends", "lonely", "heartbreak", "love"],
                "responses": [
                    "Relationship issues can be really tough, especially when balancing them with academic life. In Nigerian culture, we value relationships deeply, which can make conflicts even more painful. What's been weighing on your heart?",
                    "I understand relationship challenges can feel overwhelming. Whether it's family expectations, romantic relationships, or friendships, these connections are important. Want to talk about what's been troubling you?",
                    "Relationships can be complicated, especially with the cultural expectations we face as Nigerian students. You don't have to navigate this alone. What's been the biggest challenge in your relationships lately?"
                ]
            },
            "financial_stress": {
                "patterns": ["money", "financial", "fees", "broke", "pocket money", "school fees", "family pressure"],
                "responses": [
                    "Financial stress is real, especially for Nigerian university students. Many of us face these challenges. Have you looked into scholarships, work-study programs, or spoken with your school's financial aid office?",
                    "Money wahala can really affect our mental health and studies. You're not alone in this struggle. Many Nigerian students face similar challenges. Are there any campus resources or part-time opportunities you could explore?",
                    "Financial pressure can be overwhelming, particularly when family expectations are involved. Remember, your worth isn't determined by your financial situation. What support systems do you have available right now?"
                ]
            },
            "crisis": {
                "patterns": ["suicide", "kill myself", "die", "end it all", "hurt myself", "not worth living", "give up"],
                "responses": [
                    "🚨 I'm very concerned about you right now. Your life has value and meaning. Please reach out for immediate help: Call the National Emergency Number 112, or contact your university counseling center right away. You don't have to face this alone.",
                    "🚨 I care about your safety and I'm worried about you. Please connect with someone immediately - a trusted friend, family member, or professional. You can call 112 for emergency services or reach out to your campus counseling center.",
                    "🚨 Your life matters so much. These feelings can change with proper support. Please reach out to emergency services (112) or your university's counseling center right now. You deserve help and support."
                ]
            }
        },
        "pidgin": {
            "greetings": {
                "patterns": ["wetin dey happen", "how far", "how you dey", "wetin sup", "bawo"],
                "responses": [
                    "How far! Welcome to TalkSafe. I dey here to listen to you. How your body dey today? 🛡️",
                    "Wetin dey sup! This na your safe space to talk wetin dey worry you. How you dey feel today?",
                    "How you dey! I happy say you dey here. Whether you dey feel good or you get wahala, I dey here to gist with you."
                ]
            },
            "academic_stress": {
                "patterns": ["exam", "test", "study", "school wahala", "result", "grade"],
                "responses": [
                    "Exam stress fit really disturb person o! But no forget say your grade no be wetin define who you be. You don try break your study into small small parts? Like 30 minutes study, 10 minutes rest?",
                    "I understand say school matter fit dey stress you. Plenty Nigerian students dey face the same thing. You fit try reach your department counselor - dem dey there to help you, no be to judge you.",
                    "School wahala fit really stress somebody! But you know wetin? You don reach this far, na show say you strong pass how you think. Wetin subject or assignment dey give you more trouble now?"
                ]
            },
            "anxiety": {
                "patterns": ["anxiety", "dey worry", "fear", "panic", "overwhelmed"],
                "responses": [
                    "Anxiety fit really make person feel like say everything too much, but you no dey alone for this matter. Make we try one small breathing exercise: breathe in count 4, hold am count 4, breathe out count 6. You fit try am with me?",
                    "I hear you. Anxiety fit make everything feel like wahala. For our culture, sometimes we dey feel pressure to 'be strong' all the time, but e dey okay to talk say you dey struggle. Wetin dey trigger your anxiety lately?",
                    "To dey feel anxious na normal thing, especially with all the pressure for university life for Nigeria. Your feelings dey valid. You don try talk to person wey you trust about wetin you dey experience?"
                ]
            }
        }
    }

# Crisis detection system
class CrisisDetector:
    def __init__(self):
        self.crisis_keywords = [
            "suicide", "kill myself", "die", "end it all", "hurt myself", 
            "not worth living", "give up", "better off dead", "can't go on"
        ]
        self.severity_indicators = [
            "plan", "method", "tonight", "today", "pills", "rope", "bridge"
        ]
    
    def detect_crisis(self, text):
        text_lower = text.lower()
        crisis_score = 0
        
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                crisis_score += 2
        
        for indicator in self.severity_indicators:
            if indicator in text_lower:
                crisis_score += 3
        
        return crisis_score >= 2

# Intelligent response system with cultural sensitivity
class CulturalResponder:
    def __init__(self):
        self.responses = load_cultural_responses()
        self.crisis_detector = CrisisDetector()
        self.conversation_context = []
        self.user_mood_history = []
        
    def detect_language(self, user_input):
        pidgin_indicators = ["wetin", "dey", "how far", "wahala", "no be", "fit", "make we"]
        if any(indicator in user_input.lower() for indicator in pidgin_indicators):
            return "pidgin"
        return "english"
    
    def analyze_mood(self, user_input):
        positive_words = ["good", "great", "happy", "fine", "better", "okay"]
        negative_words = ["bad", "terrible", "awful", "depressed", "anxious", "overwhelmed", "stressed"]
        
        user_lower = user_input.lower()
        positive_count = sum(1 for word in positive_words if word in user_lower)
        negative_count = sum(1 for word in negative_words if word in user_lower)
        
        if positive_count > negative_count:
            return "good"
        elif negative_count > positive_count:
            return "bad"
        return "okay"
    
    def get_response_category(self, user_input, language):
        user_input = user_input.lower()
        lang_responses = self.responses[language]
        
        category_scores = {}
        for category, data in lang_responses.items():
            score = 0
            for pattern in data["patterns"]:
                if pattern in user_input:
                    score += len(pattern) * user_input.count(pattern)
            category_scores[category] = score
        
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        return "greetings"
    
    def generate_response(self, user_input):
        # Detect crisis first
        is_crisis = self.crisis_detector.detect_crisis(user_input)
        
        # Detect language
        language = self.detect_language(user_input)
        
        # Analyze mood
        mood = self.analyze_mood(user_input)
        self.user_mood_history.append(mood)
        
        # Get appropriate category
        if is_crisis:
            category = "crisis"
        else:
            category = self.get_response_category(user_input, language)
        
        # Generate response
        lang_responses = self.responses[language]
        if category in lang_responses:
            response_data = lang_responses[category]
            response = random.choice(response_data["responses"])
        else:
            # Fallback to English if category not found in pidgin
            response = random.choice(self.responses["english"]["greetings"]["responses"])
        
        # Update conversation context
        self.conversation_context.append({"input": user_input, "response": response, "mood": mood})
        if len(self.conversation_context) > 8:
            self.conversation_context = self.conversation_context[-8:]
        
        return response, is_crisis, mood, language

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'responder' not in st.session_state:
    st.session_state.responder = CulturalResponder()
if 'user_mood_history' not in st.session_state:
    st.session_state.user_mood_history = []
if 'crisis_detected' not in st.session_state:
    st.session_state.crisis_detected = False

# Limit message history
MAX_MESSAGES = 20
if len(st.session_state.messages) > MAX_MESSAGES:
    st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]

# Load CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h1>🛡️ TalkSafe</h1>
    <h3>Culturally-Sensitive Mental Health Support for Nigerian Students</h3>
    <p><em>Your safe space to talk • Confidential • Available 24/7</em></p>
</div>
""", unsafe_allow_html=True)

# Sidebar with resources and controls
with st.sidebar:
    st.markdown("### 🌍 Language / Asụsụ")
    selected_lang = st.selectbox("Choose your preferred language:", 
                                ["English", "Nigerian Pidgin"], 
                                key="lang_selector")
    
    st.markdown("### 🆘 Emergency Resources")
    st.markdown("""
    **National Emergency**  
    📞 112 (Free from any network)
    
    **Mental Health Helplines**  
    📞 0809 844 2369 (MENTal AwareNG)  
    📞 0803 772 1123 (Mentally Aware)
    
    **Campus Counseling**  
    📞 Contact your university counseling center
    
    **Crisis Text Line**  
    📱 Text "HELLO" to 741741
    """)
    
    st.markdown("### 📊 Your Mood Pattern")
    if st.session_state.user_mood_history:
        recent_moods = st.session_state.user_mood_history[-5:]
        mood_display = ""
        for mood in recent_moods:
            if mood == "good":
                mood_display += "😊 "
            elif mood == "okay":
                mood_display += "😐 "
            else:
                mood_display += "😔 "
        st.markdown(f"Recent: {mood_display}")
    
    st.markdown("### 📚 Nigerian Mental Health Resources")
    st.markdown("""
    - [MENTal AwareNG](https://mentalawareng.com)
    - [Mentally Aware Nigeria](https://mentallyawareng.org)
    - [Nigerian Psychological Association](https://npa.org.ng)
    - [She Writes Woman](https://shewriteswoman.org)
    """)
    
    if st.button("🔄 Start New Conversation", key="clear_chat"):
        st.session_state.messages = []
        st.session_state.responder = CulturalResponder()
        st.session_state.user_mood_history = []
        st.session_state.crisis_detected = False
        st.rerun()

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for message in st.session_state.messages[-12:]:  # Show last 12 messages
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        message_class = "bot-message crisis-message" if message.get("is_crisis") else "bot-message"
        st.markdown(f'<div class="{message_class}">{message["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# User input
if selected_lang == "Nigerian Pidgin":
    placeholder_text = "Talk wetin dey your mind here..."
else:
    placeholder_text = "Share what's on your mind..."

user_input = st.text_input("", key="user_input", placeholder=placeholder_text, max_chars=500)

# Process user input
if user_input and user_input.strip():
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    
    # Generate response
    bot_response, is_crisis, mood, detected_lang = st.session_state.responder.generate_response(user_input)
    
    # Track mood
    st.session_state.user_mood_history.append(mood)
    
    # Add bot response
    st.session_state.messages.append({
        "role": "assistant", 
        "content": bot_response,
        "is_crisis": is_crisis,
        "mood": mood
    })
    
    # Set crisis flag
    if is_crisis:
        st.session_state.crisis_detected = True
    
    st.rerun()

# Crisis alert
if st.session_state.crisis_detected:
    st.error("🚨 CRISIS DETECTED: If you're in immediate danger, please call 112 or go to your nearest hospital emergency room.")
    if st.button("I'm Safe Now", key="crisis_clear"):
        st.session_state.crisis_detected = False
        st.rerun()

# Quick help buttons
st.markdown("### Quick Help Options")

col1, col2, col3, col4 = st.columns(4)

if selected_lang == "Nigerian Pidgin":
    quick_actions = [
        ("😰 I Dey Worry", "I dey feel anxiety and I no know wetin to do"),
        ("📚 School Wahala", "School dey stress me and I dey overwhelmed"),
        ("💔 Relationship Matter", "I get relationship wahala wey dey worry me"),
        ("💰 Money Problem", "I get financial stress wey dey affect my mental health")
    ]
else:
    quick_actions = [
        ("😰 Feeling Anxious", "I'm feeling anxious and overwhelmed"),
        ("📚 Academic Stress", "I'm stressed about school and my studies"),
        ("💔 Relationship Issues", "I'm having relationship problems that are affecting me"),
        ("💰 Financial Pressure", "I'm stressed about money and financial issues")
    ]

for i, (col, (button_text, message)) in enumerate(zip([col1, col2, col3, col4], quick_actions)):
    with col:
        if st.button(button_text, key=f"quick_{i}"):
            st.session_state.messages.append({"role": "user", "content": message})
            bot_response, is_crisis, mood, detected_lang = st.session_state.responder.generate_response(message)
            st.session_state.user_mood_history.append(mood)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": bot_response,
                "is_crisis": is_crisis,
                "mood": mood
            })
            if is_crisis:
                st.session_state.crisis_detected = True
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #006633;">
    <strong>TalkSafe</strong> - Made with ❤️ for Nigerian University Students<br>
    <em>Confidential • Culturally-Sensitive • Always Here for You</em><br>
    <small>Remember: You're not alone in this journey. Your mental health matters.</small>
</div>
""", unsafe_allow_html=True)

# Debug info (remove in production)
if st.checkbox("Show Debug Info", value=False):
    st.write(f"Messages: {len(st.session_state.messages)}")
    st.write(f"Mood History: {st.session_state.user_mood_history[-5:] if st.session_state.user_mood_history else 'None'}")
    st.write(f"Crisis Detected: {st.session_state.crisis_detected}")
