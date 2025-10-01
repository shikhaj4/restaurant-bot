1) Installation & Setup

1.1) Clone the repository

git clone https://github.com/shikhaj4/restaurant-bot.git
cd restaurant-bot


1.2) Create and activate a virtual environment

python -m venv .venv
# Windows
.venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


1.3) Set Cohere API key

# Windows
set HF_API_KEY=cohere_api_key

2) How to Run the project

2.1) Start the FastAPI backend

uvicorn single_backend:app --reload


2.2) Start the Streamlit frontend

streamlit run streamlit_ui.py


3) Use the Chatbot

Open the Streamlit UI in your browser 

Enter queries like:

Find Italian restaurants in Whitefield
Suggest vegetarian food near Indiranagar