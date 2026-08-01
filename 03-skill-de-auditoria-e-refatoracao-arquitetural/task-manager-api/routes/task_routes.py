from flask import Blueprint, request, jsonify

from services.task_service import (
    create_task as create_task_service,
    delete_task as delete_task_service,
    get_task as get_task_service,
    list_tasks as list_tasks_service,
    search_tasks as search_tasks_service,
    task_stats as task_stats_service,
    update_task as update_task_service,
)

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    payload, status = list_tasks_service()
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    payload, status = get_task_service(task_id)
    return jsonify(payload), status


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    payload, status = create_task_service(request.get_json())
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    payload, status = update_task_service(task_id, request.get_json())
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    payload, status = delete_task_service(task_id)
    return jsonify(payload), status


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    payload, status = search_tasks_service(request.args)
    return jsonify(payload), status


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    payload, status = task_stats_service()
    return jsonify(payload), status
