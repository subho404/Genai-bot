import streamlit as st
import back as bk

# Page title
st.title("TECHPIRATES BOT")

# Session state for conversation
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Get user input via text box
input_text = st.text_input('Enter your message')

# Button to trigger text-based interaction
if st.button('Generate') and input_text:
    output = bk.get_text(input_text)
    st.session_state.conversation.append({'sender': 'user', 'message': input_text})
    st.session_state.conversation.append({'sender': 'bot', 'message': output})

# Button to trigger voice-based interaction
if st.button("Speak"):
    input_text = bk.get_voice_input()
    if input_text:
        output = bk.get_text(input_text)
        st.write(f"**You (via voice):** {input_text}")
        st.write(f"**Bot:** {output}")
        bk.speak_text(output)
        st.session_state.conversation.append({'sender': 'user', 'message': input_text})
        st.session_state.conversation.append({'sender': 'bot', 'message': output})

# Add a summarization feature
if st.button("Summarize"):
    if input_text:
        summary = bk.summarize_text(input_text)
        st.write(f"**Summary:** {summary}")

# Display the conversation in chat bubble format
st.markdown("""
<style>
    .user-bubble { 
        background-color: #D1E8E4;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        max-width: 80%;
        color:#000000;
    }
    .bot-bubble {
        background-color: #F8F9FA;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        max-width: 80%;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Loop through the conversation history and display it
for message in st.session_state.conversation:
    if message['sender'] == 'user':
        st.markdown(f"<div class='user-bubble'><b>You:</b> {message['message']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'><b>Bot:</b> {message['message']}</div>", unsafe_allow_html=True)
