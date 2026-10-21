"""Small automated tests for campus booking validation."""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import database

class BookingRuleTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.patcher = patch.object(database, "DB_PATH", self.db_path)
        self.patcher.start()
        database.DATA_DIR.mkdir(exist_ok=True)
        database.initialize_database()
        with database.connect() as conn:
            self.user_id = conn.execute("SELECT id FROM users WHERE username='lecturer'").fetchone()["id"]
            row = conn.execute("""SELECT resources.id, resources.campus_id FROM resources
                                WHERE resources.resource_code='PRET-LAB-01'""").fetchone()
            self.resource_id, self.campus_id = row["id"], row["campus_id"]

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_valid_booking(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        ok, _ = database.create_booking(self.user_id, self.resource_id, self.campus_id, future, "10:00", 1)
        self.assertTrue(ok)

    def test_over_max_duration_rejected(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        ok, _ = database.create_booking(self.user_id, self.resource_id, self.campus_id, future, "10:00", 5)
        self.assertFalse(ok)

    def test_overlapping_booking_rejected(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        first, _ = database.create_booking(self.user_id, self.resource_id, self.campus_id, future, "10:00", 2)
        second, _ = database.create_booking(self.user_id, self.resource_id, self.campus_id, future, "11:00", 1)
        self.assertTrue(first)
        self.assertFalse(second)

if __name__ == "__main__":
    unittest.main()
