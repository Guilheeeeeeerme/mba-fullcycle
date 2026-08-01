from flask import Blueprint, request, jsonify

from services.user_service import (
    create_user as create_user_service,
    delete_user as delete_user_service,
    get_user as get_user_service,
    get_user_tasks as get_user_tasks_service,
    list_users as list_users_service,
    login_user as login_user_service,
    update_user as update_user_service,
)

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    payload, status = list_users_service()
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    payload, status = get_user_service(user_id)
    return jsonify(payload), status


@user_bp.route('/users', methods=['POST'])
def create_user():
    payload, status = create_user_service(request.get_json())
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    payload, status = update_user_service(user_id, request.get_json())
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    payload, status = delete_user_service(user_id)
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    payload, status = get_user_tasks_service(user_id)
    return jsonify(payload), status


@user_bp.route('/login', methods=['POST'])
def login():
    payload, status = login_user_service(request.get_json())
    return jsonify(payload), status
