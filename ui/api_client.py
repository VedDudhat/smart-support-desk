import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:5000"


def api_request(method, endpoint, payload=None, params=None):
    url = BASE_URL + endpoint
    headers = {"Content-Type": "application/json"}

    if 'jwt_token' in st.session_state and st.session_state.jwt_token:
        headers["Authorization"] = f"Bearer {st.session_state.jwt_token}"

    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=payload, headers=headers, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
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
    if 'jwt_token' not in st.session_state:
        return False, None
    headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
    try:
        response = requests.get(BASE_URL + "/api/check_auth", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data.get("name")
        return False, None
    except:
        return False, None

def clear_session():
    if 'jwt_token' in st.session_state:
        del st.session_state.jwt_token
    if 'user' in st.session_state:
        del st.session_state.user