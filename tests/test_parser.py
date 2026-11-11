import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cv_parser import parse_cv  # noqa: E402

TEXT = """Sara Khan
sara@example.com
0300-1234567
SKILLS
Python, HTML
EDUCATION
BS IT
"""


def test_basic_parse():
    r = parse_cv(TEXT)
    assert r["name"] == "Sara Khan"
    assert r["email"] == "sara@example.com"
    assert r["skills"] == ["Python", "HTML"]
    assert "Projects" in r["missing"]


def test_empty_text():
    r = parse_cv("")
    assert r["name"] == ""
    assert len(r["missing"]) == 7
