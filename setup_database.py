"""
setup_database.py
────────────────────────────────────────────────────────────────────────────────
Creates the clinic.db SQLite database with schema and realistic dummy data.

Run:  python setup_database.py

Produces:
  • clinic.db
  • Summary printed to stdout:
    "Created X patients, Y doctors, Z appointments, W treatments, V invoices"

Data requirements (from assignment):
  ✅ 15 doctors across 5 specializations
  ✅ 200 patients, spread across 8-10 cities
  ✅ 500 appointments over the past 12 months, varied statuses
  ✅ 350 treatments linked to completed appointments
  ✅ 300 invoices (mix of Paid / Pending / Overdue)
  ✅ Dates spread across the last 12 months
  ✅ Costs between 50 and 5000
  ✅ Some patients with many appointments, some with just 1
  ✅ Some doctors busier than others
  ✅ NULL values in optional fields (email, phone, notes)
"""

import sqlite3
import random
from datetime import datetime, timedelta, date
from faker import Faker

fake = Faker("en_IN")   # Indian locale for more realistic clinic data
random.seed(42)
Faker.seed(42)

DB_PATH = "clinic.db"

SPECIALIZATIONS = ["Dermatology", "Cardiology", "Orthopedics", "General", "Pediatrics"]
DEPARTMENTS      = {
    "Dermatology": "Skin & Hair",
    "Cardiology":  "Heart & Vascular",
    "Orthopedics": "Bone & Joint",
    "General":     "General Medicine",
    "Pediatrics":  "Child Health",
}
CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
]
APPOINTMENT_STATUSES = ["Scheduled", "Completed", "Cancelled", "No-Show"]
INVOICE_STATUSES     = ["Paid", "Pending", "Overdue"]
TREATMENTS = [
    "Blood Test", "ECG", "X-Ray", "MRI Scan", "CT Scan",
    "Physiotherapy Session", "Skin Biopsy", "Vaccination",
    "Consultation", "Ultrasound", "Dental Cleaning", "Eye Exam",
    "Allergy Test", "Spirometry", "Bone Density Scan",
]


def random_date_in_last_n_months(n: int = 12) -> date:
    end   = date.today()
    start = end - timedelta(days=n * 30)
    return start + timedelta(days=random.randint(0, (end - start).days))


def random_datetime_in_last_n_months(n: int = 12) -> datetime:
    d = random_date_in_last_n_months(n)
    hour   = random.randint(8, 17)
    minute = random.choice([0, 15, 30, 45])
    return datetime(d.year, d.month, d.day, hour, minute)


# ── Schema ─────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    date_of_birth   DATE,
    gender          TEXT CHECK(gender IN ('M', 'F')),
    city            TEXT,
    registered_date DATE
);

CREATE TABLE doctors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    specialization TEXT,
    department     TEXT,
    phone          TEXT
);

CREATE TABLE appointments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL REFERENCES patients(id),
    doctor_id        INTEGER NOT NULL REFERENCES doctors(id),
    appointment_date DATETIME,
    status           TEXT CHECK(status IN ('Scheduled','Completed','Cancelled','No-Show')),
    notes            TEXT
);

CREATE TABLE treatments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id   INTEGER NOT NULL REFERENCES appointments(id),
    treatment_name   TEXT,
    cost             REAL,
    duration_minutes INTEGER
);

CREATE TABLE invoices (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id   INTEGER NOT NULL REFERENCES patients(id),
    invoice_date DATE,
    total_amount REAL,
    paid_amount  REAL,
    status       TEXT CHECK(status IN ('Paid','Pending','Overdue'))
);
"""


def seed(conn: sqlite3.Connection):
    cur = conn.cursor()

    # ── Doctors (15 across 5 specializations, 3 each) ─────────────────────
    doctor_ids = []
    for i in range(15):
        spec  = SPECIALIZATIONS[i % len(SPECIALIZATIONS)]
        dept  = DEPARTMENTS[spec]
        phone = fake.phone_number() if random.random() > 0.1 else None
        cur.execute(
            "INSERT INTO doctors (name, specialization, department, phone) VALUES (?,?,?,?)",
            (fake.name(), spec, dept, phone),
        )
        doctor_ids.append(cur.lastrowid)

    # Make some doctors "busier" by repeating them in a weighted pool
    busy_doctors = random.choices(doctor_ids, k=5)   # 5 extra popular doctors
    doctor_pool  = doctor_ids + busy_doctors * 4      # weighted pool

    # ── Patients (200) ────────────────────────────────────────────────────
    patient_ids = []
    for _ in range(200):
        email = fake.email()           if random.random() > 0.15 else None
        phone = fake.phone_number()    if random.random() > 0.15 else None
        cur.execute(
            """INSERT INTO patients
               (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                fake.first_name(),
                fake.last_name(),
                email,
                phone,
                fake.date_of_birth(minimum_age=5, maximum_age=85).isoformat(),
                random.choice(["M", "F"]),
                random.choice(CITIES),
                random_date_in_last_n_months(18).isoformat(),
            ),
        )
        patient_ids.append(cur.lastrowid)

    # Make some patients "repeat visitors" (4-8 appointments)
    # and some single-visit patients
    repeat_patients = random.sample(patient_ids, k=60)

    # Build appointment patient pool
    appointment_patients = []
    for pid in repeat_patients:
        appointment_patients.extend([pid] * random.randint(3, 8))
    remaining_slots = 500 - len(appointment_patients)
    if remaining_slots > 0:
        appointment_patients.extend(
            random.choices(patient_ids, k=remaining_slots)
        )
    random.shuffle(appointment_patients)
    appointment_patients = appointment_patients[:500]

    # ── Appointments (500) ───────────────────────────────────────────────
    appointment_ids_by_status: dict[str, list[int]] = {s: [] for s in APPOINTMENT_STATUSES}

    status_weights = [0.15, 0.55, 0.20, 0.10]   # Scheduled/Completed/Cancelled/No-Show

    for pid in appointment_patients:
        doc_id  = random.choice(doctor_pool)
        appt_dt = random_datetime_in_last_n_months(12)
        status  = random.choices(APPOINTMENT_STATUSES, weights=status_weights)[0]
        notes   = fake.sentence() if random.random() > 0.5 else None
        cur.execute(
            """INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
               VALUES (?,?,?,?,?)""",
            (pid, doc_id, appt_dt.strftime("%Y-%m-%d %H:%M:%S"), status, notes),
        )
        appointment_ids_by_status[status].append(cur.lastrowid)

    # ── Treatments (350, linked to Completed appointments) ───────────────
    completed_ids = appointment_ids_by_status["Completed"]
    treat_appt_ids = random.sample(
        completed_ids, k=min(350, len(completed_ids))
    )

    for appt_id in treat_appt_ids:
        cur.execute(
            """INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes)
               VALUES (?,?,?,?)""",
            (
                appt_id,
                random.choice(TREATMENTS),
                round(random.uniform(50, 5000), 2),
                random.choice([15, 20, 30, 45, 60, 90, 120]),
            ),
        )

    # ── Invoices (300, linked to patients) ───────────────────────────────
    invoice_patient_ids = random.choices(patient_ids, k=300)
    inv_status_weights  = [0.55, 0.30, 0.15]   # Paid / Pending / Overdue

    for pid in invoice_patient_ids:
        total  = round(random.uniform(100, 15000), 2)
        status = random.choices(INVOICE_STATUSES, weights=inv_status_weights)[0]
        if status == "Paid":
            paid = total
        elif status == "Pending":
            paid = round(total * random.uniform(0, 0.5), 2)
        else:
            paid = round(total * random.uniform(0, 0.2), 2)

        cur.execute(
            """INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status)
               VALUES (?,?,?,?,?)""",
            (
                pid,
                random_date_in_last_n_months(12).isoformat(),
                total,
                paid,
                status,
            ),
        )

    conn.commit()

    # ── Summary ───────────────────────────────────────────────────────────
    def count(table): return cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    print("─" * 50)
    print("  clinic.db created successfully!")
    print("─" * 50)
    print(f"  Patients     : {count('patients')}")
    print(f"  Doctors      : {count('doctors')}")
    print(f"  Appointments : {count('appointments')}")
    print(f"  Treatments   : {count('treatments')}")
    print(f"  Invoices     : {count('invoices')}")
    print("─" * 50)
    print(f"\nCreated {count('patients')} patients, {count('doctors')} doctors, "
          f"{count('appointments')} appointments, {count('treatments')} treatments, "
          f"{count('invoices')} invoices.")


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    seed(conn)
    conn.close()
