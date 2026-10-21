"""Simple object-oriented models and role-based permissions."""
class User:
    def __init__(self, user_id, full_name, username, role, campus_id=None, campus_name=None):
        self.user_id = user_id
        self.full_name = full_name
        self.username = username
        self.role = role
        self.campus_id = campus_id
        self.campus_name = campus_name

    def can_manage_resources(self):
        return self.role in ("Campus Administrator", "System Operator")

    def can_view_all_campuses(self):
        return self.role == "System Operator"

class Lecturer(User):
    """Lecturers can create, view and cancel their own bookings."""
    pass

class CampusAdministrator(User):
    """Campus administrators manage resources and bookings at their assigned campus."""
    pass

class SystemOperator(User):
    """System operators can inspect data and reports across all campuses."""
    pass

def build_user(row):
    details = (row["id"], row["full_name"], row["username"], row["role"],
               row["campus_id"], row["campus_name"])
    if row["role"] == "Lecturer":
        return Lecturer(*details)
    if row["role"] == "Campus Administrator":
        return CampusAdministrator(*details)
    return SystemOperator(*details)
