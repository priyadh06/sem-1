import streamlit as st
import random
import json
import os
import time
from datetime import datetime

# =========================================================
# STREAMLIT CONFIG (MUST BE FIRST)
# =========================================================
st.set_page_config(
    page_title="Flashcard Quiz App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# AUTH FILES (FROM P_Final.py)
# =========================================================
USERS_FILE = "users.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


# =========================================================
# AUTH SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

# =========================================================
# LOGIN / SIGNUP (ONLY CHANGE VS ORIGINAL JACK.py)
# =========================================================
if not st.session_state.logged_in:

    def signup(username, password):
        users = load_users()
        if not username or not password:
            return False, "Username and password required"
        if username in users:
            return False, "Username already exists"
        users[username] = password
        save_users(users)
        return True, "Signup successful. Please login."

    def login(username, password):
        users = load_users()
        if username not in users:
            return False, "User not found"
        if users[username] != password:
            return False, "Incorrect password"
        return True, "Login successful"

    st.title("🔐 Login")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            ok, msg = login(u.strip(), p)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = u.strip()
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        su = st.text_input("Create Username")
        sp = st.text_input("Create Password", type="password")
        if st.button("Signup"):
            ok, msg = signup(su.strip(), sp)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.stop()

# =========================================================
# ORIGINAL JACK.py DATA & LOGIC (UNCHANGED)
# =========================================================
FLASHCARD_FILE = "flashcards.json"


def load_flashcards():
    default_data = [
        {
            "subject": "Math",
            "front": "➗ Quadratic Formula",
            "back": "Solution for a quadratic equation $ax^2+bx+c=0$." + r'$$x=\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}$$'
        },
        {
            "subject": "Physics",
            "front": "🔬 Newton's Second Law",
            "back": "Force equals mass times acceleration." + r'$$F=ma$$'
        },
        {
            "subject": "Chemistry",
            "front": "⚛️ Ideal Gas Law",
            "back": "Gas pressure-volume relation." + r'$$PV=nRT$$'
        }
    ]

    if os.path.exists(FLASHCARD_FILE):
        try:
            with open(FLASHCARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_data
    return default_data


def save_flashcards(data):
    with open(FLASHCARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =========================================================
# FLASHCARD SESSION STATE (ORIGINAL)
# =========================================================
if "flashcards" not in st.session_state:
    st.session_state.flashcards = load_flashcards()

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "is_flipped" not in st.session_state:
    st.session_state.is_flipped = False

# =========================================================
# SIDEBAR (ORIGINAL + LOGOUT)
# =========================================================
st.sidebar.title("📚 Flashcard Quiz App")
st.sidebar.success(f"Logged in as {st.session_state.username}")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🔄 FORMULA Flashcards", "🛠️ Create Flashcards", "📋 Manage Flashcards", "🚪 Logout"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Flashcards:** {len(st.session_state.flashcards)}")

# =========================================================
# PAGE 1: FORMULA FLASHCARDS (ORIGINAL UI)
# =========================================================
if page == "🔄 FORMULA Flashcards":
    st.title("🔄 FORMULA Flashcards")
    st.markdown("Click the card to flip it!")

    card = st.session_state.flashcards[st.session_state.current_index]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Previous"):
            st.session_state.current_index = (st.session_state.current_index - 1) % len(st.session_state.flashcards)
            st.session_state.is_flipped = False

    with col3:
        if st.button("Next ▶"):
            st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.flashcards)
            st.session_state.is_flipped = False

    if st.button("Answer Key"):
        st.session_state.is_flipped = not st.session_state.is_flipped

    if not st.session_state.is_flipped:
        st.markdown(
            f"""
            <div style="
                background:#d9c4f1;
                padding:40px;
                border-radius:15px;
                text-align:center;
                box-shadow:0 4px 15px rgba(0,0,0,0.4);
                max-width:600px;
                margin:auto;">
                <h2>{card['front']}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.subheader("Solution:")
        st.markdown(card['back'])

    st.markdown(f"**Subject:** {card['subject']}")

# =========================================================
# PAGE 2: CREATE FLASHCARDS (ORIGINAL)
# =========================================================
elif page == "🛠️ Create Flashcards":
    st.title("🛠️ Create Your Own Flashcards")

    with st.form("create_flashcard_form"):
        subject = st.text_input("Subject")
        front = st.text_input("Front")
        back = st.text_area("Back")
        submitted = st.form_submit_button("➕ Add Flashcard")

        if submitted:
            if front.strip() and back.strip():
                st.session_state.flashcards.append(
                    {"subject": subject, "front": front, "back": back}
                )
                save_flashcards(st.session_state.flashcards)
                st.success("Flashcard added!")
                st.rerun()
            else:
                st.error("Fill both front and back")

# =========================================================
# PAGE 3: MANAGE FLASHCARDS (ORIGINAL FEATURES)
# =========================================================
elif page == "📋 Manage Flashcards":
    st.title("📋 Manage Flashcards")

    subjects = sorted(set(c['subject'] for c in st.session_state.flashcards))
    selected = st.selectbox("Filter by Subject", ["All"] + subjects)

    cards = st.session_state.flashcards
    if selected != "All":
        cards = [c for c in cards if c['subject'] == selected]

    grouped = {}
    for c in cards:
        grouped.setdefault(c['subject'], []).append(c)

    for subject, items in grouped.items():
        with st.expander(f"{subject} ({len(items)})"):
            for i, card in enumerate(items):
                idx = st.session_state.flashcards.index(card)
                st.markdown(card['front'])
                if st.button("Delete", key=f"del_{subject}_{i}"):
                    st.session_state.flashcards.pop(idx)
                    save_flashcards(st.session_state.flashcards)
                    st.rerun()

# =========================================================
# LOGOUT (ONLY ADDITION)
# =========================================================
elif page == "🚪 Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()
