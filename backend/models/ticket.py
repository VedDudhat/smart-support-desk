from datetime import datetime
from backend import db

class Tickets(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True)
    description = db.Column(db.String(256), index=True, nullable=False)
    status = db.Column(db.String(50), index=True, nullable=False, default='Open')
    priority = db.Column(db.String(50), index=True, nullable=False, default='Medium')
    category = db.Column(db.String(50), index=True, default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    customer = db.relationship('Customers', backref='tickets', lazy=True)
    hubspot_ticket_id = db.Column(db.String(128), nullable=True)