# -*- coding: utf-8 -*-
"""
seed_doctors.py  -- Run once to populate MongoDB with doctor accounts & consultation data.
Usage:  python seed_doctors.py
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random, os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))
db = client["medico"]

# ── Clean previous seed data ──────────────────────────────────
for col in ["doctors", "consultations", "referrals", "ipd_requests"]:
    db[col].drop()

print("[SEED] Seeding doctors...")

DOCTORS = [
    {
        "name": "Dr. Aisha Khan",
        "email": "dr.aisha@medico.com",
        "password": generate_password_hash("Doctor@123", method="pbkdf2:sha256"),
        "specialization": "Cardiologist",
        "license_id": "MCI-CAR-00101",
        "department": "Cardiology",
        "phone": "+91-9000000001",
        "experience_years": 12,
        "hospital": "MediGuide Central Hospital",
        "avatar_initials": "AK",
        "avatar_color": "#0ABFA3",
        "is_active": True,
        "created_at": datetime.utcnow(),
    },
    {
        "name": "Dr. Rajan Mehta",
        "email": "dr.rajan@medico.com",
        "password": generate_password_hash("Doctor@456", method="pbkdf2:sha256"),
        "specialization": "General Physician",
        "license_id": "MCI-GP-00202",
        "department": "General Medicine",
        "phone": "+91-9000000002",
        "experience_years": 8,
        "hospital": "MediGuide Central Hospital",
        "avatar_initials": "RM",
        "avatar_color": "#6C5CE7",
        "is_active": True,
        "created_at": datetime.utcnow(),
    },
]

result = db.doctors.insert_many(DOCTORS)
doctor_ids = [str(d) for d in result.inserted_ids]

print(f"  [OK] Inserted {len(doctor_ids)} doctors")

# ── Helper data ───────────────────────────────────────────────
NAMES = ["Priya Sharma","Arjun Patel","Sunita Devi","Mohammed Ali","Kavya Reddy",
         "Rohan Singh","Meena Iyer","Vikram Nair","Deepa Gupta","Sanjay Joshi"]
GENDERS = ["Female","Male","Female","Male","Female","Male","Female","Male","Female","Male"]
BLOOD_GRP = ["A+","O+","B+","AB+","A-","O-","B+","A+","O+","B-"]
COMPLAINTS = ["Chest pain and shortness of breath","Persistent headache","High fever for 3 days",
               "Knee pain","Diabetes follow-up","Hypertension check","Cough and cold",
               "Back pain","Eye irritation","Stomach cramps"]
STATUSES_QUEUE = ["Waiting","In Progress","Completed","No-Show","Waiting","Completed",
                  "Waiting","In Progress","Completed","Waiting"]
PRIORITIES = ["Urgent","Normal","Follow-up","Urgent","Normal","Normal","Follow-up","Urgent","Normal","Normal"]
DIAGNOSES = ["Hypertensive Crisis","Migraine","Viral fever","Osteoarthritis","Type 2 Diabetes",
             "Essential Hypertension","URTI","Lumbar Spondylosis","Conjunctivitis","IBS"]

now = datetime.utcnow()

# ── Build consultations for each doctor ───────────────────────
all_consultations = []
for i, did in enumerate(doctor_ids):
    for j, pname in enumerate(NAMES):
        age = random.randint(22, 72)
        apt_time = (now.replace(hour=9, minute=0, second=0) + timedelta(minutes=j*20)).strftime("%I:%M %p")
        # past consultations (history)
        past_date = now - timedelta(days=random.randint(1, 60))
        status_today = STATUSES_QUEUE[j]

        all_consultations.append({
            "doctor_id": did,
            "patient_name": pname,
            "patient_age": age,
            "patient_gender": GENDERS[j],
            "patient_dob": (now - timedelta(days=age*365)).strftime("%Y-%m-%d"),
            "patient_blood_group": BLOOD_GRP[j],
            "patient_contact": f"+91-98{random.randint(10000000,99999999)}",
            "slot_number": j + 1,
            "appointment_time": apt_time,
            "chief_complaint": COMPLAINTS[j],
            "symptoms": ["fever","fatigue","nausea"][:random.randint(1,3)],
            "status": status_today,
            "priority": PRIORITIES[j],
            "queue_type": "today",
            # vitals
            "vitals": {
                "bp": f"{random.randint(100,160)}/{random.randint(60,100)} mmHg",
                "temp": f"{round(random.uniform(97.0, 103.0),1)} °F",
                "pulse": f"{random.randint(60,110)} bpm",
                "spo2": f"{random.randint(94,100)}%",
                "weight": f"{random.randint(45,100)} kg",
            },
            "medical_history": ["Diabetes","Hypertension"][:random.randint(0,2)],
            "current_medications": ["Metformin 500mg","Amlodipine 5mg"][:random.randint(0,2)],
            "allergies": random.choice(["None","Penicillin","Aspirin","Sulfa drugs"]),
            "doctor_notes": "",
            "investigation_requests": [],
            "prescription": [],
            "follow_up_date": None,
            "consultation_date": now.strftime("%Y-%m-%d"),
            "diagnosis": DIAGNOSES[j] if status_today == "Completed" else "",
            "prescription_issued": status_today == "Completed",
            "follow_up_scheduled": random.choice([True, False]) if status_today == "Completed" else False,
            "patient_rating": random.randint(3,5) if status_today == "Completed" else None,
            "created_at": now,
        })

        # Follow-up (separate entry with future date)
        if j % 3 == 0:
            all_consultations.append({
                **all_consultations[-1],
                "_id": None,
                "queue_type": "followup",
                "status": "Waiting",
                "priority": "Follow-up",
                "follow_up_date": (now + timedelta(days=random.randint(3,30))).strftime("%Y-%m-%d"),
                "last_diagnosis": DIAGNOSES[j],
                "treatment_progress": random.choice(["Improving","Stable","Worsening"]),
                "pending_tasks": random.choice(["Review blood reports","Renew prescription","Await ECG results"]),
                "created_at": now,
            })

        # Pending/awaiting
        if j % 4 == 0:
            all_consultations.append({
                **all_consultations[-1],
                "_id": None,
                "queue_type": "pending",
                "status": "Waiting",
                "pending_reason": random.choice(["Awaiting lab results","Teleconsult request","Second opinion","Referred by Dr. Mehta"]),
                "created_at": now,
            })

        # Emergency / Walk-in
        if j % 5 == 0:
            all_consultations.append({
                **all_consultations[-1],
                "_id": None,
                "queue_type": "emergency",
                "status": random.choice(["In Progress","Waiting","Completed"]),
                "triage_level": random.choice(["🔴 Critical","🟠 High","🟡 Moderate"]),
                "arrival_time": (now - timedelta(minutes=random.randint(5,120))).strftime("%I:%M %p"),
                "created_at": now,
            })

# Remove None _ids (they'll be auto-assigned)
for c in all_consultations:
    c.pop("_id", None)

db.consultations.insert_many(all_consultations)
print(f"  [OK] Inserted {len(all_consultations)} consultation records")

# ── Referrals ─────────────────────────────────────────────────
referrals = []
for i, did in enumerate(doctor_ids):
    for j in range(5):
        referrals.append({
            "to_doctor_id": did,
            "from_doctor": random.choice(["Dr. S. Verma (Ortho)","Dr. P. Nair (Neuro)","Dr. A. Roy (Oncology)"]),
            "from_department": random.choice(["Orthopedics","Neurology","Oncology","Pediatrics"]),
            "patient_name": NAMES[j],
            "patient_age": random.randint(20,70),
            "referral_reason": random.choice(["Cardiac evaluation","Second opinion","Specialist consult","Pre-op clearance"]),
            "urgency": random.choice(["Urgent","Routine","Semi-urgent"]),
            "referral_date": (now - timedelta(days=random.randint(0,10))).strftime("%Y-%m-%d"),
            "status": random.choice(["Pending","Accepted","Declined"]),
            "created_at": now,
        })

db.referrals.insert_many(referrals)
print(f"  [OK] Inserted {len(referrals)} referrals")

# ── IPD Requests ──────────────────────────────────────────────
ipd_requests = []
for i, did in enumerate(doctor_ids):
    for j in range(4):
        ipd_requests.append({
            "to_doctor_id": did,
            "patient_name": NAMES[j+2],
            "patient_age": random.randint(25,80),
            "ward": random.choice(["Ward A","ICU","Ward C","HDU","Ward B"]),
            "bed_number": f"Bed-{random.randint(1,40)}",
            "requesting_doctor": random.choice(["Dr. J. Singh","Dr. M. Patel","Dr. S. Kumar"]),
            "condition_summary": random.choice([
                "Post-op cardiac monitoring","Acute breathlessness","Uncontrolled BP","Altered sensorium"
            ]),
            "request_datetime": (now - timedelta(hours=random.randint(1,24))).strftime("%Y-%m-%d %H:%M"),
            "response_status": random.choice(["Pending","Seen"]),
            "created_at": now,
        })

db.ipd_requests.insert_many(ipd_requests)
print(f"  [OK] Inserted {len(ipd_requests)} IPD requests")

print("\n[DONE] Seeding complete!")
print("\n[CREDENTIALS] Doctor Login:")
print("  Email: dr.aisha@medico.com   | Password: Doctor@123  (Cardiologist)")
print("  Email: dr.rajan@medico.com   | Password: Doctor@456  (General Physician)")
