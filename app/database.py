"""SQLite database setup and data access for the booking system."""
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "smart_campus.db"

CAMPUSES = [
    ("Pretoria Campus", 4, 8, 18),
    ("Johannesburg Campus", 3, 7, 20),
    ("Durban Campus", 2, 9, 17),
]
SAMPLE_RESOURCES = [
    ("PRET-LAB-01", "Computer Laboratory 1", "Computer Lab", "Pretoria Campus"),
    ("PRET-PROJ-01", "Multimedia Projector 1", "Projector", "Pretoria Campus"),
    ("PRET-ROOM-01", "Seminar Room A", "Seminar Room", "Pretoria Campus"),
    ("JHB-LAB-01", "Computer Laboratory 1", "Computer Lab", "Johannesburg Campus"),
    ("JHB-PROJ-01", "Multimedia Projector 1", "Projector", "Johannesburg Campus"),
    ("JHB-ROOM-01", "Presentation Room B", "Seminar Room", "Johannesburg Campus"),
    ("DBN-LAB-01", "Computer Laboratory 1", "Computer Lab", "Durban Campus"),
    ("DBN-PROJ-01", "Multimedia Projector 1", "Projector", "Durban Campus"),
    ("DBN-ROOM-01", "Seminar Room C", "Seminar Room", "Durban Campus"),
]

def connect():
    """Open a connection and enable foreign-key checks."""
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database():
    """Create tables and insert starter campuses, resources and demo staff."""
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS campuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                max_duration INTEGER NOT NULL,
                opening_hour INTEGER NOT NULL,
                closing_hour INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Lecturer','Campus Administrator','System Operator')),
                campus_id INTEGER,
                FOREIGN KEY(campus_id) REFERENCES campuses(id)
            );
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                campus_id INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(campus_id) REFERENCES campuses(id)
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resource_id INTEGER NOT NULL,
                campus_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(resource_id) REFERENCES resources(id),
                FOREIGN KEY(campus_id) REFERENCES campuses(id)
            );
        """)
        for campus in CAMPUSES:
            db.execute("INSERT OR IGNORE INTO campuses(name,max_duration,opening_hour,closing_hour) VALUES(?,?,?,?)", campus)
        campus_ids = {r["name"]: r["id"] for r in db.execute("SELECT id,name FROM campuses")}
        for code, name, kind, campus_name in SAMPLE_RESOURCES:
            db.execute("INSERT OR IGNORE INTO resources(resource_code,name,resource_type,campus_id) VALUES(?,?,?,?)",
                       (code, name, kind, campus_ids[campus_name]))
        demo_users = [
            ("Demo Lecturer", "lecturer", "lecturer123", "Lecturer", campus_ids["Pretoria Campus"]),
            ("Pretoria Administrator", "admin_pretoria", "admin123", "Campus Administrator", campus_ids["Pretoria Campus"]),
            ("Johannesburg Administrator", "admin_jhb", "admin123", "Campus Administrator", campus_ids["Johannesburg Campus"]),
            ("Durban Administrator", "admin_durban", "admin123", "Campus Administrator", campus_ids["Durban Campus"]),
            ("System Operator", "operator", "operator123", "System Operator", None),
        ]
        for user in demo_users:
            db.execute("""INSERT OR IGNORE INTO users(full_name,username,password,role,campus_id)
                          VALUES(?,?,?,?,?)""", user)

def get_campuses():
    with connect() as db:
        return db.execute("SELECT * FROM campuses ORDER BY name").fetchall()

def get_user(username, password):
    with connect() as db:
        return db.execute("""SELECT users.*, campuses.name AS campus_name
            FROM users LEFT JOIN campuses ON users.campus_id=campuses.id
            WHERE username=? AND password=?""", (username.strip(), password)).fetchone()

def register_lecturer(full_name, username, password):
    full_name, username = full_name.strip(), username.strip()
    if not full_name or not username or not password:
        return False, "Please complete every field."
    try:
        with connect() as db:
            db.execute("INSERT INTO users(full_name,username,password,role) VALUES(?,?,?,'Lecturer')",
                       (full_name, username, password))
        return True, "Account created. You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username is already in use."

def get_resources(campus_id, active_only=True):
    query = """SELECT resources.*, campuses.name AS campus_name FROM resources
               JOIN campuses ON resources.campus_id=campuses.id WHERE resources.campus_id=?"""
    if active_only:
        query += " AND resources.active=1"
    query += " ORDER BY resources.name"
    with connect() as db:
        return db.execute(query, (campus_id,)).fetchall()

def get_all_resources(campus_id=None):
    query = """SELECT resources.*, campuses.name AS campus_name FROM resources
               JOIN campuses ON resources.campus_id=campuses.id"""
    params = ()
    if campus_id:
        query += " WHERE resources.campus_id=?"
        params = (campus_id,)
    query += " ORDER BY campuses.name, resources.name"
    with connect() as db:
        return db.execute(query, params).fetchall()

def add_resource(code, name, kind, campus_id):
    try:
        with connect() as db:
            db.execute("INSERT INTO resources(resource_code,name,resource_type,campus_id) VALUES(?,?,?,?)",
                       (code.strip().upper(), name.strip(), kind.strip(), campus_id))
        return True, "Resource added successfully."
    except sqlite3.IntegrityError:
        return False, "Resource code already exists, or a required value is invalid."

def update_resource(resource_id, code, name, kind, campus_id):
    try:
        with connect() as db:
            db.execute("""UPDATE resources SET resource_code=?,name=?,resource_type=?,campus_id=?
                          WHERE id=?""", (code.strip().upper(), name.strip(), kind.strip(), campus_id, resource_id))
        return True, "Resource updated."
    except sqlite3.IntegrityError:
        return False, "Resource code already exists or campus is invalid."

def deactivate_resource(resource_id):
    with connect() as db:
        db.execute("UPDATE resources SET active=0 WHERE id=?", (resource_id,))

def get_bookings(campus_id=None, user_id=None, status=None):
    query = """SELECT bookings.*, users.full_name, users.username, resources.resource_code,
               resources.name AS resource_name, campuses.name AS campus_name
               FROM bookings JOIN users ON bookings.user_id=users.id
               JOIN resources ON bookings.resource_id=resources.id
               JOIN campuses ON bookings.campus_id=campuses.id WHERE 1=1"""
    params = []
    if campus_id:
        query += " AND bookings.campus_id=?"; params.append(campus_id)
    if user_id:
        query += " AND bookings.user_id=?"; params.append(user_id)
    if status:
        query += " AND bookings.status=?"; params.append(status)
    query += " ORDER BY booking_date DESC, start_time DESC"
    with connect() as db:
        return db.execute(query, params).fetchall()

def create_booking(user_id, resource_id, campus_id, booking_date, start_time, duration):
    from datetime import date, datetime, timedelta
    try:
        chosen_date = date.fromisoformat(booking_date)
        start = datetime.strptime(start_time, "%H:%M")
    except ValueError:
        return False, "Use date YYYY-MM-DD and time HH:MM (24-hour clock)."
    if chosen_date < date.today():
        return False, "Bookings must be for today or a future date."
    if not isinstance(duration, int) or duration < 1:
        return False, "Duration must be a whole number of hours."
    with connect() as db:
        campus = db.execute("SELECT * FROM campuses WHERE id=?", (campus_id,)).fetchone()
        resource = db.execute("SELECT * FROM resources WHERE id=? AND campus_id=? AND active=1",
                              (resource_id, campus_id)).fetchone()
        if not campus or not resource:
            return False, "Choose an active resource at the selected campus."
        start_minutes = start.hour * 60 + start.minute
        end_minutes = start_minutes + duration * 60
        if duration > campus["max_duration"]:
            return False, f"This campus allows a maximum of {campus['max_duration']} hours per booking."
        if start_minutes < campus["opening_hour"] * 60 or end_minutes > campus["closing_hour"] * 60:
            return False, f"Bookings must fit within {campus['opening_hour']:02d}:00–{campus['closing_hour']:02d}:00."
        if chosen_date == date.today() and start < datetime.now().replace(second=0, microsecond=0):
            return False, "Choose a start time that has not already passed."
        existing = db.execute("""SELECT start_time,duration FROM bookings
            WHERE resource_id=? AND booking_date=? AND status='Active'""", (resource_id, booking_date)).fetchall()
        for row in existing:
            old_start = datetime.strptime(row["start_time"], "%H:%M")
            old_a = old_start.hour * 60 + old_start.minute
            old_b = old_a + row["duration"] * 60
            if start_minutes < old_b and old_a < end_minutes:
                return False, "That resource is already booked for an overlapping time."
        db.execute("""INSERT INTO bookings(user_id,resource_id,campus_id,booking_date,start_time,duration)
                      VALUES(?,?,?,?,?,?)""",
                   (user_id, resource_id, campus_id, booking_date, start_time, duration))
    return True, "Booking created successfully."

def cancel_booking(booking_id, user_id=None, campus_id=None):
    from datetime import date
    with connect() as db:
        query = "SELECT * FROM bookings WHERE id=? AND status='Active'"
        params = [booking_id]
        if user_id:
            query += " AND user_id=?"; params.append(user_id)
        if campus_id:
            query += " AND campus_id=?"; params.append(campus_id)
        booking = db.execute(query, params).fetchone()
        if not booking:
            return False, "Active booking not found or you do not have permission."
        if booking["booking_date"] < date.today().isoformat():
            return False, "Past bookings cannot be cancelled."
        db.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (booking_id,))
    return True, "Booking cancelled."

def get_campus_reports():
    with connect() as db:
        return db.execute("""SELECT campuses.name,
            COUNT(CASE WHEN bookings.status='Active' THEN 1 END) AS total_bookings,
            ROUND(AVG(CASE WHEN bookings.status='Active' THEN bookings.duration END),2) AS average_duration
            FROM campuses LEFT JOIN bookings ON campuses.id=bookings.campus_id
            GROUP BY campuses.id ORDER BY campuses.name""").fetchall()

def get_popular_resources(campus_id=None):
    query = """SELECT resources.name, resources.resource_code, campuses.name AS campus_name,
               COUNT(bookings.id) AS use_count FROM resources
               JOIN campuses ON resources.campus_id=campuses.id
               LEFT JOIN bookings ON resources.id=bookings.resource_id AND bookings.status='Active'"""
    params = ()
    if campus_id:
        query += " WHERE resources.campus_id=?"; params = (campus_id,)
    query += " GROUP BY resources.id ORDER BY use_count DESC, resources.name"
    with connect() as db:
        return db.execute(query, params).fetchall()
