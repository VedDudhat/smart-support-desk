from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from backend import db
from backend.models import Tickets, Customers

dash_bp = Blueprint('dashboard', __name__)

@dash_bp.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    # 1. Scalar Counts
    total_tickets = Tickets.query.count()
    open_tickets = Tickets.query.filter(Tickets.status != 'Closed').count()
    closed_tickets = Tickets.query.filter_by(status='Closed').count()
    high_priority = Tickets.query.filter(Tickets.priority == 'High', Tickets.status != 'Closed').count()

    top_customers_query = db.session.query(
        Customers.firstname,
        Customers.lastname,
        func.count(Tickets.id).label('total')
    ).join(Tickets, Tickets.customer_id == Customers.id) \
        .group_by(Customers.id, Customers.firstname, Customers.lastname) \
        .order_by(func.count(Tickets.id).desc()) \
        .all()

    top_customers = [
        {
            "name": f"{fname} {lname}".strip(),
            "tickets": count
        }
        for fname, lname, count in top_customers_query
    ]

    return jsonify({
        "total": total_tickets,
        "open": open_tickets,
        "closed": closed_tickets,
        "high_priority": high_priority,
        "top_customers": top_customers
    }), 200

