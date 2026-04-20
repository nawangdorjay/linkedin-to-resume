"""
LinkedIn to Resume — Streamlit App
Paste your LinkedIn profile data, get a professional resume PDF.
"""
import streamlit as st
import json
import os
from generator.parser import Profile, parse_linkedin_text, create_sample_profile
from generator.resume_generator import generate_pdf, generate_html

st.set_page_config(
    page_title="📄 LinkedIn to Resume",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0077B5, #00A0DC);
        color: white; padding: 1.5rem 2rem; border-radius: 12px;
        margin-bottom: 1rem; text-align: center;
    }
    .method-card {
        background: #f0f8ff; border-radius: 10px; padding: 1rem;
        border: 2px solid #e0e0e0; cursor: pointer;
    }
    .method-card:hover { border-color: #0077B5; }
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown("""
    <div class="main-header">
        <h1>📄 LinkedIn to Resume</h1>
        <p style="font-size:1.1rem; margin:0;">Paste your LinkedIn profile → Get a professional resume PDF</p>
        <p style="font-size:0.9rem; margin:0.5rem 0 0 0; opacity:0.9;">
            3 templates • PDF download • Multiple formats • Customizable
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Input method selection
    tab1, tab2, tab3 = st.tabs(["📋 Paste LinkedIn Data", "✏️ Fill Form", "📝 JSON Input"])

    profile = None

    with tab1:
        st.subheader("Paste Your LinkedIn Profile")
        st.info("Copy text from your LinkedIn profile page (Ctrl+A → Ctrl+C on your LinkedIn profile) and paste it here. Or paste sections manually below.")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="Nawang Dorjay")
            headline = st.text_input("Headline", placeholder="B.Tech CSE Student | AI Developer")
            location = st.text_input("Location", placeholder="Delhi, India")
            email = st.text_input("Email", placeholder="nawangdorjay09@gmail.com")
            phone = st.text_input("Phone", placeholder="+91 9876543210")
            github = st.text_input("GitHub URL", placeholder="https://github.com/nawangdorjay")
            linkedin = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/nawangdorjay")

        with col2:
            summary = st.text_area("Professional Summary", height=120,
                placeholder="2nd-year B.Tech student passionate about AI and open source...")

            skills_text = st.text_input("Skills (comma-separated)",
                placeholder="Python, NLP, LangChain, Streamlit, SQL")

            languages_text = st.text_input("Languages (comma-separated)",
                placeholder="English, Hindi, Ladakhi")

        st.subheader("💼 Experience")
        num_exp = st.number_input("Number of experiences", 0, 10, 1)
        experiences = []
        for i in range(int(num_exp)):
            with st.expander(f"Experience {i+1}", expanded=(i == 0)):
                ec1, ec2 = st.columns(2)
                with ec1:
                    title = st.text_input("Job Title", key=f"exp_title_{i}", placeholder="Software Intern")
                    company = st.text_input("Company", key=f"exp_company_{i}", placeholder="Tech Corp")
                    exp_location = st.text_input("Location", key=f"exp_loc_{i}", placeholder="Remote")
                with ec2:
                    start = st.text_input("Start Date", key=f"exp_start_{i}", placeholder="Jan 2026")
                    end = st.text_input("End Date", key=f"exp_end_{i}", placeholder="Present")
                    current = st.checkbox("Currently working here", key=f"exp_cur_{i}")
                desc = st.text_area("Description", key=f"exp_desc_{i}", height=80,
                    placeholder="Built AI-powered tools for...")
                highlights = st.text_area("Highlights (one per line)", key=f"exp_hl_{i}", height=60,
                    placeholder="Developed NLP tool\nBuilt voice assistant")
                experiences.append({
                    "title": title, "company": company, "location": exp_location,
                    "start_date": start, "end_date": end if not current else "",
                    "current": current, "description": desc,
                    "highlights": [h.strip() for h in highlights.split("\n") if h.strip()],
                })

        st.subheader("🎓 Education")
        num_edu = st.number_input("Number of education entries", 0, 5, 1)
        education = []
        for i in range(int(num_edu)):
            with st.expander(f"Education {i+1}", expanded=(i == 0)):
                ec1, ec2 = st.columns(2)
                with ec1:
                    school = st.text_input("School/University", key=f"edu_school_{i}",
                        placeholder="Maharaja Agrasen Institute of Technology")
                    degree = st.text_input("Degree", key=f"edu_degree_{i}", placeholder="B.Tech")
                    field = st.text_input("Field of Study", key=f"edu_field_{i}", placeholder="CSE (Data Science)")
                with ec2:
                    edu_start = st.text_input("Start Year", key=f"edu_start_{i}", placeholder="2024")
                    edu_end = st.text_input("End Year", key=f"edu_end_{i}", placeholder="2028")
                    grade = st.text_input("Grade/GPA", key=f"edu_grade_{i}", placeholder="8.5 CGPA")
                education.append({
                    "school": school, "degree": degree, "field_of_study": field,
                    "start_date": edu_start, "end_date": edu_end, "grade": grade,
                })

        st.subheader("🚀 Projects")
        num_proj = st.number_input("Number of projects", 0, 10, 2)
        projects = []
        for i in range(int(num_proj)):
            with st.expander(f"Project {i+1}", expanded=(i < 2)):
                pc1, pc2 = st.columns(2)
                with pc1:
                    pname = st.text_input("Project Name", key=f"proj_name_{i}", placeholder="Ladakh Travel Agent")
                    pdesc = st.text_area("Description", key=f"proj_desc_{i}", height=60,
                        placeholder="AI-powered travel assistant for Ladakh")
                with pc2:
                    purl = st.text_input("URL", key=f"proj_url_{i}", placeholder="https://github.com/...")
                    ptech = st.text_input("Technologies (comma-separated)", key=f"proj_tech_{i}",
                        placeholder="Python, LangChain, Streamlit")
                projects.append({
                    "name": pname, "description": pdesc, "url": purl,
                    "technologies": [t.strip() for t in ptech.split(",") if t.strip()],
                })

        certs = st.text_area("Certifications (one per line)", height=80,
            placeholder="GSSoC 2026\nAWS Cloud Practitioner")

        if name:
            profile = Profile(
                name=name, headline=headline, location=location,
                email=email, phone=phone, github=github, linkedin=linkedin,
                summary=summary,
                skills=[s.strip() for s in skills_text.split(",") if s.strip()],
                experiences=[Experience(**e) if not isinstance(e, dict) else Experience(**e) for e in experiences if e.get("title")],
                education=[Education(**e) for e in education if e.get("school")],
                projects=[Project(**p) if not isinstance(p, dict) else Project(**p) for p in projects if p.get("name")],
                certifications=[c.strip() for c in certs.split("\n") if c.strip()],
                languages=[l.strip() for l in languages_text.split(",") if l.strip()],
            )

    with tab2:
        st.info("Use the 'Paste LinkedIn Data' tab — it has a form. This tab is for quick JSON.")
        sample = create_sample_profile()
        st.code(sample.to_json(), language="json")
        if st.button("Load Sample Profile"):
            profile = sample

    with tab3:
        st.subheader("Paste Profile JSON")
        json_input = st.text_area("Profile JSON", height=400,
            placeholder=Profile(
                name="Your Name", headline="Your Headline",
                email="you@email.com"
            ).to_json())
        if json_input:
            try:
                profile = Profile.from_json(json_input)
                st.success("✅ JSON parsed successfully!")
            except Exception as e:
                st.error(f"❌ Invalid JSON: {e}")

    # Generate Resume
    if profile:
        st.divider()

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"📄 Resume Preview — {profile.name}")
        with col2:
            template = st.selectbox("Template", ["modern", "classic", "minimal"])

        # Generate HTML preview
        html = generate_html(profile, template)
        st.components.v1.html(html, height=800, scrolling=True)

        # Generate and download PDF
        st.divider()
        if st.button("📥 Generate PDF Download", type="primary"):
            with st.spinner("Generating PDF..."):
                try:
                    pdf_path = generate_pdf(profile, template)
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label="⬇️ Download Resume PDF",
                        data=pdf_bytes,
                        file_name=f"{profile.name.replace(' ', '_')}_Resume.pdf",
                        mime="application/pdf",
                    )
                    st.success("✅ PDF generated! Click the download button above.")
                except Exception as e:
                    st.error(f"PDF generation error: {e}")
                    st.info("Downloading HTML instead. Use browser Print → Save as PDF.")
                    st.download_button(
                        label="⬇️ Download HTML (open in browser, Print → PDF)",
                        data=html,
                        file_name=f"{profile.name.replace(' ', '_')}_Resume.html",
                        mime="text/html",
                    )

        # Export JSON
        with st.expander("💾 Export Profile as JSON"):
            st.code(profile.to_json(), language="json")
            st.download_button(
                label="Download JSON",
                data=profile.to_json(),
                file_name=f"{profile.name.replace(' ', '_')}_profile.json",
                mime="application/json",
            )

    st.divider()
    st.caption("Built by [Nawang Dorjay](https://github.com/nawangdorjay) for GSSoC 2026")


# Import Experience, Education, Project for the form
from generator.parser import Experience, Education, Project

if __name__ == "__main__":
    main()
