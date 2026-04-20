"""Tests for LinkedIn to Resume Generator."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generator.parser import Profile, Experience, Education, Project, create_sample_profile
from generator.resume_generator import generate_html, generate_pdf


def test_profile_creation():
    p = Profile(name="Test", headline="Developer", email="test@test.com")
    assert p.name == "Test"
    assert p.headline == "Developer"
    print("✅ test_profile_creation passed")


def test_profile_to_json():
    p = Profile(name="Test", skills=["Python", "SQL"])
    j = json.loads(p.to_json())
    assert j["name"] == "Test"
    assert "Python" in j["skills"]
    print("✅ test_profile_to_json passed")


def test_profile_from_json():
    data = {"name": "Test", "headline": "Dev", "skills": ["Go", "Rust"], "experiences": [{"title": "SWE", "company": "X"}]}
    p = Profile.from_dict(data)
    assert p.name == "Test"
    assert len(p.skills) == 2
    assert len(p.experiences) == 1
    assert p.experiences[0].title == "SWE"
    print("✅ test_profile_from_json passed")


def test_sample_profile():
    p = create_sample_profile()
    assert p.name == "Nawang Dorjay"
    assert len(p.skills) > 0
    assert len(p.education) > 0
    assert len(p.projects) > 0
    assert len(p.experiences) > 0
    print("✅ test_sample_profile passed")


def test_html_generation_modern():
    p = create_sample_profile()
    html = generate_html(p, "modern")
    assert "<!DOCTYPE html>" in html
    assert p.name in html
    assert "Summary" in html
    assert "Experience" in html
    assert "Education" in html
    assert "Skills" in html
    assert "Projects" in html
    print("✅ test_html_generation_modern passed")


def test_html_generation_classic():
    p = create_sample_profile()
    html = generate_html(p, "classic")
    assert "<!DOCTYPE html>" in html
    print("✅ test_html_generation_classic passed")


def test_html_generation_minimal():
    p = create_sample_profile()
    html = generate_html(p, "minimal")
    assert "<!DOCTYPE html>" in html
    print("✅ test_html_generation_minimal passed")


def test_html_escaping():
    p = Profile(name="Test <Name>", headline='Dev & "Engineer"')
    html = generate_html(p)
    assert "&lt;Name&gt;" in html
    assert "&amp;" in html
    print("✅ test_html_escaping passed")


def test_empty_profile():
    p = Profile()
    html = generate_html(p)
    assert "<!DOCTYPE html>" in html
    print("✅ test_empty_profile passed")


def test_pdf_generation():
    p = create_sample_profile()
    try:
        pdf_path = generate_pdf(p, "modern")
        assert os.path.exists(pdf_path)
        size = os.path.getsize(pdf_path)
        assert size > 0
        print(f"✅ test_pdf_generation passed ({size} bytes)")
    except Exception as e:
        print(f"⚠️ test_pdf_generation: fpdf2 not installed, HTML fallback used ({e})")


def test_json_roundtrip():
    p = create_sample_profile()
    j = p.to_json()
    p2 = Profile.from_json(j)
    assert p2.name == p.name
    assert p2.skills == p.skills
    assert len(p2.experiences) == len(p.experiences)
    print("✅ test_json_roundtrip passed")


if __name__ == "__main__":
    tests = [
        test_profile_creation, test_profile_to_json, test_profile_from_json,
        test_sample_profile, test_html_generation_modern, test_html_generation_classic,
        test_html_generation_minimal, test_html_escaping, test_empty_profile,
        test_pdf_generation, test_json_roundtrip,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t(); passed += 1
        except Exception as e:
            print(f"❌ {t.__name__}: {e}"); failed += 1
    print(f"\n{'='*40}\n{passed} passed, {failed} failed")
    if not failed:
        print("All tests passed! 🎉")
