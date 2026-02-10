import requests
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from backend.schemas import CustomerCreateSchema, CustomerUpdateSchema
from backend import db,CUSTOMER_SERVICE_URL
from backend.models import Customers

cust_bp = Blueprint('customer_bp', __name__)

@cust_bp.route('/api/view_customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    customers = Customers.query.all()
    output = []
    for c in customers:
        output.append({
            'id': c.id,
            'firstname': c.firstname,
            'lastname': c.lastname,
            'email': c.email,
            'company': c.company,
            'phone':c.phone,
        })
    return jsonify(output), 200

@cust_bp.route('/api/add_customers', methods=['POST'])
def create_customer():

    data = request.get_json()

    try:
        # 1. Validate with Pydantic
        validated = CustomerCreateSchema(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()[0]['msg']}), 400

    # Check if email already exists in local DB
    if Customers.query.filter_by(email=validated.email).first():
        return jsonify({"error": "Email already exists"}), 409

    # 2. Save to local MySQL database FIRST
    new_customer = Customers(
        firstname=validated.firstname,
        lastname=validated.lastname,
        email=validated.email,
        company=validated.company,
        phone=validated.phone
    )

    try:
        db.session.add(new_customer)
        db.session.commit()

        local_customer_id = new_customer.id

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    # 3. Sync to HubSpot CRM as Contact (via FastAPI service)
    hubspot_contact_id = None
    hubspot_error = None

    # Prepare payload for FastAPI CRM service
    crm_payload = {
        "email": validated.email,
        "firstname": validated.firstname,
        "lastname": validated.lastname,
        "company": validated.company if validated.company else None,
        'phone': validated.phone
    }

    try:
        # Call FastAPI CRM Integration Service
        response = requests.post(
            CUSTOMER_SERVICE_URL,
            json=crm_payload,
            timeout=10
        )

        if response.status_code == 201:
            crm_data = response.json()
            hubspot_contact_id = crm_data.get('hubspot_contact_id')
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

    # 4. Return success response
    response_data = {
        'message': 'Customer created successfully',
        'customer_id': local_customer_id,
        'saved_to_database': True,
    }

    if hubspot_contact_id:
        response_data['saved_to_hubspot'] = True
        response_data['hubspot_contact_id'] = hubspot_contact_id
    else:
        response_data['saved_to_hubspot'] = False
        if hubspot_error:
            response_data['hubspot_warning'] = hubspot_error

    return jsonify(response_data), 201


@cust_bp.route('/api/get_customers/<string:name>', methods=['GET'])
def get_customer_by_name(name):
    """Get single customer by name"""
    customer = Customers.query.filter_by(name=name).first()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'email': customer.email,
        'company': customer.company
    }), 200

@cust_bp.route('/api/update_customers/<string:name>', methods=['PUT'])
def update_customer_by_name(name):
    customer = Customers.query.filter_by(name=name).first()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    data = request.get_json()

    try:
        # Pydantic validates the data
        validated_data = CustomerUpdateSchema(**data)

        # Convert to dictionary, ignoring unset fields
        update_dict = validated_data.model_dump(exclude_unset=True)

        if not update_dict:
            return jsonify({"error": "No changes detected"}), 400

        # Update the database object
        for key, value in update_dict.items():
            setattr(customer, key, value)

        db.session.commit()

        # Optional: Sync update to HubSpot
        # You can add HubSpot update logic here if needed

        return jsonify({"message": "Customer updated successfully"}), 200

    except ValidationError as e:
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
        return jsonify({"message": "Customer deleted from local database"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Cannot delete. Customer might have linked tickets."}), 500