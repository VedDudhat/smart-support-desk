from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend import db, login_manager
from backend.models import Users

@login_manager.user_loader
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
        login_user(user, remember=True)

        return jsonify({
            'message': 'Logged in',
            'name': user.name,
            'user_id': user.id
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'}), 200


@auth_bp.route('/api/check_auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'name': current_user.name,
            'user_id': current_user.id
        }), 200
    else:
        return jsonify({'authenticated': False}), 401