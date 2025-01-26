# 💬 Enhanced Gemini Chatbot

A feature-rich Streamlit chatbot using Google's Gemini Pro model.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### Requirements

To run this app, you'll need:
- A Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Python 3.7+

### Features

- Adjustable model parameters (temperature, max tokens)
- Custom system messages to control AI behavior
- Chat history management (clear, export)
- Error handling and loading states
- Responsive interface with sidebar controls

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Dependencies

- streamlit
- google-generativeai
