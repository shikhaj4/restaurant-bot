Installation & Setup

Clone the repository

git clone https://github.com/shikhaj4/restaurant-bot.git
cd restaurant-bot


Create and activate a virtual environment

python -m venv .venv
# Windows
.venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Set Cohere API key

# Windows
set HF_API_KEY=cohere_api_key

How to Run

Start the FastAPI backend

uvicorn single_backend:app --reload


Start the Streamlit frontend

streamlit run streamlit_ui.py


Use the Chatbot

Open the Streamlit UI in your browser 

Enter queries like:

Find Italian restaurants in Whitefield
Suggest vegetarian food near Indiranagar