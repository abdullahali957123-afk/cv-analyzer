import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["CV_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

from utils import db  # noqa: E402


def test_profile_history_jobs_and_delete():
    db.init_db()
    assert db.get_profile() is None
    db.save_profile({"name": "Sara", "skills": "Python"})
    assert db.get_profile()["data"]["name"] == "Sara"
    db.add_history("CV analysis", 80)
    assert db.list_history()[0]["score"] == 80
    db.save_job("job-1")
    assert db.list_saved_jobs()[0]["job_id"] == "job-1"
    db.set_setting("save_history", "1")
    assert db.get_setting("save_history") == "1"
    db.delete_all()
    assert db.get_profile() is None and db.list_history() == [] and db.list_saved_jobs() == []
    assert db.get_setting("save_history") == "0"
