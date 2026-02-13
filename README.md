# Smart Support Desk
The Smart Support Desk is a full-stack ticketing system designed to help support teams manage customer issues efficiently. It features a robust Flask API backend for data management and a modern Streamlit frontend for the agent interface.

# 1. What This Service Does
This application serves as the central hub for support agents. It allows them to:

Manage Tickets: Create, view, update, and search for support tickets.
Customer Management: Register and maintain customer profiles.
Role-Based Access: Secure login for Agents and Admins.
Status Tracking: Track ticket lifecycle (Open -> In Progress -> Closed) and priority levels (Low, Medium, High).
Database Persistence: All data is securely stored in a MySQL database using SQLAlchemy ORM.

# 2. How to Set It Up Locally
Prerequisites
Python 3.10+
MySQL Server (or SQLite for testing)
pip (Python Package Manager)

# Installation Steps
Clone the Repository:
git clone <your-repo-url>
cd smart-support-desk

# Create a Virtual Environment:
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Dependencies:
pip install -r requirements.txt

# Configure Environment Variables: Create a .env file in the root directory and add your database credentials:
SECRET_KEY=your_secret_key_here
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@localhost/support_desk_db
# Or for SQLite: sqlite:///site.db

# Initialize the Database: Run the following commands to create the necessary tables:
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

#  How to Start the Application
You need to run the Backend and Frontend in two separate terminals.

Terminal 1: Start the Backend (Flask API)
This powers the API that the frontend talks to.
# Make sure your virtual environment is active
flask run --port 5000

Terminal 2: Start the Frontend (Streamlit App)
This launches the user interface for agents.
# Open a new terminal, activate venv, then run:
streamlit run ui/streamlit_ui.py

# Project Structure
smart-support-desk/
├── backend/             # Flask Backend Logic
│   ├── routes/          # API Endpoints (Auth, Tickets, Customers)
│   ├── models/          # Database Models (SQLAlchemy)
│   └── __init__.py      # App Factory
├── ui/                  # Streamlit Frontend
│   ├── streamlit_ui.py  # Main UI Entry Point
│   └── ...
├── migrations/          # Database Migration Scripts
├── requirements.txt     # Python Dependencies
├── .env                 # Secrets (Not committed to Git)
└── app.py               # Application Entry Point

# Tech Stack
Backend: Python, Flask, Flask-SQLAlchemy, Flask-Migrate
Frontend: Streamlit, Requests
Database: MySQL (Production) / SQLite (Dev)
