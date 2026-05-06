import os

app_path = r"c:\Users\hp\OneDrive\Attachments\Desktop\medico - Copy\app.py"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# Chunk 1
c1_old = """from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename"""
c1_new = """from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename"""
content = content.replace(c1_old, c1_new)

# Chunk 2
c2_old = """# Database Configuration (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:adii1118@localhost:5432/medico')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('artifacts', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    records = db.relationship('MedicalRecord', backref='user', lazy=True)

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class SymptomHistory(db.Model):
    __tablename__ = 'symptom_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symptoms = db.Column(db.String(255))
    severity = db.Column(db.String(50))
    predicted_medicine = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class MedicationReminder(db.Model):
    __tablename__ = 'medication_reminders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medicine_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    time = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class HealthTip(db.Model):
    __tablename__ = 'health_tips'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()
    # Seed health tips if empty or fewer than 10
    if HealthTip.query.count() < 10:
        HealthTip.query.delete() # Clear existing to avoid duplicates when adding the new set
        tips = [
            HealthTip(title="Stay Hydrated", content="Drinking enough water every day is crucial for many reasons: to regulate body temperature, keep joints lubricated, prevent infections, deliver nutrients to cells, and keep organs functioning properly. Being well-hydrated also improves sleep quality, cognition, and mood."),
            HealthTip(title="Benefits of Walking", content="Walking for 30 minutes a day or more on most days of the week is a great way to improve or maintain your overall health. If you can't manage 30 minutes a day, remember even short walks are better than none at all."),
            HealthTip(title="Healthy Sleep Habits", content="A healthy adult needs between 7 and 9 hours of sleep per night. Going to bed and waking up at the same time every day can help improve your sleep quality."),
            HealthTip(title="Eat More Fiber", content="Dietary fiber, found mainly in fruits, vegetables, whole grains and legumes, is probably best known for its ability to prevent or relieve constipation. But foods containing fiber can provide other health benefits as well, such as helping to maintain a healthy weight and lowering your risk of diabetes, heart disease and some types of cancer."),
            HealthTip(title="Mindful Eating", content="Mindful eating is about using mindfulness to reach a state of full attention to your experiences, cravings, and physical cues when eating. This practice helps you learn to hear what your body is telling you about hunger and satisfaction."),
            HealthTip(title="Limit Added Sugars", content="Consuming too much added sugar is linked to an increased risk of weight gain, obesity, type 2 diabetes, and heart disease. Check food labels and try to choose products with little to no added sugar."),
            HealthTip(title="Regular Screen Breaks", content="To prevent eye strain from digital devices, follow the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for at least 20 seconds. Also, remember to blink frequently to keep your eyes moist."),
            HealthTip(title="Strength Training", content="Incorporating strength training exercises at least two days a week is essential. It helps increase muscle mass, strengthens your bones, and boosts your metabolism, which can help with weight management."),
            HealthTip(title="Practice Deep Breathing", content="Taking a few minutes each day to practice deep breathing can significantly reduce stress levels. It signals your nervous system to calm down, lowers your heart rate, and can help reduce blood pressure."),
            HealthTip(title="Don't Skip Breakfast", content="Eating a nutritious breakfast kick-starts your metabolism and provides you with the energy you need to focus and be productive throughout the morning. Opt for protein and whole grains over sugary pastries.")
        ]
        db.session.bulk_save_objects(tips)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_emergency_contacts():
    if current_user.is_authenticated:
        contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
        return dict(global_emergency_contacts=contacts)
    return dict(global_emergency_contacts=[])"""

c2_new = """# Database Configuration (MongoDB)
app.config['UPLOAD_FOLDER'] = os.path.join('artifacts', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client['medico']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password = user_data.get('password')

# Seed health tips if empty or fewer than 10
if db.health_tips.count_documents({}) < 10:
    db.health_tips.delete_many({}) # Clear existing to avoid duplicates when adding the new set
    tips = [
        {"title": "Stay Hydrated", "content": "Drinking enough water every day is crucial for many reasons: to regulate body temperature, keep joints lubricated, prevent infections, deliver nutrients to cells, and keep organs functioning properly. Being well-hydrated also improves sleep quality, cognition, and mood.", "date_added": datetime.utcnow()},
        {"title": "Benefits of Walking", "content": "Walking for 30 minutes a day or more on most days of the week is a great way to improve or maintain your overall health. If you can't manage 30 minutes a day, remember even short walks are better than none at all.", "date_added": datetime.utcnow()},
        {"title": "Healthy Sleep Habits", "content": "A healthy adult needs between 7 and 9 hours of sleep per night. Going to bed and waking up at the same time every day can help improve your sleep quality.", "date_added": datetime.utcnow()},
        {"title": "Eat More Fiber", "content": "Dietary fiber, found mainly in fruits, vegetables, whole grains and legumes, is probably best known for its ability to prevent or relieve constipation. But foods containing fiber can provide other health benefits as well, such as helping to maintain a healthy weight and lowering your risk of diabetes, heart disease and some types of cancer.", "date_added": datetime.utcnow()},
        {"title": "Mindful Eating", "content": "Mindful eating is about using mindfulness to reach a state of full attention to your experiences, cravings, and physical cues when eating. This practice helps you learn to hear what your body is telling you about hunger and satisfaction.", "date_added": datetime.utcnow()},
        {"title": "Limit Added Sugars", "content": "Consuming too much added sugar is linked to an increased risk of weight gain, obesity, type 2 diabetes, and heart disease. Check food labels and try to choose products with little to no added sugar.", "date_added": datetime.utcnow()},
        {"title": "Regular Screen Breaks", "content": "To prevent eye strain from digital devices, follow the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for at least 20 seconds. Also, remember to blink frequently to keep your eyes moist.", "date_added": datetime.utcnow()},
        {"title": "Strength Training", "content": "Incorporating strength training exercises at least two days a week is essential. It helps increase muscle mass, strengthens your bones, and boosts your metabolism, which can help with weight management.", "date_added": datetime.utcnow()},
        {"title": "Practice Deep Breathing", "content": "Taking a few minutes each day to practice deep breathing can significantly reduce stress levels. It signals your nervous system to calm down, lowers your heart rate, and can help reduce blood pressure.", "date_added": datetime.utcnow()},
        {"title": "Don't Skip Breakfast", "content": "Eating a nutritious breakfast kick-starts your metabolism and provides you with the energy you need to focus and be productive throughout the morning. Opt for protein and whole grains over sugary pastries.", "date_added": datetime.utcnow()}
    ]
    db.health_tips.insert_many(tips)

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except Exception:
        pass
    return None

@app.context_processor
def inject_emergency_contacts():
    if current_user.is_authenticated:
        contacts = list(db.emergency_contacts.find({'user_id': current_user.id}))
        for c in contacts:
            c['id'] = str(c['_id'])
        return dict(global_emergency_contacts=contacts)
    return dict(global_emergency_contacts=[])"""
content = content.replace(c2_old, c2_new)

c3_old = """        # Save to SymptomHistory
        new_history = SymptomHistory(
            user_id=current_user.id,
            symptoms=request.form.get("symptoms"),
            severity=request.form.get("severity"),
            predicted_medicine=result["medicine"]
        )
        db.session.add(new_history)
        db.session.commit()"""
c3_new = """        # Save to SymptomHistory
        new_history = {
            'user_id': current_user.id,
            'symptoms': request.form.get("symptoms"),
            'severity': request.form.get("severity"),
            'predicted_medicine': result["medicine"],
            'date_added': datetime.utcnow()
        }
        db.symptom_history.insert_one(new_history)"""
content = content.replace(c3_old, c3_new)

c4_old = """        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
            
        new_user = User(name=name, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)"""
c4_new = """        user = db.users.find_one({'email': email})
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
            
        new_user_data = {
            'name': name, 
            'email': email, 
            'password': generate_password_hash(password, method='pbkdf2:sha256')
        }
        res = db.users.insert_one(new_user_data)
        new_user_data['_id'] = res.inserted_id
        
        login_user(User(new_user_data))"""
content = content.replace(c4_old, c4_new)

c5_old = """        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
            
        login_user(user)"""
c5_new = """        user_data = db.users.find_one({'email': email})
        
        if not user_data or not check_password_hash(user_data['password'], password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
            
        login_user(User(user_data))"""
content = content.replace(c5_old, c5_new)

c6_old = """        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != current_user.id:
            flash("Email already in use.")
        else:
            current_user.name = name
            current_user.email = email
            db.session.commit()
            flash("Profile updated successfully.")"""
c6_new = """        existing = db.users.find_one({'email': email})
        if existing and str(existing['_id']) != current_user.id:
            flash("Email already in use.")
        else:
            db.users.update_one(
                {'_id': ObjectId(current_user.id)}, 
                {'$set': {'name': name, 'email': email}}
            )
            current_user.name = name
            current_user.email = email
            flash("Profile updated successfully.")"""
content = content.replace(c6_old, c6_new)

c7_old = """    total_users = User.query.count()
    total_records = MedicalRecord.query.count()
    total_checks = SymptomHistory.query.count()
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    recent_checks = SymptomHistory.query.order_by(SymptomHistory.date_added.desc()).limit(10).all()"""
c7_new = """    total_users = db.users.count_documents({})
    total_records = db.medical_records.count_documents({})
    total_checks = db.symptom_history.count_documents({})
    recent_users = list(db.users.find().sort('_id', -1).limit(5))
    for u in recent_users: u['id'] = str(u['_id'])
    recent_checks = list(db.symptom_history.find().sort('date_added', -1).limit(10))
    for c in recent_checks: c['id'] = str(c['_id'])"""
content = content.replace(c7_old, c7_new)

c8_old = """        new_record = MedicalRecord(
            user_id=current_user.id,
            record_type=record_type,
            description=description,
            file_path=file_path
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Record added successfully')
        return redirect(url_for('dashboard'))
        
    records = MedicalRecord.query.filter_by(user_id=current_user.id).order_by(MedicalRecord.date_added.desc()).all()
    symptom_history = SymptomHistory.query.filter_by(user_id=current_user.id).order_by(SymptomHistory.date_added.desc()).all()
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, records=records, symptom_history=symptom_history, contacts=contacts)"""
c8_new = """        new_record = {
            'user_id': current_user.id,
            'record_type': record_type,
            'description': description,
            'file_path': file_path,
            'date_added': datetime.utcnow()
        }
        db.medical_records.insert_one(new_record)
        flash('Record added successfully')
        return redirect(url_for('dashboard'))
        
    records = list(db.medical_records.find({'user_id': current_user.id}).sort('date_added', -1))
    for r in records: r['id'] = str(r['_id'])
    symptom_history = list(db.symptom_history.find({'user_id': current_user.id}).sort('date_added', -1))
    for s in symptom_history: s['id'] = str(s['_id'])
    contacts = list(db.emergency_contacts.find({'user_id': current_user.id}))
    for c in contacts: c['id'] = str(c['_id'])
    return render_template('dashboard.html', user=current_user, records=records, symptom_history=symptom_history, contacts=contacts)"""
content = content.replace(c8_old, c8_new)

c9_old = """@app.route('/view_record/<int:record_id>')
@login_required
def view_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    if record.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    
    if not record.file_path:
        flash('No file associated with this record')
        return redirect(url_for('dashboard'))
        
    filename = os.path.basename(record.file_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/edit_record/<int:record_id>', methods=['POST'])
@login_required
def edit_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    if record.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    record.record_type = request.form.get('record_type', record.record_type)
    record.description = request.form.get('description', record.description)
    
    file = request.files.get('file')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        record.file_path = file_path
        
    db.session.commit()
    flash('Record updated successfully')
    return redirect(url_for('dashboard'))

@app.route('/delete_record/<int:record_id>')
@login_required
def delete_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    if record.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted')
    return redirect(url_for('dashboard'))"""
c9_new = """@app.route('/view_record/<record_id>')
@login_required
def view_record(record_id):
    record = db.medical_records.find_one({'_id': ObjectId(record_id)})
    if not record:
        flash('Record not found')
        return redirect(url_for('dashboard'))
    if record.get('user_id') != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    
    if not record.get('file_path'):
        flash('No file associated with this record')
        return redirect(url_for('dashboard'))
        
    filename = os.path.basename(record['file_path'])
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/edit_record/<record_id>', methods=['POST'])
@login_required
def edit_record(record_id):
    record = db.medical_records.find_one({'_id': ObjectId(record_id)})
    if not record:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    if record.get('user_id') != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    update_data = {}
    record_type = request.form.get('record_type')
    if record_type: update_data['record_type'] = record_type
    description = request.form.get('description')
    if description: update_data['description'] = description
    
    file = request.files.get('file')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        update_data['file_path'] = file_path
        
    if update_data:
        db.medical_records.update_one({'_id': ObjectId(record_id)}, {'$set': update_data})
    
    flash('Record updated successfully')
    return redirect(url_for('dashboard'))

@app.route('/delete_record/<record_id>')
@login_required
def delete_record(record_id):
    record = db.medical_records.find_one({'_id': ObjectId(record_id)})
    if not record:
        flash('Record not found')
        return redirect(url_for('dashboard'))
    if record.get('user_id') != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    
    db.medical_records.delete_one({'_id': ObjectId(record_id)})
    flash('Record deleted')
    return redirect(url_for('dashboard'))"""
content = content.replace(c9_old, c9_new)

c10_old = """    new_contact = EmergencyContact(user_id=current_user.id, name=name, phone=phone)
    db.session.add(new_contact)
    db.session.commit()
    flash('Contact added')
    return redirect(url_for('dashboard'))

@app.route('/delete_contact/<int:contact_id>')
@login_required
def delete_contact(contact_id):
    contact = EmergencyContact.query.get_or_404(contact_id)
    if contact.user_id == current_user.id:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact deleted')
    return redirect(url_for('dashboard'))"""
c10_new = """    new_contact = {'user_id': current_user.id, 'name': name, 'phone': phone}
    db.emergency_contacts.insert_one(new_contact)
    flash('Contact added')
    return redirect(url_for('dashboard'))

@app.route('/delete_contact/<contact_id>')
@login_required
def delete_contact(contact_id):
    contact = db.emergency_contacts.find_one({'_id': ObjectId(contact_id)})
    if contact and contact.get('user_id') == current_user.id:
        db.emergency_contacts.delete_one({'_id': ObjectId(contact_id)})
        flash('Contact deleted')
    return redirect(url_for('dashboard'))"""
content = content.replace(c10_old, c10_new)

c11_old = """        new_reminder = MedicationReminder(
            user_id=current_user.id,
            medicine_name=medicine_name,
            dosage=dosage,
            time=time
        )
        db.session.add(new_reminder)
        db.session.commit()
        flash("Reminder added successfully!")
        return redirect(url_for("reminders"))
        
    user_reminders = MedicationReminder.query.filter_by(user_id=current_user.id).all()
    return render_template("reminders.html", reminders=user_reminders)

@app.route('/delete_reminder/<int:reminder_id>')
@login_required
def delete_reminder(reminder_id):
    reminder = MedicationReminder.query.get_or_404(reminder_id)
    if reminder.user_id == current_user.id:
        db.session.delete(reminder)
        db.session.commit()
        flash('Reminder deleted')
    return redirect(url_for('reminders'))"""
c11_new = """        new_reminder = {
            'user_id': current_user.id,
            'medicine_name': medicine_name,
            'dosage': dosage,
            'time': time,
            'date_added': datetime.utcnow()
        }
        db.medication_reminders.insert_one(new_reminder)
        flash("Reminder added successfully!")
        return redirect(url_for("reminders"))
        
    user_reminders = list(db.medication_reminders.find({'user_id': current_user.id}))
    for r in user_reminders: r['id'] = str(r['_id'])
    return render_template("reminders.html", reminders=user_reminders)

@app.route('/delete_reminder/<reminder_id>')
@login_required
def delete_reminder(reminder_id):
    reminder = db.medication_reminders.find_one({'_id': ObjectId(reminder_id)})
    if reminder and reminder.get('user_id') == current_user.id:
        db.medication_reminders.delete_one({'_id': ObjectId(reminder_id)})
        flash('Reminder deleted')
    return redirect(url_for('reminders'))"""
content = content.replace(c11_old, c11_new)

c12_old = """@app.route("/health_tips")
def health_tips():
    tips = HealthTip.query.order_by(HealthTip.date_added.desc()).all()
    return render_template("health_tips.html", tips=tips)

@app.route('/api/reminders')
@login_required
def api_reminders():
    user_reminders = MedicationReminder.query.filter_by(user_id=current_user.id).all()
    reminders_data = [{"medicine_name": r.medicine_name, "time": r.time} for r in user_reminders]
    return jsonify({"reminders": reminders_data})"""
c12_new = """@app.route("/health_tips")
def health_tips():
    tips = list(db.health_tips.find().sort('date_added', -1))
    for t in tips: t['id'] = str(t['_id'])
    return render_template("health_tips.html", tips=tips)

@app.route('/api/reminders')
@login_required
def api_reminders():
    user_reminders = list(db.medication_reminders.find({'user_id': current_user.id}))
    reminders_data = [{"medicine_name": r.get('medicine_name'), "time": r.get('time')} for r in user_reminders]
    return jsonify({"reminders": reminders_data})"""
content = content.replace(c12_old, c12_new)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied.")
