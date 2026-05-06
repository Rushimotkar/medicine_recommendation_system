"""
doctor_routes.py — Doctor portal blueprint for MediGuide
Import this in app.py: from doctor_routes import doctor_bp; app.register_blueprint(doctor_bp)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId
from datetime import datetime
from functools import wraps

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

# ── Injected from app.py via init_doctor_bp() ────────────────
_db = None

def init_doctor_bp(db):
    global _db
    _db = db


# ── Auth guard decorator ──────────────────────────────────────
def doctor_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('doctor_id'):
            flash('Please log in to access the Doctor Portal.')
            return redirect(url_for('doctor_login'))
        return f(*args, **kwargs)
    return decorated


def get_current_doctor():
    did = session.get('doctor_id')
    if not did:
        return None
    doc = _db.doctors.find_one({'_id': ObjectId(did)})
    if doc:
        doc['id'] = str(doc['_id'])
    return doc


# ── LOGIN ─────────────────────────────────────────────────────
@doctor_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('doctor_id'):
        return redirect(url_for('doctor.dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        doc = _db.doctors.find_one({'email': email, 'is_active': True})
        if doc and check_password_hash(doc['password'], password):
            session['doctor_id']   = str(doc['_id'])
            session['doctor_name'] = doc.get('name', 'Doctor')
            session['doctor_spec'] = doc.get('specialization', '')
            return redirect(url_for('doctor.dashboard'))
        flash('Invalid credentials or account inactive.')
    return render_template('doctor_login.html')


# ── LOGOUT ────────────────────────────────────────────────────
@doctor_bp.route('/logout')
def logout():
    session.pop('doctor_id', None)
    session.pop('doctor_name', None)
    session.pop('doctor_spec', None)
    flash('You have been logged out from the Doctor Portal.')
    return redirect(url_for('doctor.login'))


# ── MAIN DASHBOARD ────────────────────────────────────────────
@doctor_bp.route('/dashboard')
@doctor_login_required
def dashboard():
    doctor = get_current_doctor()
    if not doctor:
        session.clear()
        flash('Session expired or doctor not found.')
        return redirect(url_for('doctor.login'))
    
    did = doctor['id']

    today_str = datetime.utcnow().strftime('%Y-%m-%d')

    # 1. Today's queue
    today_queue = list(_db.consultations.find({
        'doctor_id': did, 'queue_type': 'today', 'consultation_date': today_str
    }).sort('slot_number', 1))

    # Summary counts
    counts = {
        'total'      : len(today_queue),
        'waiting'    : sum(1 for c in today_queue if c['status'] == 'Waiting'),
        'in_progress': sum(1 for c in today_queue if c['status'] == 'In Progress'),
        'completed'  : sum(1 for c in today_queue if c['status'] == 'Completed'),
        'no_show'    : sum(1 for c in today_queue if c['status'] == 'No-Show'),
    }

    # 3. Pending / awaiting
    pending = list(_db.consultations.find({'doctor_id': did, 'queue_type': 'pending'}))

    # 4. Referrals
    referrals = list(_db.referrals.find({'to_doctor_id': did}).sort('referral_date', -1))

    # 5. Follow-ups
    followups = list(_db.consultations.find({'doctor_id': did, 'queue_type': 'followup'}).sort('follow_up_date', 1))

    # 6. IPD requests
    ipd_requests = list(_db.ipd_requests.find({'to_doctor_id': did}).sort('request_datetime', -1))

    # 7. Completed history
    history = list(_db.consultations.find({
        'doctor_id': did, 'queue_type': 'today', 'status': 'Completed'
    }).sort('consultation_date', -1).limit(20))

    # 8. Emergency / walk-ins
    emergency = list(_db.consultations.find({'doctor_id': did, 'queue_type': 'emergency'}))

    # 9. Notifications
    notifications = list(_db.doctor_notifications.find({'doctor_id': did}).sort('created_at', -1).limit(10))
    unread_count = sum(1 for n in notifications if not n['is_read'])

    # Stringify _id for all lists
    for lst in [today_queue, pending, referrals, followups, ipd_requests, history, emergency, notifications]:
        for item in lst:
            item['id'] = str(item['_id'])

    return render_template(
        'doctor_dashboard.html',
        doctor       = doctor,
        today_queue  = today_queue,
        counts       = counts,
        pending      = pending,
        referrals    = referrals,
        followups    = followups,
        ipd_requests = ipd_requests,
        history      = history,
        emergency    = emergency,
        notifications = notifications,
        unread_count = unread_count
    )


# ── PATIENT DETAIL (modal/AJAX) ───────────────────────────────
@doctor_bp.route('/patient/<consult_id>')
@doctor_login_required
def patient_detail(consult_id):
    doctor = get_current_doctor()
    consult = _db.consultations.find_one({'_id': ObjectId(consult_id), 'doctor_id': doctor['id']})
    if not consult:
        flash('Patient not found or access denied.')
        return redirect(url_for('doctor.dashboard'))
    consult['id'] = str(consult['_id'])
    # Past consultations for same patient
    past = list(_db.consultations.find({
        'doctor_id': doctor['id'],
        'patient_name': consult['patient_name'],
        'status': 'Completed',
        '_id': {'$ne': consult['_id']}
    }).sort('consultation_date', -1).limit(5))
    for p in past:
        p['id'] = str(p['_id'])
    return render_template('doctor_patient.html', doctor=doctor, consult=consult, past=past)


# ── SAVE NOTES / PRESCRIPTION ─────────────────────────────────
@doctor_bp.route('/patient/<consult_id>/save', methods=['POST'])
@doctor_login_required
def save_consult(consult_id):
    doctor = get_current_doctor()
    notes        = request.form.get('doctor_notes', '')
    diagnosis    = request.form.get('diagnosis', '')
    prescription = request.form.get('prescription', '')
    investigation= request.form.get('investigation', '')
    follow_up    = request.form.get('follow_up_date', '')
    new_status   = request.form.get('status', 'In Progress')

    # Fetch consult to get user_id
    consult = _db.consultations.find_one({'_id': ObjectId(consult_id)})
    
    _db.consultations.update_one(
        {'_id': ObjectId(consult_id), 'doctor_id': doctor['id']},
        {'$set': {
            'doctor_notes': notes,
            'diagnosis': diagnosis,
            'prescription_text': prescription,
            'investigation_requests': [i.strip() for i in investigation.split('\n') if i.strip()],
            'follow_up_date': follow_up,
            'status': new_status,
            'prescription_issued': bool(prescription),
            'follow_up_scheduled': bool(follow_up),
            'updated_at': datetime.utcnow(),
        }}
    )

    # Notify patient if completed
    if new_status == 'Completed' and consult.get('user_id'):
        _db.patient_notifications.insert_one({
            "user_id": consult['user_id'],
            "message": f"Your consultation with Dr. {doctor['name']} is complete. You can now view your prescription and clinical notes.",
            "type": "success",
            "is_read": False,
            "created_at": datetime.utcnow()
        })

    flash('Consultation saved successfully.')
    return redirect(url_for('doctor.dashboard'))


# ── UPDATE REFERRAL STATUS ─────────────────────────────────────
@doctor_bp.route('/referral/<ref_id>/status', methods=['POST'])
@doctor_login_required
def update_referral(ref_id):
    status = request.form.get('status')
    _db.referrals.update_one({'_id': ObjectId(ref_id)}, {'$set': {'status': status}})
    return redirect(url_for('doctor.dashboard') + '#referrals')


# ── UPDATE IPD RESPONSE ───────────────────────────────────────
@doctor_bp.route('/ipd/<ipd_id>/seen', methods=['POST'])
@doctor_login_required
def mark_ipd_seen(ipd_id):
    _db.ipd_requests.update_one({'_id': ObjectId(ipd_id)}, {'$set': {'response_status': 'Seen'}})
    return redirect(url_for('doctor.dashboard') + '#ipd')


# ── UPDATE CONSULTATION STATUS (quick action) ─────────────────
@doctor_bp.route('/consult/<consult_id>/status', methods=['POST'])
@doctor_login_required
def update_status(consult_id):
    doctor = get_current_doctor()
    new_status = request.form.get('status')
    _db.consultations.update_one(
        {'_id': ObjectId(consult_id), 'doctor_id': doctor['id']},
        {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
    )
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/notifications/read', methods=['POST'])
@doctor_login_required
def mark_notifications_read():
    doctor = get_current_doctor()
    _db.doctor_notifications.update_many(
        {'doctor_id': doctor['id'], 'is_read': False},
        {'$set': {'is_read': True}}
    )
    return jsonify({'success': True})

# ── APPOINTMENT ACTIONS (Accept/Reschedule/Cancel) ───────────
@doctor_bp.route('/appointment/<apt_id>/accept', methods=['POST'])
@doctor_login_required
def accept_appointment(apt_id):
    doctor = get_current_doctor()
    apt = _db.consultations.find_one({'_id': ObjectId(apt_id)})
    if not apt: return redirect(url_for('doctor.dashboard'))
    
    _db.consultations.update_one(
        {'_id': ObjectId(apt_id)},
        {'$set': {'status': 'Waiting', 'confirmed': True}}
    )
    
    # Notify patient
    _db.patient_notifications.insert_one({
        "user_id": apt['user_id'],
        "message": f"Your appointment with {doctor['name']} has been ACCEPTED.",
        "type": "success",
        "is_read": False,
        "created_at": datetime.utcnow()
    })
    
    flash("Appointment accepted.")
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/appointment/<apt_id>/reschedule', methods=['POST'])
@doctor_login_required
def reschedule_appointment(apt_id):
    doctor = get_current_doctor()
    apt = _db.consultations.find_one({'_id': ObjectId(apt_id)})
    if not apt: return redirect(url_for('doctor.dashboard'))
    
    message = request.form.get('message')
    _db.consultations.update_one(
        {'_id': ObjectId(apt_id)},
        {'$set': {'status': 'Reschedule Requested', 'doctor_note': message}}
    )
    
    # Notify patient
    _db.patient_notifications.insert_one({
        "user_id": apt['user_id'],
        "message": f"Dr. {doctor['name']} requested a reschedule: {message}",
        "type": "warning",
        "is_read": False,
        "created_at": datetime.utcnow()
    })
    
    flash("Reschedule request sent to patient.")
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/appointment/<apt_id>/cancel', methods=['POST'])
@doctor_login_required
def cancel_appointment(apt_id):
    doctor = get_current_doctor()
    apt = _db.consultations.find_one({'_id': ObjectId(apt_id)})
    if not apt: return redirect(url_for('doctor.dashboard'))
    
    _db.consultations.update_one(
        {'_id': ObjectId(apt_id)},
        {'$set': {'status': 'Cancelled'}}
    )
    
    # Notify patient
    _db.patient_notifications.insert_one({
        "user_id": apt['user_id'],
        "message": f"Your appointment with {doctor['name']} has been CANCELLED.",
        "type": "error",
        "is_read": False,
        "created_at": datetime.utcnow()
    })
    
    flash("Appointment cancelled.")
    return redirect(url_for('doctor.dashboard'))
