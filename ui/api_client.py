import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:5000"

session = requests.Session()

def get_session():
    if 'requests_session' not in st.session_state:
        st.session_state.requests_session = requests.Session()
    return st.session_state.requests_session

def api_request(method, endpoint, payload=None, params=None):
    session = get_session()
    url = BASE_URL + endpoint
    try:

        if method.upper() == 'GET':
            response = session.get(url, params=params, timeout=10)
        elif method.upper() == 'POST':
            response = session.post(url, json=payload, timeout=10)
        elif method.upper() == 'PUT':
            response = session.put(url, json=payload, timeout=10)
        elif method.upper() == 'DELETE':
            response = session.delete(url, timeout=10)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None

        return response

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Please ensure the Flask server is running on port 5000.")
        return None
    except requests.exceptions.Timeout:
        st.error("⚠️ Request timed out. Backend is taking too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Request failed: {str(e)}")
        return None


def check_session():
    try:
        response = session.get(BASE_URL + "/api/check_auth", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data.get("name")
        return False, None
    except:
        return False, None

def clear_session():
    if 'requests_session' in st.session_state:
        del st.session_state.requests_session