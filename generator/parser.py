"""
LinkedIn to Resume Generator — Core Module
Parses profile data and generates professional resumes.
"""
import json
import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime


@dataclass
class Experience:
    title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    current: bool = False
    description: str = ""
    highlights: List[str] = field(default_factory=list)


@dataclass
class Education:
    school: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    grade: str = ""
    activities: str = ""


@dataclass
class Project:
    name: str = ""
    description: str = ""
    url: str = ""
    technologies: List[str] = field(default_factory=list)


@dataclass
class Profile:
    name: str = ""
    headline: str = ""
    location: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    summary: str = ""
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Profile":
        profile = cls()
        profile.name = data.get("name", "")
        profile.headline = data.get("headline", "")
        profile.location = data.get("location", "")
        profile.email = data.get("email", "")
        profile.phone = data.get("phone", "")
        profile.linkedin = data.get("linkedin", "")
        profile.github = data.get("github", "")
        profile.website = data.get("website", "")
        profile.summary = data.get("summary", "")
        profile.skills = data.get("skills", [])
        profile.certifications = data.get("certifications", [])
        profile.languages = data.get("languages", [])

        for exp in data.get("experiences", []):
            profile.experiences.append(Experience(**exp))

        for edu in data.get("education", []):
            profile.education.append(Education(**edu))

        for proj in data.get("projects", []):
            profile.projects.append(Project(**proj))

        return profile

    @classmethod
    def from_json(cls, json_str: str) -> "Profile":
        return cls.from_dict(json.loads(json_str))


def parse_linkedin_text(text: str) -> Profile:
    """
    Parse a pasted LinkedIn profile page text into a structured Profile.
    Handles common LinkedIn export formats and copy-paste patterns.
    """
    profile = Profile()
    lines = text.strip().split("\n")
    lines = [l.strip() for l in lines if l.strip()]

    if not lines:
        return profile

    # Name is usually the first line
    profile.name = lines[0] if lines else ""

    # Headline is usually second line
    if len(lines) > 1:
        profile.headline = lines[1]

    # Look for common patterns
    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Email
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', line)
        if email_match:
            profile.email = email_match.group()

        # Phone
        phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', line)
        if phone_match and not profile.phone:
            profile.phone = phone_match.group().strip()

        # LinkedIn URL
        if "linkedin.com/in/" in line:
            linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', line)
            if linkedin_match:
                profile.linkedin = "https://" + linkedin_match.group()

        # GitHub
        if "github.com/" in line:
            github_match = re.search(r'github\.com/[\w\-]+', line)
            if github_match:
                profile.github = "https://" + github_match.group()

        # Location (usually contains city/country patterns)
        location_patterns = [
            r'(?:Delhi|Mumbai|Bangalore|Chennai|Kolkata|Hyderabad|Pune|Ahmedabad)[\w\s,]*(?:India)?',
            r'(?:New Delhi|NCR|Bengaluru|Navi Mumbai)',
            r'[\w\s]+,\s*(?:India|USA|UK|Canada|Australia)',
        ]
        for pattern in location_patterns:
            loc_match = re.search(pattern, line, re.IGNORECASE)
            if loc_match and not profile.location:
                profile.location = loc_match.group().strip()

    return profile


def create_sample_profile() -> Profile:
    """Create a sample profile for demonstration."""
    return Profile(
        name="Nawang Dorjay",
        headline="B.Tech CSE (Data Science) | AI Agent Developer | Open Source Contributor",
        location="Delhi, India",
        email="nawangdorjay09@gmail.com",
        linkedin="https://linkedin.com/in/nawangdorjay",
        github="https://github.com/nawangdorjay",
        summary="2nd-year B.Tech CSE (Data Science) student from Ladakh, building AI agents and tools for remote and underserved regions. Passionate about NLP, speech recognition, and open source.",
        experiences=[
            Experience(
                title="Software Development Intern",
                company="Tech Startup",
                location="Remote",
                start_date="Jan 2026",
                current=True,
                description="Building AI-powered tools and automation solutions.",
                highlights=["Developed NLP-based resume analysis tool", "Built voice-activated AI assistant"],
            ),
        ],
        education=[
            Education(
                school="Maharaja Agrasen Institute of Technology, GGSIPU",
                degree="B.Tech",
                field_of_study="Computer Science & Engineering (Data Science)",
                start_date="2024",
                end_date="2028",
            ),
            Education(
                school="Jawahar Navodaya Vidyalaya, Leh",
                degree="12th",
                field_of_study="Science",
                end_date="2024",
            ),
        ],
        skills=["Python", "C++", "SQL", "JavaScript", "NLP", "LangChain", "Streamlit",
                "Flask", "NumPy", "Pandas", "Git", "Linux"],
        projects=[
            Project(
                name="Ladakh Travel Agent",
                description="AI-powered travel assistant for Ladakh — permits, weather, altitude safety.",
                technologies=["Python", "LangChain", "Streamlit"],
                url="https://github.com/nawangdorjay/ladakh-travel-agent",
            ),
            Project(
                name="Voice-First Accessibility Agent",
                description="Voice assistant for rural India supporting 10+ Indian languages.",
                technologies=["Python", "Whisper", "gTTS", "Gradio"],
                url="https://github.com/nawangdorjay/voice-assistant-agent",
            ),
        ],
        certifications=["GSSoC 2026 — Agents for India Track"],
        languages=["English", "Hindi", "Ladakhi"],
    )
