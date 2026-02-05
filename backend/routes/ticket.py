from flask import Blueprint, request, jsonify
from flask_login import login_required
from backend import db
from backend.models import Tickets
from backend.schemas import TicketUpdateSchema
from pydantic import ValidationError

ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/api/view_tickets', methods=['GET'])
@login_required
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
        output.append({
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'customer_id': t.customer_id,
            'customer_name': t.customer.name if t.customer else "Unknown",
            'customer_email': t.customer.email if t.customer else ""

        })

    return jsonify(output), 200

@ticket_bp.route('/api/add_tickets', methods=['POST'])
@login_required
def add_ticket():
    data = request.get_json()

    if not data.get('title') or not data.get('customer_id'):
        return jsonify({'error': 'Title and customer_id are required'}), 400

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
        return jsonify({'message': 'Ticket created', 'id': new_ticket.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ticket_bp.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
@login_required
def update_ticket_route(ticket_id):
    ticket = Tickets.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    try:
        data = request.get_json()
        validated_data = TicketUpdateSchema(**data)
        update_dict = validated_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(ticket, key, value)

        db.session.commit()
        return jsonify({'message': 'Ticket updated successfully'}), 200
    except ValidationError as e:
        return jsonify({'error': e.errors()[0]['msg']}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# FIXED: Added @login_required decorator
@ticket_bp.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket_route(ticket_id):
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