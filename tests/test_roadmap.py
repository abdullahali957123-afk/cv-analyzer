import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.matcher import SKILLS  # noqa: E402
from utils.roadmap import GUIDE, build_roadmap  # noqa: E402


def test_guide_covers_all_skills():
    assert set(SKILLS) <= set(GUIDE)


def test_priorities_and_order():
    req = [{"skill": "SQL", "status": "missing"}, {"skill": "Git", "status": "matched"},
           {"skill": "Docker", "status": "partial"}]
    pref = [{"skill": "React", "status": "missing"}, {"skill": "Pandas", "status": "partial"}]
    r = build_roadmap(req, pref)
    got = [(i["skill"], i["priority"]) for i in r["items"]]
    assert got[0] == ("SQL", "high")
    assert ("Docker", "medium") in got and ("React", "medium") in got
    assert ("Pandas", "low") in got
    assert all(i["skill"] != "Git" for i in r["items"])


def test_nothing_missing():
    assert build_roadmap([{"skill": "Python", "status": "matched"}], [])["items"] == []
