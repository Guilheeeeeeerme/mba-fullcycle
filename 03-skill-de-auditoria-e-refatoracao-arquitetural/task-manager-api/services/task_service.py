from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import serialize_task, utc_now


VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PRIORITY = 1
MAX_PRIORITY = 5


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    result = [serialize_task(task, include_related=True, include_overdue=True) for task in tasks]
    return result, 200


def get_task(task_id):
    task = Task.query.options(joinedload(Task.user), joinedload(Task.category)).get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    data = serialize_task(task, include_related=True, include_overdue=True)
    return data, 200


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    title = data.get('title')
    if not title:
        return {'error': 'Título é obrigatório'}, 400
    if len(title) < MIN_TITLE_LENGTH:
        return {'error': 'Título muito curto'}, 400
    if len(title) > MAX_TITLE_LENGTH:
        return {'error': 'Título muito longo'}, 400

    description = data.get('description', '')
    status = data.get('status', 'pending')
    if status not in VALID_STATUSES:
        return {'error': 'Status inválido'}, 400

    try:
        priority = int(data.get('priority', 3))
    except (TypeError, ValueError):
        return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        return {'error': 'Prioridade deve ser entre 1 e 5'}, 400

    user_id = data.get('user_id')
    if user_id not in (None, ''):
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return {'error': 'Usuário não encontrado'}, 404
        if not User.query.get(user_id):
            return {'error': 'Usuário não encontrado'}, 404
    else:
        user_id = None

    category_id = data.get('category_id')
    if category_id not in (None, ''):
        try:
            category_id = int(category_id)
        except (TypeError, ValueError):
            return {'error': 'Categoria não encontrada'}, 404
        if not Category.query.get(category_id):
            return {'error': 'Categoria não encontrada'}, 404
    else:
        category_id = None

    task = Task()
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        return serialize_task(task, include_related=True, include_overdue=True), 201
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao criar task'}, 500


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'title' in data:
        title = data['title']
        if len(title) < MIN_TITLE_LENGTH:
            return {'error': 'Título muito curto'}, 400
        if len(title) > MAX_TITLE_LENGTH:
            return {'error': 'Título muito longo'}, 400
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return {'error': 'Status inválido'}, 400
        task.status = data['status']

    if 'priority' in data:
        try:
            priority = int(data['priority'])
        except (TypeError, ValueError):
            return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
        if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
            return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
        task.priority = priority

    if 'user_id' in data:
        user_id = data['user_id']
        if user_id in (None, ''):
            task.user_id = None
        else:
            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                return {'error': 'Usuário não encontrado'}, 404
            if not User.query.get(user_id):
                return {'error': 'Usuário não encontrado'}, 404
            task.user_id = user_id

    if 'category_id' in data:
        category_id = data['category_id']
        if category_id in (None, ''):
            task.category_id = None
        else:
            try:
                category_id = int(category_id)
            except (TypeError, ValueError):
                return {'error': 'Categoria não encontrada'}, 404
            if not Category.query.get(category_id):
                return {'error': 'Categoria não encontrada'}, 404
            task.category_id = category_id

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return {'error': 'Formato de data inválido'}, 400
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = utc_now()

    try:
        db.session.commit()
        return serialize_task(task, include_related=True, include_overdue=True), 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao atualizar'}, 500


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    try:
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deletada com sucesso'}, 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao deletar'}, 500


def search_tasks(params):
    query = params.get('q', '')
    status = params.get('status', '')
    priority = params.get('priority', '')
    user_id = params.get('user_id', '')

    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category))

    if query:
        tasks = tasks.filter(
            or_(
                Task.title.ilike(f'%{query}%'),
                Task.description.ilike(f'%{query}%')
            )
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority:
        try:
            tasks = tasks.filter(Task.priority == int(priority))
        except (TypeError, ValueError):
            return {'error': 'Prioridade inválida'}, 400

    if user_id:
        try:
            tasks = tasks.filter(Task.user_id == int(user_id))
        except (TypeError, ValueError):
            return {'error': 'Usuário inválido'}, 400

    results = tasks.all()
    output = [serialize_task(task, include_related=True, include_overdue=True) for task in results]
    return output, 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    overdue_count = 0
    for task in Task.query.all():
        if task.is_overdue():
            overdue_count += 1

    stats = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }

    return stats, 200
