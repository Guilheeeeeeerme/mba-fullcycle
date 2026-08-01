import re
from sqlalchemy import func

from database import db
from models.user import User
from models.task import Task
from services.auth_service import create_auth_token
from utils.helpers import serialize_user, serialize_task, utc_now


EMAIL_PATTERN = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
VALID_ROLES = ['user', 'admin', 'manager']
MIN_PASSWORD_LENGTH = 4


def list_users():
    users = User.query.all()
    task_counts = dict(
        db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all()
    )

    result = []
    for user in users:
        data = serialize_user(user, include_tasks=False)
        data['task_count'] = int(task_counts.get(user.id, 0))
        result.append(data)

    return result, 200


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    data = serialize_user(user, include_tasks=False)
    data['tasks'] = [serialize_task(task, include_related=False, include_overdue=True) for task in user.tasks]
    return data, 200


def create_user(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        return {'error': 'Nome é obrigatório'}, 400
    if not email:
        return {'error': 'Email é obrigatório'}, 400
    if not password:
        return {'error': 'Senha é obrigatória'}, 400
    if not re.match(EMAIL_PATTERN, email):
        return {'error': 'Email inválido'}, 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return {'error': 'Senha deve ter no mínimo 4 caracteres'}, 400
    if role not in VALID_ROLES:
        return {'error': 'Role inválido'}, 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return {'error': 'Email já cadastrado'}, 409

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        return serialize_user(user), 201
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao criar usuário'}, 500


def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        email = data['email']
        if not re.match(EMAIL_PATTERN, email):
            return {'error': 'Email inválido'}, 400

        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user_id:
            return {'error': 'Email já cadastrado'}, 409
        user.email = email

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return {'error': 'Senha muito curta'}, 400
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            return {'error': 'Role inválido'}, 400
        user.role = data['role']

    if 'active' in data:
        user.active = bool(data['active'])

    try:
        db.session.commit()
        return serialize_user(user), 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao atualizar'}, 500


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    try:
        for task in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(task)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'Usuário deletado com sucesso'}, 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao deletar'}, 500


def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = [serialize_task(task, include_related=False, include_overdue=True) for task in tasks]
    return result, 200


def login_user(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'error': 'Email e senha são obrigatórios'}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {'error': 'Credenciais inválidas'}, 401

    if not user.active:
        return {'error': 'Usuário inativo'}, 403

    return {
        'message': 'Login realizado com sucesso',
        'user': serialize_user(user),
        'token': create_auth_token(user),
    }, 200
