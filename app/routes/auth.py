from flask import Blueprint, render_template, request, redirect
from flask import url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        additional_data = {}

        # 役割に応じた追加データの収集
        if role == 'student':
            additional_data['grade'] = request.form.get('grade')
            additional_data['subjects'] = request.form.getlist('subjects')
        elif role == 'teacher':
            additional_data['subjects'] = request.form.getlist('subjects')

        if not username or not password or not role:
            flash('すべてのフィールドを入力してください')
            return redirect(url_for('auth.register'))

        if User.get_by_username(username, role):
            flash('そのユーザー名は既に使用されています')
            return redirect(url_for('auth.register'))

        try:
            user = User.create_user(username, password, role, **additional_data)
            session['user_id'] = user.id
            session['role'] = user.role
            flash('登録が完了しました。ログインしてください。', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('ユーザー登録中にエラーが発生しました')
            print(e)
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # ロールも選択する形に変更

        if not username or not password or not role:
            flash('ユーザー名、パスワード、および役割を入力してください')
            return render_template('auth/login.html')

        user = User.get_by_username(username, role)
        if user:
            if check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['role'] = user.role

                if user.role == 'student':
                    return redirect(url_for('student.dashboard'))
                elif user.role == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
            else:
                flash('無効なパスワードです')
                return render_template('auth/login.html')
        else:
            flash('ユーザーが見つかりません')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('ログアウトしました')
    return redirect(url_for('auth.login'))

# ログイン必須のルートのためのデコレータ
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ログインが必要です')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ロール確認のデコレータ
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != role:
                flash('アクセスが拒否されました')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

