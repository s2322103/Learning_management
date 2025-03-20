from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth import login_required, role_required
from app.models.schedule import ScheduleModel

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/get_all_student', methods=['GET'])
@login_required
@role_required('admin')
def get_all_student():
    try:
        requests = ScheduleModel.get_all_student_requests()
        return render_template('admin/admin_student_requests.html', requests=requests)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.dashboard'))
    except Exception as e:
        flash('生徒のリクエスト情報の取得中にエラーが発生しました。', 'error')
        return redirect(url_for('admin.dashboard'))
    
@admin_bp.route('/get_all_teacher', methods=['GET'])
@login_required
@role_required('admin')
def get_all_teacher():
    try:
        requests = ScheduleModel.get_all_teacher_requests()
        return render_template('admin/admin_teacher_schedules.html', requests=requests)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.dashboard'))
    except Exception as e:
        flash('講師のスケジュール情報の取得中にエラーが発生しました。', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/create_schedule', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_schedule():
    if request.method == 'POST':
        try:
            teacher_id = request.form.get('teacher_id')
            student_id = request.form.get('student_id')
            date = request.form.get('date')
            time_slot_id = request.form.get('time_slot_id')
            subject = request.form.get('subject')

            result = ScheduleModel.create_confirmed_schedule(teacher_id, student_id, date, time_slot_id, subject)
            flash(result['message'], 'success')
            return redirect(url_for('admin.get_schedules'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('admin.create_schedule'))
        except Exception as e:
            flash('スケジュールの確定中にエラーが発生しました。', 'error')
            return redirect(url_for('admin.create_schedule'))

    try:
        teachers = ScheduleModel.get_all_teachers()
        students = ScheduleModel.get_all_students()
        time_slots = ScheduleModel.get_all_time_slots()
        
        return render_template('admin/admin_create_schedule.html',
                             teachers=teachers,
                             students=students,
                             time_slots=time_slots)
    except Exception as e:
        flash('データの取得中にエラーが発生しました。', 'error')
        return redirect(url_for('admin.dashboard'))
    
@admin_bp.route('/get_schedule', methods=['GET'])
@login_required
@role_required('admin')
def get_schedule():
    try:
        role = 'admin'
        schedules = ScheduleModel.get_confirmed_schedules(None, role)
        return render_template('admin/admin_confirmed_schedules.html', schedules=schedules)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.dashboard'))
    
    except Exception as e:
        flash('確定済みスケジュールの取得中にエラーが発生しました。', 'error')
        return redirect(url_for('admin.dashboard'))

# @admin_bp.route('/schedules', methods=['GET'])
# @login_required
# @role_required('admin')
# def get_confirmed_schedules():
#     try:
#         user_id = request.args.get('user_id', type=int)
#         role = request.args.get('role')

#         if not user_id or not role:
#             flash('User ID and role are required', 'error')
#             return redirect(url_for('admin.dashboard'))

#         schedules = ScheduleModel.get_confirmed_schedules(user_id, role)
#         return render_template(
#             'admin_confirmed_schedules.html', 
#             schedules=schedules,
#             user_id=user_id,
#             role=role
#         )
#     except ValueError as e:
#         flash(str(e), 'error')
#         return redirect(url_for('admin.dashboard'))
#     except Exception as e:
#         flash('An error occurred while fetching schedules', 'error')
#         return redirect(url_for('admin.dashboard'))
    

@admin_bp.route('/update_schedule/<int:confirmed_schedule_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def update_schedule(confirmed_schedules_id):
    if request.method == 'POST':
        try:
            teacher_id = request.form.get('teacher_id')
            student_id = request.form.get('student_id')
            date = request.form.get('date')
            time_slot_id = request.form.get('time_slot_id')
            subject = request.form.get('subject')
            result = ScheduleModel.update_confirmed_schedule(confirmed_schedules_id, teacher_id, student_id, date, time_slot_id, subject)
            flash(result['message'], 'success')
            return redirect(url_for('admin.get_schedules'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('admin.update_schedule', confirmed_schedules_id=confirmed_schedules_id))    

        except Exception as e:
            flash('スケジュールの更新中にエラーが発生しました。', 'error')
            return redirect(url_for('admin.update_schedule', confirmed_schedules_id=confirmed_schedules_id)) 

    try:
        teachers = ScheduleModel.get_all_teachers()
        students = ScheduleModel.get_all_students()
        time_slots = ScheduleModel.get_all_time_slots()
        
        return render_template('admin/admin_update_schedule.html',
                             teachers=teachers,
                             students=students,
                             time_slots=time_slots)  
    except Exception as e:
        flash('データの取得中にエラーが発生しました。', 'error')
        return redirect(url_for('admin.dashboard'))    
    
    
# @admin_bp.route('/confirmed_schedules/<int:schedule_id>/delete', methods=['GET', 'POST'])
# @login_required
# @role_required('admin')
# def delete_confirmed_schedule(schedule_id):
#     try:
#         if request.method == 'POST':
#             result = ScheduleModel.delete_confirmed_schedule(schedule_id)
#             flash(result['message'], 'success')
#             return redirect(url_for('admin.get_confirmed_schedules'))

#     except ValueError as e:
#         flash(str(e), 'error')
#         return redirect(url_for('admin.delete_confirmed_schedule', schedule_id=schedule_id))
#     except Exception as e:
#         flash('An error occurred while deleting the schedule', 'error')
#         return redirect(url_for('admin.delete_confirmed_schedule', schedule_id=schedule_id))