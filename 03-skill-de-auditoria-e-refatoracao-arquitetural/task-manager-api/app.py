from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from database import db
from config import Config
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from utils.helpers import utc_now

app = Flask(__name__)

app.config.from_object(Config)

CORS(app)
db.init_app(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)

@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(utc_now())}

@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}

with app.app_context():
    db.create_all()


@app.errorhandler(HTTPException)
def handle_http_exception(exc):
    response = jsonify({'error': exc.description})
    response.status_code = exc.code or 500
    return response


@app.errorhandler(Exception)
def handle_unexpected_exception(exc):
    response = jsonify({'error': 'Erro interno'})
    response.status_code = 500
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
