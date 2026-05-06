import sys
from app import app, db, User
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

with app.app_context():
    admin_data = db.users.find_one({'email': 'admin@medico.com'})
    if not admin_data:
        new_admin = {
            'name': 'Admin User',
            'email': 'admin@medico.com',
            'password': generate_password_hash('admin123', method='pbkdf2:sha256')
        }
        db.users.insert_one(new_admin)
        print("Admin user created: admin@medico.com / admin123")
    else:
        print("Admin user already exists.")
