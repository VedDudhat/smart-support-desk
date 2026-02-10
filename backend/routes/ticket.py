import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models import Tickets, Customers
from backend import CRM_SERVICE_URL
ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/api/view_tickets', methods=['GET'])
@jwt_required()
def view_tickets():
    status = request.args.get('status')
    priority = request.args.get('priority')

    query = Tickets.query

    if status:
        status_list = status.split(',')
        query = query.filter(Tickets.status.in_(status_list))

    if priority:
        priority_list = priority.split(',')
        query = query.filter(Tickets.priority.in_(priority_list))

    tickets = query.all()

    output = []
    for t in tickets:
        display_name = "Unknown"
        if t.customer:
            fname = t.customer.firstname or ""
            lname = t.customer.lastname or ""
            display_name = f"{fname} {lname}".strip() or t.customer.email
        output.append({
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'customer_id': t.customer_id,
            'customer_name': t.customer.firstname or t.customer.lastname if t.customer else "Unknown",
            'customer_email': t.customer.email if t.customer else ""
        })

    return jsonify(output), 200


@ticket_bp.route('/api/add_tickets', methods=['POST'])
@jwt_required()
def add_ticket():

    data = request.get_json()

    # 1. Validation
    if not data.get('title') or not data.get('customer_id'):
        return jsonify({'error': 'Title and customer_id are required'}), 400

    # 2. Get customer details from database using customer_id
    customer = Customers.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found with that ID'}), 404

    # 3. Save to local MySQL database FIRST
    new_ticket = Tickets(
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'Medium'),
        status=data.get('status', 'Open'),
        customer_id=data['customer_id']
    )

    try:
        db.session.add(new_ticket)
        db.session.commit()

        local_ticket_id = new_ticket.id

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # 4. Sync to HubSpot CRM (via FastAPI service)
    # Now we use the customer's email to link the ticket to the contact
    hubspot_ticket_id = None
    hubspot_error = None
    linked_to_contact = False

    # Prepare payload for FastAPI CRM service
    crm_payload = {
        "title": data['title'],
        "description": data.get('description', 'No description provided'),
        "email": customer.email,
        "customer_firstname": customer.firstname,
        'customer_lastname': customer.lastname,
        "priority": data.get('priority', 'High').upper(),
        'category':'General'
    }

    try:
        # Call FastAPI CRM Integration Service
        response = requests.post(
            CRM_SERVICE_URL,
            json=crm_payload,
            timeout=10
        )

        if response.status_code == 201:
            crm_data = response.json()
            hubspot_ticket_id = crm_data.get('hubspot_ticket_id')
            linked_to_contact = crm_data.get('linked_to_contact', False)
        else:
            # Log error but don't fail the request
            hubspot_error = f"HubSpot sync failed: {response.text}"
            print(f"Warning: {hubspot_error}")

    except requests.exceptions.ConnectionError:
        hubspot_error = "CRM Integration Service is not running on port 8000"
        print(f"Warning: {hubspot_error}")
    except requests.exceptions.Timeout:
        hubspot_error = "CRM Integration Service timed out"
        print(f"Warning: {hubspot_error}")
    except Exception as e:
        hubspot_error = f"CRM sync error: {str(e)}"
        print(f"Warning: {hubspot_error}")

    # 5. Return success response
    response_data = {
        'message': 'Ticket created successfully',
        'ticket_id': local_ticket_id,
        'saved_to_database': True,
        'customer_email': customer.email,
        'customer_firstname': customer.firstname,
        'customer_lastname': customer.lastname,
    }

    if hubspot_ticket_id:
        response_data['saved_to_hubspot'] = True
        response_data['hubspot_ticket_id'] = hubspot_ticket_id
        response_data['linked_to_contact'] = linked_to_contact
    else:
        response_data['saved_to_hubspot'] = False
        if hubspot_error:
            response_data['hubspot_warning'] = hubspot_error

    return jsonify(response_data), 201


@ticket_bp.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    """Update a ticket"""
    ticket = Tickets.query.get(ticket_id)

    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404

    data = request.get_json()

    try:
        ticket.title = data.get('title', ticket.title)
        ticket.description = data.get('description', ticket.description)
        ticket.priority = data.get('priority', ticket.priority).upper()
        ticket.status = data.get('status', ticket.status)


        # Update customer_id if provided
        if 'customer_id' in data:
            # Verify customer exists
            customer = Customers.query.get(data['customer_id'])
            if customer:
                ticket.customer_id = data['customer_id']
            else:
                return jsonify({'error': 'Customer not found'}), 404


            db.session.commit()

            # 2. Sync to HubSpot if a HubSpot ID exists
            if ticket.hubspot_ticket_id:
                hubspot_payload = {
                    "title": ticket.title,
                    "description": ticket.description,
                    "priority": ticket.priority,
                    "status": ticket.status
                }
                crm_url = f"http://localhost:8000/integrate/ticket/{ticket.hubspot_ticket_id}"
                requests.patch(crm_url, json=hubspot_payload, timeout=5)
            return jsonify({"message": "Ticket updated locally and synced to CRM"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(ticket_id):
    """Delete a ticket"""
    ticket = Tickets.query.get(ticket_id)

    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    try:
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500