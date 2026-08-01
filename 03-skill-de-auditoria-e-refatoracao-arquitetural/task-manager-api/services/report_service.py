from datetime import timedelta

from sqlalchemy import case, func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import serialize_category, serialize_task, utc_now


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    status_counts = dict(
        db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    )
    priority_counts = dict(
        db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )

    overdue_list = []
    overdue_count = 0
    for task in Task.query.all():
        if task.is_overdue():
            overdue_count += 1
            overdue_list.append({
                'id': task.id,
                'title': task.title,
                'due_date': str(task.due_date),
                'days_overdue': (utc_now() - task.due_date).days,
            })

    seven_days_ago = utc_now() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago
    ).count()

    user_stats = []
    users = User.query.all()
    productivity_rows = (
        db.session.query(
            Task.user_id,
            func.count(Task.id).label('total_tasks'),
            func.sum(case((Task.status == 'done', 1), else_=0)).label('completed_tasks'),
        )
        .group_by(Task.user_id)
        .all()
    )
    productivity_map = {
        row.user_id: {
            'total_tasks': int(row.total_tasks or 0),
            'completed_tasks': int(row.completed_tasks or 0),
        }
        for row in productivity_rows
    }

    for user in users:
        stats = productivity_map.get(user.id, {'total_tasks': 0, 'completed_tasks': 0})
        total = stats['total_tasks']
        completed = stats['completed_tasks']
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    report = {
        'generated_at': str(utc_now()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': int(status_counts.get('pending', 0)),
            'in_progress': int(status_counts.get('in_progress', 0)),
            'done': int(status_counts.get('done', 0)),
            'cancelled': int(status_counts.get('cancelled', 0)),
        },
        'tasks_by_priority': {
            'critical': int(priority_counts.get(1, 0)),
            'high': int(priority_counts.get(2, 0)),
            'medium': int(priority_counts.get(3, 0)),
            'low': int(priority_counts.get(4, 0)),
            'minimal': int(priority_counts.get(5, 0)),
        },
        'overdue': {
            'count': overdue_count,
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }

    return report, 200


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()

    total = len(tasks)
    done = 0
    pending = 0
    in_progress = 0
    cancelled = 0
    overdue = 0
    high_priority = 0

    for task in tasks:
        if task.status == 'done':
            done += 1
        elif task.status == 'pending':
            pending += 1
        elif task.status == 'in_progress':
            in_progress += 1
        elif task.status == 'cancelled':
            cancelled += 1

        if task.priority <= 2:
            high_priority += 1

        if task.is_overdue():
            overdue += 1

    report = {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }
    }

    return report, 200


def list_categories():
    categories = Category.query.all()
    task_counts = dict(
        db.session.query(Task.category_id, func.count(Task.id)).group_by(Task.category_id).all()
    )

    result = []
    for category in categories:
        cat_data = serialize_category(category)
        cat_data['task_count'] = int(task_counts.get(category.id, 0))
        result.append(cat_data)

    return result, 200


def create_category(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    name = data.get('name')
    if not name:
        return {'error': 'Nome é obrigatório'}, 400

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
        return serialize_category(category), 201
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao criar categoria'}, 500


def update_category(cat_id, data):
    cat = Category.query.get(cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
        return serialize_category(cat), 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao atualizar'}, 500


def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404

    try:
        db.session.delete(cat)
        db.session.commit()
        return {'message': 'Categoria deletada'}, 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao deletar'}, 500
