from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from backend.schemas import CustomerCreateSchema ,CustomerUpdateSchema
from backend import db
from backend.models import Customers
cust_bp = Blueprint('customer_bp', __name__)

@cust_bp.route('/api/view_customers', methods=['GET'])
def get_customers():
    customers = Customers.query.all()
    output = []
    for c in customers:
        output.append({
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'company': c.company
        })
    return jsonify(output), 200


# 2. CREATE CUSTOMER
@cust_bp.route('/api/add_customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    validate = CustomerCreateSchema.validate(data)

    if Customers.query.filter_by(email=validate.email).first():
        return jsonify({"error": "Email already exists"}), 409

    new_customer = Customers(
        name=validate.name,
        email=validate.email,
        company=validate.company
    )

    try:
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Customer created"}), 201
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': e.errors()[0]['msg']}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 3. GET SINGLE CUSTOMER BY NAME
@cust_bp.route('/api/get_customers/<string:name>', methods=['GET'])
def get_customer_by_name(name):
    customer = Customers.query.filter_by(name=name).first()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'company': customer.company
    }), 200


def update_customer_by_name(name):
    customer = Customers.query.filter_by(name=name).first()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    data = request.get_json()

    try:
        # Pydantic validates the data here
        validated_data = CustomerUpdateSchema(**data)

        # Convert to dictionary, ignoring fields the user didn't change
        update_dict = validated_data.model_dump(exclude_unset=True)

        if not update_dict:
            return jsonify({"error": "No changes detected"}), 400

        # Update the database object
        for key, value in update_dict.items():
            setattr(customer, key, value)

        db.session.commit()
        return jsonify({"message": "Customer updated successfully"}), 200

    except ValidationError as e:
        # Capture the specific error message (e.g., "Name cannot contain numbers")
        error_msg = e.errors()[0]['msg']
        return jsonify({"error": error_msg}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@cust_bp.route('/api/delete_customers/<string:name>', methods=['DELETE'])
def delete_customer_by_name(name):
    customer = Customers.query.filter_by(name=name).first()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Cannot delete. Customer might have linked tickets."}), 500