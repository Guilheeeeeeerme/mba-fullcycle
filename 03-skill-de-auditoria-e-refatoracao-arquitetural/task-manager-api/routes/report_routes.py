from flask import Blueprint, request, jsonify

from services.report_service import (
    create_category as create_category_service,
    delete_category as delete_category_service,
    list_categories as list_categories_service,
    summary_report as summary_report_service,
    update_category as update_category_service,
    user_report as user_report_service,
)

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    payload, status = summary_report_service()
    return jsonify(payload), status


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    payload, status = user_report_service(user_id)
    return jsonify(payload), status


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    payload, status = list_categories_service()
    return jsonify(payload), status


@report_bp.route('/categories', methods=['POST'])
def create_category():
    payload, status = create_category_service(request.get_json())
    return jsonify(payload), status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    payload, status = update_category_service(cat_id, request.get_json())
    return jsonify(payload), status


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    payload, status = delete_category_service(cat_id)
    return jsonify(payload), status
