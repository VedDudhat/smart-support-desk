import pandas as pd
import streamlit as st
from api_client import check_session, api_request, clear_session
import time

st.set_page_config(
    page_title="Smart Support Desk",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state='expanded',
)

st.markdown("""
    <style>
    /* Main Background & Text */
    .stApp {
            background: linear-gradient(90deg, #00008A, #0000BD, #00D4FF);
            background-attachment: fixed;
            color: white;
        }

    div[data-testid="stForm"], div.css-1r6slb0 {
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            border: none;
            box-shadow: none;
        }

    section[data-testid="stSidebar"] {
        background-color: #2c3e50;
        color: white;
    }

    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }

    div[data-testid="stDataFrame"] {
        background-color: transparent;
        padding: 10px;
        border-radius: 10px;
        border: none;
    }

    h1, h2, h3 {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:5000"

if "user" not in st.session_state:
    st.session_state.user = None

if "current_view" not in st.session_state:
    st.session_state.current_view = "home"

if "active_menu" not in st.session_state:
    st.session_state.active_menu = "tickets"

# Check session on startup
if st.session_state.user is None:
    valid, name = check_session()
    if valid:
        st.session_state.user = name
        st.session_state.current_view = "dashboard"


def fetch_customers():
    try:
        resp = api_request('GET', '/api/view_customers')
        if resp and resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        st.error(f"Error fetching customers: {str(e)}")
        return []


def fetch_tickets(status_filter=None, priority_filter=None):
    try:
        params = {}
        if status_filter:
            params['status'] = ",".join(status_filter)
        if priority_filter:
            params['priority'] = ",".join(priority_filter)

        resp = api_request('GET', '/api/view_tickets', None, params)
        return resp
    except Exception as e:
        st.error(f"Error fetching tickets: {str(e)}")
        return None


def navigate_to(view):
    st.session_state.current_view = view
    st.rerun()


def home_view():
    c1, c2, c3 = st.columns([8, 1, 1])
    with c1:
        st.title("🚀 Smart Support Desk")
    with c2:
        if st.button("Log In ➜", use_container_width=True):
            navigate_to('login')
    with c3:
        if st.button("Register ➜", use_container_width=True):
            navigate_to('register')

    st.markdown("---")

    # Hero Content
    st.markdown(
        """
        <div style="text-align: center; padding: 40px;">
            <h1>Efficient Support Management</h1>
            <p style="font-size: 1.2rem; color: #fff;">
                Empowering agents to track, manage, and resolve tickets in real-time.
                Connects directly to your live database.
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("📊 **Real-time Data**\n\nFetch live ticket status and customer info instantly.")
    with c2:
        st.success("⚡ **Fast Actions**\n\nCreate, update, and resolve tickets with a few clicks.")
    with c3:
        st.warning("🛡️ **Secure Access**\n\nRole-based access control for agents and admins.")


def register_view():
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← Back"):
            navigate_to('home')
    with c2:
        with st.container(border=True):
            st.header("Create Account")
            with st.form("register_form"):
                name = st.text_input("Full Name")
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Register", use_container_width=True)

                if submitted:
                    payload = {"name": name, "username": username, "email": email, "password": password}

                    resp = api_request('POST', '/api/register', payload)

                    if resp is None:
                        st.error("❌ Could not connect to the server.")

                    elif resp.status_code == 201:
                        st.success("✅ Account created! Please log in.")
                        time.sleep(1)
                        navigate_to('login')
                        # NEW FIXED CODE
                        if resp.status_code == 201:
                            st.success("Registration successful! Please login.")
                        else:
                            try:

                                error_msg = resp.json().get('error', 'Registration failed')
                            except ValueError:
                                st.error(f"Server Error (Status {resp.status_code}):")
                                if resp.text.strip().startswith("<"):
                                    st.text("The backend returned an HTML error page instead of JSON.")
                                    with st.expander("See Backend Error Details"):
                                        st.code(resp.text[:500])
                                else:
                                    st.error(f"Error: {resp.text}")


def login_view():
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← Back"):
            navigate_to('home')
    with c2:
        with st.container(border=True):
            st.header("Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True)

                if submitted:
                    resp = api_request('POST', '/api/login', {"username": username, "password": password})

                    if resp is None:
                        st.error("❌ Could not connect to the server.")

                    elif resp.status_code == 200:
                        data = resp.json()
                        st.session_state.user = data.get('name')
                        st.session_state.jwt_token = data.get('access_token')
                        st.success(f"Welcome, {st.session_state.user}!")
                        time.sleep(0.5)
                        navigate_to('dashboard')

                    else:
                        error_msg = resp.json().get('error', 'Login failed')
                        st.error(f"❌ {error_msg}")

            st.markdown("Don't have an account?")
            if st.button("Create Account"):
                navigate_to('register')


def dashboard_view():
    c_title, c_user, c_refresh, c_logout = st.columns([5, 2, 1, 1])
    with c_title:
        st.subheader(f"👋 Welcome, {st.session_state.user}!")
    with c_refresh:
        if st.button("🔄 Refresh"):
            st.rerun()
    with c_logout:
        if st.button("Logout", type="primary"):
            if 'jwt_token' in st.session_state:
                del st.session_state.jwt_token
            st.session_state.user = None
            st.session_state.current_view = 'home'
            clear_session()
            st.rerun()

    st.markdown("---")

    # Dashboard Stats
    stats_resp = api_request('GET', '/api/dashboard/stats')

    if stats_resp and stats_resp.status_code == 200:
        stats = stats_resp.json()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Tickets", stats['total'], border=True)
        k2.metric("Open Tickets", stats['open'], delta="Active", delta_color="normal", border=True)
        k3.metric("Closed Tickets", stats['closed'], delta="Completed", delta_color="off", border=True)
        k4.metric("High Priority", stats['high_priority'], delta="Urgent", delta_color='inverse', border=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if stats['top_customers']:
            st.caption("🏆 Top 3 Customers by Ticket Volume")
            chart_data = pd.DataFrame(stats['top_customers'])
            st.bar_chart(
                chart_data,
                x="name",
                y="tickets",
                color="#faae7b",
                use_container_width=True
            )
        else:
            st.info("No customer data available yet for charts.")
    else:
        st.warning("⚠️ Could not load dashboard statistics. Is the backend running?")

    st.markdown("---")

    # Sidebar Operations Menu
    st.sidebar.title("🛠️ Operations")

    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("🎫 Tickets", use_container_width=True):
            st.session_state.active_menu = "tickets"
            st.rerun()
    with c2:
        if st.button("👥 Customers", use_container_width=True):
            st.session_state.active_menu = "customers"
            st.rerun()

    st.sidebar.markdown("---")

    selection = ""

    if st.session_state.active_menu == "tickets":
        st.sidebar.subheader("Ticket Ops")
        menu_options = ["View Tickets", "Create Ticket", "Update Ticket", "Delete Ticket"]
        selection = st.sidebar.radio("Select Action:", menu_options, key='ticket_ops')
    elif st.session_state.active_menu == "customers":
        st.sidebar.subheader("Customer Ops")
        menu_options = ["View Customers", "Create Customer", "Update Customer", 'Delete Customer']
        selection = st.sidebar.radio("Select Action:", menu_options, key='customer_ops')

    if selection == "View Tickets":
        view_ticket(selection)
    elif selection == "Create Ticket":
        create_ticket(selection)
    elif selection == "Update Ticket":
        update_ticket(selection)
    elif selection == "Delete Ticket":
        delete_ticket(selection)
    elif selection == "View Customers":
        view_customer(selection)
    elif selection == "Create Customer":
        create_customer(selection)
    elif selection == "Update Customer":
        update_customer(selection)
    elif selection == "Delete Customer":
        delete_customer(selection)


def view_ticket(selection):
    if selection == "View Tickets":
        st.header("📋 All Tickets")

        st.sidebar.subheader("🎯 Ticket Filters")

        status_filter = st.sidebar.multiselect(
            "Status",
            ["Open", "In Progress", "Closed"],
            key="status_filter"
        )

        priority_filter = st.sidebar.multiselect(
            "Priority",
            ["Low", "Medium", "High"],
            key="priority_filter"
        )

        resp = fetch_tickets(status_filter if status_filter else None,
                           priority_filter if priority_filter else None)

        if resp and resp.status_code == 200:
            tickets = resp.json()
            if tickets:
                df = pd.DataFrame(tickets)
                if 'customer_name' in df.columns:
                    df = df.rename(columns={
                        'id':"ID",
                        'title': 'Title',
                        'customer_name': 'Customer',
                        'status': 'Status',
                        'priority': 'Priority',
                        'description': 'Description'
                    })

                    cols_to_show = ['ID','Title', 'Customer', 'Status', 'Priority', 'Description']
                    st.dataframe(df[cols_to_show], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.info("No tickets match the selected filters.")
        elif resp and resp.status_code == 401:
            st.error("⚠️ Session expired. Please log in again.")
            time.sleep(2)
            st.session_state.user = None
            clear_session()
            navigate_to('login')
        else:
            st.error("Failed to load tickets. Please check if backend is running and you're logged in.")


def create_ticket(selection):
    if selection == "Create Ticket":
        st.header("➕ Create New Ticket")

        customers = fetch_customers()

        if not customers:
            st.warning("⚠️ No customers found. Please go to 'Customer Ops' and create a customer first.")
        else:
            customer_map = {
                f"{c['firstname']} {c.get('lastname', '')} ({c['email']})": c['id']
                for c in customers
            }

            with st.form("create_ticket_form"):
                title = st.text_input("Title")
                desc = st.text_area("Description")
                priority = st.selectbox("Priority", ["Low", "Medium", "High"])
                selected_label = st.selectbox("Assign to Customer", options=list(customer_map.keys()))
                selected_customer_id = customer_map[selected_label]
                submitted = st.form_submit_button("Create Ticket", use_container_width=True)

                if submitted:
                    if not title:
                        st.error("Title is required.")
                    elif not desc:
                        st.error("Description is required.")
                    else:
                        payload = {
                            "title": title,
                            "description": desc,
                            "priority": priority,
                            "customer_id": selected_customer_id
                        }

                        resp = api_request('POST', '/api/add_tickets', payload)

                        if resp and resp.status_code == 201:
                            st.success("✅ Ticket Created Successfully!")
                            time.sleep(1)
                            st.rerun()
                        elif resp and resp.status_code == 401:
                            st.error("⚠️ Session expired. Please log in again.")
                            time.sleep(2)
                            st.session_state.user = None
                            clear_session()
                            navigate_to('login')
                        else:
                            error_msg = resp.json().get('error', 'Unknown error') if resp else 'No response from server'
                            st.error(f"Failed to create ticket: {error_msg}")

def update_ticket(selection):
    if selection == "Update Ticket":
        st.header("✏️ Update Ticket")

        resp = fetch_tickets()
        customers = fetch_customers()

        if resp and resp.status_code == 200:
            tickets = resp.json()

            if not tickets:
                st.info("No tickets available to update.")
                return

            ticket_map = {
                f"{t['id']} - {t['title']}": t for t in tickets
            }

            selected_ticket_label = st.selectbox(
                "Select Ticket",
                list(ticket_map.keys()),
                key="update_ticket_selector"
            )

            ticket = ticket_map[selected_ticket_label]
            ticket_id = ticket['id']
            current_cust_id = ticket.get('customer_id')

            customer_map = {f"{c['firstname']} {c['lastname']} ({c['email']}) ({c['id']})": c for c in customers}
            cust_labels = list(customer_map.keys())

            current_cust_index = 0
            for i, label in enumerate(cust_labels):
                if customer_map[label]['id'] == current_cust_id:
                    current_cust_index = i
                    break

            with st.form("update_ticket_form"):
                status = st.selectbox(
                    "Status",
                    ["Open", "In Progress", "Closed"],
                    index=["Open", "In Progress", "Closed"].index(ticket["status"])
                )

                priority = st.selectbox(
                    "Priority",
                    ["LOW", "MEDIUM", "HIGH"],
                    index=["LOW", "MEDIUM", "HIGH"].index(ticket["priority"].upper())
                )

                selected_cust_label = st.selectbox(
                    "Assigned Customer",
                    options=cust_labels,
                    index=current_cust_index
                )

                desc = st.text_area("Description", value=ticket.get("description", ""))

                if st.form_submit_button("Update Ticket", use_container_width=True):
                    new_customer_id = customer_map[selected_cust_label]
                    payload = {
                        "status": status,
                        "priority": priority,
                        "description": desc,
                        'customer_id': new_customer_id['id'],
                        "email": new_customer_id['email']
                    }
                    update_resp = api_request('PUT', f'/api/tickets/{ticket_id}', payload)

                    if update_resp and update_resp.status_code == 200:
                        st.success("✅ Ticket Updated Successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    elif update_resp and update_resp.status_code == 401:
                        st.error("⚠️ Session expired. Please log in again.")
                        time.sleep(2)
                        st.session_state.user = None
                        clear_session()
                        navigate_to('login')
                    else:
                        try:
                            error_detail = update_resp.json().get('error', update_resp.text)
                            st.error(f"Backend Error: {error_detail}")
                        except:
                            st.error(f"Server crashed with status 500. Check Flask console logs.")
        elif resp and resp.status_code == 401:
            st.error("⚠️ Session expired. Please log in again.")
            time.sleep(2)
            st.session_state.user = None
            clear_session()
            navigate_to('login')
        else:
            st.error("Failed to load tickets. Please check if backend is running and you're logged in.")


def delete_ticket(selection):
    if selection == "Delete Ticket":
        st.header("🗑️ Delete Ticket")
        resp = fetch_tickets()

        if resp and resp.status_code == 200:
            tickets = resp.json()

            if not tickets:
                st.info("No tickets available to delete.")
                return

            ticket_map = {
                f"{t['id']} - {t['title']}": t['id']
                for t in tickets
            }

            selected_ticket = st.selectbox(
                "Select Ticket to Delete",
                list(ticket_map.keys()),
                key="delete_ticket_selector"
            )

            ticket_id = ticket_map[selected_ticket]
            confirm = st.checkbox("I understand this action is irreversible")

            if confirm and st.button("Confirm Delete", type="primary"):
                delete_resp = api_request('DELETE', f'/api/tickets/{ticket_id}')

                if delete_resp and delete_resp.status_code == 200:
                    st.success("✅ Ticket deleted successfully!")
                    time.sleep(0.5)
                    st.rerun()
                elif delete_resp and delete_resp.status_code == 401:
                    st.error("⚠️ Session expired. Please log in again.")
                    time.sleep(2)
                    st.session_state.user = None
                    clear_session()
                    navigate_to('login')
                else:
                    st.error("Delete failed. Please try again.")
        elif resp and resp.status_code == 401:
            st.error("⚠️ Session expired. Please log in again.")
            time.sleep(2)
            st.session_state.user = None
            clear_session()
            navigate_to('login')
        else:
            st.error("Failed to load tickets. Please check if backend is running and you're logged in.")


def view_customer(selection):
    if selection == "View Customers":
        st.header("👥 All Customers")

        customers = fetch_customers()

        if customers:
            df = pd.DataFrame(customers)
            desired_order = ['id', 'firstname','lastname', 'email', 'phone','company']

            cols_to_show = [c for c in desired_order if c in df.columns]
            st.dataframe(df[cols_to_show])
        else:
            st.info("No customers found.")


def create_customer(selection):
    if selection == "Create Customer":
        st.header("➕ Create New Customer")

        with st.form("create_customer_form"):
            firstname = st.text_input("Customer firstname")
            lastname  = st.text_input("Customer lastname")
            email = st.text_input("Email")
            company = st.text_input("Company")
            phone = st.text_input("Phone Number")
            submitted = st.form_submit_button("Create Customer", use_container_width=True)

            if submitted:
                if not firstname or not email:
                    st.error("firstname and Email are required.")
                else:
                    payload = {
                        "firstname": firstname,
                        'lastname': lastname,
                        "email": email,
                        "company": company,
                        'phone': phone,
                    }

                    resp = api_request('POST', '/api/add_customers', payload)

                    if resp and resp.status_code == 201:
                        st.success("✅ Customer Created Successfully!")
                        time.sleep(1)
                        st.rerun()
                    elif resp and resp.status_code == 409:
                        st.error("Email already exists.")
                    else:
                        error_msg = resp.json().get('error', 'Unknown error') if resp else 'No response from server'
                        st.error(f"Failed to create customer: {error_msg}")


def update_customer(selection):
    if selection == "Update Customer":
        st.header("✏️ Update Customer")

        customers = fetch_customers()

        if not customers:
            st.info("No customers available to update.")
            return

        customer_map = {
            f"{c['firstname']} {c['lastname']} ({c['email']})": c['firstname']
            for c in customers
        }

        selected_customer_label = st.selectbox(
            "Select Customer",
            list(customer_map.keys()),
            key="update_customer_selector"
        )

        customer_name = customer_map[selected_customer_label]
        selected_customer = next((c for c in customers if c['firstname'] == customer_name), None)

        if selected_customer:
            with st.form("update_customer_form"):
                email = st.text_input("Email", value=selected_customer.get('email', ''))
                phone = st.text_input("Phone Number", value=selected_customer.get('phone', ''))
                company = st.text_input("Company", value=selected_customer.get('company', ''))

                if st.form_submit_button("Update Customer", use_container_width=True):
                    payload = {
                        "email": email,
                        "company": company,
                        'phone': phone,
                    }

                    resp = api_request('PUT', f'/api/update_customers/{customer_name}', payload)

                    if resp and resp.status_code == 200:
                        st.success("✅ Customer Updated Successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        if resp is not None:
                            try:
                                error_msg = resp.json().get('error', f"Error code: {resp.status_code}")
                            except:
                                error_msg = f"Update Customer failed: Error Code {resp.status_code}"

                            st.error(f"❌ {error_msg}")


def delete_customer(selection):
    if selection == "Delete Customer":
        st.header("🗑️ Delete Customer")

        customers = fetch_customers()

        if not customers:
            st.info("No customers available to delete.")
            return

        customer_map = {
            f"{c['firstname']} {c['lastname']} ({c['email']})": c['firstname']
            for c in customers
        }

        selected_customer = st.selectbox(
            "Select Customer to Delete",
            list(customer_map.keys()),
            key="delete_customer_selector"
        )

        customer_name = customer_map[selected_customer]
        confirm = st.checkbox("I understand this action is irreversible")

        if confirm and st.button("Confirm Delete", type="primary"):
            resp = api_request('DELETE', f'/api/delete_customers/{customer_name}')

            if resp and resp.status_code == 200:
                st.success("✅ Customer deleted successfully!")
                time.sleep(0.5)
                st.rerun()
            else:
                error_msg = resp.json().get('error', 'Unknown error') if resp else 'No response from server'
                st.error(f"Delete failed: {error_msg}")


def route():
    if st.session_state.current_view == "home":
        home_view()
    elif st.session_state.current_view == "login":
        login_view()
    elif st.session_state.current_view == "register":
        register_view()
    elif st.session_state.current_view == "dashboard":
        if st.session_state.user:
            dashboard_view()
        else:
            st.warning("Please log in to access the dashboard.")
            navigate_to('login')

route()
