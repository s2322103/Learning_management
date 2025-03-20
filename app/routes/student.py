from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.routes.auth import login_required, role_required
from app.models.schedule import ScheduleModel

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    return render_template('student/dashboard.html')

@student_bp.route('/student_request', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_request():
    if request.method == 'POST':
        try:
            student_id = session.get('user_id')
            date = request.form.get('date')
            time_slot_id = request.form.get('time_slot_id')
            subject = request.form.get('subject')
            
            result = ScheduleModel.create_student_request(student_id, date, time_slot_id, subject)
            flash(result['message'], 'success')
            return redirect(url_for('student.dashboard'))
        
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('student.student_request'))
        
        except Exception as e:
            flash("リクエストの作成中にエラーが発生しました。", 'error')
            return redirect(url_for('student.student_request'))

    try:
        user_id = session.get('user_id')
        role = session.get('role')       
        time_slots = ScheduleModel.get_all_time_slots()
        subjects = ScheduleModel.get_available_subjects(user_id, role)
        return render_template('student/student_create_request.html', time_slots=time_slots, subjects=subjects)
    
    except Exception as e:
        flash("フォームデータの読み込み中にエラーが発生しました。", 'error')
        return redirect(url_for('student.dashboard'))
    

@student_bp.route('/student_confirmed_schedules', methods=['GET'])
@login_required
@role_required('student')
def student_confirmed_schedules():
    try:
        user_id = session.get('user_id')
        role = session.get('role')

        schedules = ScheduleModel.get_confirmed_schedules(user_id, role)
        return render_template('student/student_confirmed_schedules.html', schedules=schedules)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('student.dashboard'))
    
    except Exception as e:
        flash('スケジュールの取得中にエラーが発生しました。', 'error')
        return redirect(url_for('student.dashboard'))