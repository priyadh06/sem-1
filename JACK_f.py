import streamlit as st 
import json
import os
from datetime import datetime

# =========================================================
# STREAMLIT CONFIG (MUST BE FIRST STREAMLIT CALL)
# =========================================================
st.set_page_config(
    page_title="EduFlip",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# FILES
# =========================================================
USERS_FILE = "users.json"
FLASHCARD_FILE = "flashcards.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)

if not os.path.exists(FLASHCARD_FILE):
    with open(FLASHCARD_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

# =========================================================
# HELPERS
# =========================================================
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def load_flashcards():
    try:
        with open(FLASHCARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_flashcards(cards):
    with open(FLASHCARD_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2)

# =========================================================
# SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "flashcards" not in st.session_state:
    st.session_state.flashcards = load_flashcards()

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "is_flipped" not in st.session_state:
    st.session_state.is_flipped = False

# =========================================================
# LOGIN / SIGNUP
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

    st.title("🔐 Login to EduFlip")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            ok, msg = login(u.strip(), p)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = u.strip()
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        su = st.text_input("Create Username", key="signup_user")
        sp = st.text_input("Create Password", type="password", key="signup_pass")
        if st.button("Signup"):
            ok, msg = signup(su.strip(), sp)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("📚 EduFlip")
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
# PAGE: STUDY
# =========================================================
if page == "🔄 FORMULA Flashcards":
    st.title("🔄 FORMULA Flashcards")
    st.markdown("Click **Flip** to view the answer")

    if not st.session_state.flashcards:
        st.warning("No flashcards available. Create some first.")
        st.stop()

    idx = st.session_state.current_index % len(st.session_state.flashcards)
    card = st.session_state.flashcards[idx]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Previous"):
            st.session_state.current_index -= 1
            st.session_state.is_flipped = False

    with col3:
        if st.button("Next ▶"):
            st.session_state.current_index += 1
            st.session_state.is_flipped = False

    if st.button("Flip"):
        st.session_state.is_flipped = not st.session_state.is_flipped

    # ---- Flashcard UI (RESTORED FROM ORIGINAL JACK.py STYLE) ----
    if not st.session_state.is_flipped:
        st.markdown(
            f"""
            <div style="
                background:#d9c4f1;
                color:black;
                padding:40px;
                border-radius:15px;
                text-align:center;
                box-shadow:0 4px 15px rgba(0,0,0,0.4);
                max-width:600px;
                margin:auto;">
                <h2>{card['front']}</h2>
                <p style="opacity:0.7;">Click 'Answer Key' to see the solution</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                background:#fef3c7;
                color:black;
                padding:40px;
                border-radius:15px;
                box-shadow:0 4px 15px rgba(0,0,0,0.4);
                max-width:600px;
                margin:auto;">
                {card['back']}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(f"**Subject:** {card['subject']}")

# =========================================================
# PAGE: CREATE

# =========================================================
elif page == "🛠️ Create Flashcards":
    st.title("🛠️ Create Flashcards")

    with st.form("create_flashcard"):
        subject = st.text_input("Subject")
        front = st.text_input("Front")
        back = st.text_area("Back")
        submitted = st.form_submit_button("Add Flashcard")

        if submitted:
            if subject and front and back:
                st.session_state.flashcards.append({
                    "subject": subject,
                    "front": front,
                    "back": back
                })
                save_flashcards(st.session_state.flashcards)
                st.success("Flashcard added")
                st.rerun()
            else:
                st.error("Fill all fields")

# =========================================================
# PAGE: MANAGE
# =========================================================
elif page == "📋 Manage Flashcards":
    st.title("📋 Manage Flashcards")

    if not st.session_state.flashcards:
        st.info("No flashcards to manage")
        st.stop()

    for i, card in enumerate(list(st.session_state.flashcards)):
        with st.expander(card['front']):
            st.markdown(f"**Subject:** {card['subject']}")
            st.markdown(f"**Answer:** {card['back']}")
            if st.button("Delete", key=f"del_{i}"):
                st.session_state.flashcards.pop(i)
                save_flashcards(st.session_state.flashcards)
                st.rerun()

# =========================================================
# PAGE: LOGOUT
# =========================================================
elif page == "🚪 Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()
