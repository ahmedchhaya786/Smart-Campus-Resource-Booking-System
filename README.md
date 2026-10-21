# Smart Campus Resource Booking System
**Programming 512 Assignment — Python, Tkinter and SQLite**

## 1. Project overview
This desktop application helps Richfield Graduate Institution manage shared resources across three campuses. It includes lecturer registration/login, role-based access, resource management, booking validation, cancellation, persistent SQLite storage and campus reports.

## 2. Requirements
- Python 3.10 or newer recommended
- PyCharm Community or Professional
- Tkinter (normally included with standard Windows Python)
- SQLite (included with Python; no separate database server needed)

There are no third-party Python packages to install.

## 3. Folder structure
```text
Smart_Campus_Resource_Booking_System/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   └── gui.py
├── data/
│   └── (smart_campus.db is created automatically on first run)
└── tests/
    └── test_booking_rules.py
```

## 4. Open and run in PyCharm
1. Download and extract `Smart_Campus_Resource_Booking_System.zip`.
2. Open PyCharm.
3. Select **Open** and choose the extracted `Smart_Campus_Resource_Booking_System` folder (the folder containing `main.py`).
4. Allow PyCharm to index the project. If prompted, choose a Python 3 interpreter.
5. Open `main.py`.
6. Right-click inside `main.py` and choose **Run 'main'**.
7. The database is created automatically in `data/smart_campus.db` on first launch.

## 5. Demo login accounts
These accounts are inserted automatically the first time the database is created.

| Role | Username | Password |
|---|---|---|
| Lecturer | `lecturer` | `lecturer123` |
| Pretoria Campus Administrator | `admin_pretoria` | `admin123` |
| Johannesburg Campus Administrator | `admin_jhb` | `admin123` |
| Durban Campus Administrator | `admin_durban` | `admin123` |
| System Operator | `operator` | `operator123` |

For a real deployment, passwords should be stored as salted password hashes. Plain-text passwords are used here to keep this educational assignment understandable and should not be used for a production system.

## 6. Campus booking policies
- **Pretoria Campus:** 08:00–18:00, maximum 4 hours per session.
- **Johannesburg Campus:** 07:00–20:00, maximum 3 hours per session.
- **Durban Campus:** 09:00–17:00, maximum 2 hours per session.

The booking function checks the selected campus policy before saving.

## 7. Features
- Object-oriented user roles: `Lecturer`, `CampusAdministrator`, `SystemOperator`.
- Lecturer account registration and login.
- Campus selection and visible active campus.
- Unique resource codes and duplicate rejection.
- Add, edit and deactivate resources (administrators/operators).
- Booking date, start time and duration validation.
- Prevents overlapping active bookings for the same resource.
- Lecturer booking history and cancellation of future bookings.
- SQLite persistence between program runs.
- Campus booking totals, average booking duration, popular resources and cross-campus reports.
- Input validation and user-friendly error messages.

## 8. Notes
- The first run creates the database and sample campuses/resources/accounts.
- The database file is intentionally generated at runtime and is ignored by version control; it is not required in the ZIP.
- Campus administrators can manage resources and bookings for their assigned campus. System operators can view system-wide data.
- The application uses a simple educational GUI and local database; it is not a production-ready network service.

## 9. Suggested manual testing
1. Log in as lecturer and view the available resources.
2. Create a booking during the campus's allowed hours.
3. Try booking the same resource for an overlapping time; the system should reject it.
4. Try a duration above the campus maximum; the system should reject it.
5. Cancel a future booking and confirm its status changes to Cancelled.
6. Log in as a campus administrator and add a resource with a new code.
7. Try adding a duplicate resource code; the system should reject it.
8. Log in as system operator and view the reports across all campuses.
9. Close and reopen the application; verify that saved bookings/resources remain.

## 10. Academic integrity
Review the code, test the program, and make sure you understand how each part works before submitting. Follow your lecturer's rules on assistance and disclosure. Add your own student details to any cover sheet or submission document your institution requires.


https://github.com/ahmedchhaya786/Smart-Campus-Resource-Booking-System