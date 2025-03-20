from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'bdc379578b35872eab61bce81abb1df6'

    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.teacher import teacher_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)

    return app