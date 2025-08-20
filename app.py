# app.py
import streamlit as st
import requests
from datetime import datetime

# --- Gemini 2.5 Pro API ---
GEMINI_API_KEY = "AIzaSyDyCAiSvT3QKfz1IitaJUmw0a-gbahYRMw"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-2.5-pro:generateMessage"

# --- Jewelry catalog ---
PRODUCTS = {
    "Elegant Necklace": {"price": 499, "image": "https://i.ibb.co/6s8ZKxD/necklace.jpg"},
    "Classic Earrings Set": {"price": 299, "image": "https://i.ibb.co/0JfT7yv/earrings.jpg"},
    "Charm Bracelet": {"price": 199, "image": "https://i.ibb.co/3cxhW8L/bracelet.jpg"},
    "Premium Combo Pack": {"price": 799, "image": "https://i.ibb.co/FKJ2s7v/combo.jpg"}
}

# --- Function to generate AI response ---
def generate_response(user_input):
    messages = [{"author": "user", "content": [{"type": "text", "text": user_input}]}]
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": messages,
        "temperature": 0.7,
        "maxOutputTokens": 300
    }
    try:
        # verify=False for local testing only
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, verify=False)
        if response.status_code == 200:
            # Gemini returns a structured JSON
            return response.json()["candidates"][0]["content"][0]["text"]
        else:
            return f"Sorry, API returned status {response.status_code}"
    except requests.exceptions.SSLError:
        return "SSL Error: Could not verify API certificate. Check certifi or network."
    except Exception as e:
        return f"Error: {e}"

# --- Streamlit UI setup ---
st.set_page_config(page_title="💎 Luxury Jewelry Assistant", page_icon="💍", layout="wide")
st.markdown("<h1 style='text-align:center; color:#F44336;'>💎 Luxury Jewelry Assistant</h1>", unsafe_allow_html=True)

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cart" not in st.session_state:
    st.session_state.cart = {}

# --- Display chat messages ---
def display_chat():
    for msg in st.session_state.messages:
        timestamp = msg["time"].strftime("%H:%M")
        if msg["role"] == "user":
            st.markdown(
                f"<div style='background-color:#25D366; color:white; padding:10px; border-radius:15px; margin:5px 0; width:60%; float:right;'>"
                f"<strong>You [{timestamp}]:</strong><br>{msg['content']}</div>", unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background-color:#EDEDED; color:black; padding:10px; border-radius:15px; margin:5px 0; width:60%; float:left;'>"
                f"<strong>Bot [{timestamp}]:</strong><br>{msg['content']}</div>", unsafe_allow_html=True
            )
            # Show product suggestions with add-to-cart buttons
            for product_name, details in PRODUCTS.items():
                if product_name.lower() in msg['content'].lower():
                    col1, col2 = st.columns([1,2])
                    with col1:
                        st.image(details['image'], width=120)
                    with col2:
                        st.markdown(f"**{product_name}** - ₹{details['price']}")
                        button_key = f"cart_{product_name}_{len(st.session_state.messages)}"
                        if st.button(f"Add {product_name} to Cart", key=button_key):
                            if product_name in st.session_state.cart:
                                st.session_state.cart[product_name]["quantity"] += 1
                            else:
                                st.session_state.cart[product_name] = {"price": details['price'], "quantity": 1}

# --- Display chat ---
display_chat()

# --- Display mini-cart ---
if st.session_state.cart:
    st.markdown("### 🛒 Your Cart")
    total = 0
    for item, details in st.session_state.cart.items():
        subtotal = details["price"] * details["quantity"]
        total += subtotal
        st.markdown(f"{item} x {details['quantity']} = ₹{subtotal}")
    st.markdown(f"**Total: ₹{total}**")

# --- Chat input form ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...")
    submit_button = st.form_submit_button("Send")
    if submit_button and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input, "time": datetime.now()})
        # Generate bot response
        bot_response = generate_response(user_input)
        st.session_state.messages.append({"role": "bot", "content": bot_response, "time": datetime.now()})
        # Redisplay chat
        display_chat()
