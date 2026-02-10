from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from backend import db
from backend.models import Users

def load_user(id):
    return Users.query.get(int(id))

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Username, Email, and Password are required'}), 400

    if not email.endswith('@company.com'):
        return jsonify({'error': 'Email Address is not Authorised'}), 403

    existing_user = Users.query.filter(
        (Users.username == username) | (Users.email == email)
    ).first()

    if existing_user:
        return jsonify({'error': 'Username or Email already taken'}), 409

    new_user = Users(
        username=username,
        email=email,
        name=name
    )
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Database Error: {e}")
        return jsonify({'error': 'Database error'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Users.query.filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'Logged in',
            'name': user.name,
            'user_id': user.id,
            'access_token': access_token
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/logout',methods=['POST'])
def logout():
    response = jsonify({'message': 'Logged out'})
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route('/api/check_auth', methods=['GET'])
@jwt_required
def check_auth():
    current_user_id = get_jwt_identity()
    user = Users.query.get(int(current_user_id))

    if user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'name': user.name,
            'user_id': user.id
        }), 200
    else:
        return jsonify({'authenticated': False}), 401