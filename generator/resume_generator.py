"""
LinkedIn to Resume — PDF Generator
Creates professional PDF resumes from structured profile data.
"""
import os
import tempfile
from pathlib import Path
from generator.parser import Profile

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def generate_pdf(profile: Profile, template: str = "modern") -> str:
    """
    Generate a PDF resume from profile data.
    Returns path to the generated PDF file.
    """
    if template == "classic":
        return _generate_classic(profile)
    elif template == "minimal":
        return _generate_minimal(profile)
    else:
        return _generate_modern(profile)


def generate_html(profile: Profile, template: str = "modern") -> str:
    """Generate HTML resume string for preview."""
    if template == "classic":
        return _html_classic(profile)
    elif template == "minimal":
        return _html_minimal(profile)
    else:
        return _html_modern(profile)


def _generate_modern(profile: Profile) -> str:
    """Generate PDF using fpdf2 — modern template."""
    try:
        from fpdf import FPDF
    except ImportError:
        # Fallback: save HTML
        return _save_html_fallback(profile, "modern")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Colors
    accent = (41, 98, 255)     # Blue
    dark = (33, 33, 33)
    medium = (100, 100, 100)
    light_bg = (245, 247, 250)

    # --- Header ---
    pdf.set_fill_color(*accent)
    pdf.rect(0, 0, 210, 35, style="F")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_y(8)
    pdf.cell(0, 10, _clean(profile.name), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, _clean(profile.headline), align="C", new_x="LMARGIN", new_y="NEXT")

    # Contact line
    contact_parts = []
    if profile.email:
        contact_parts.append(profile.email)
    if profile.phone:
        contact_parts.append(profile.phone)
    if profile.location:
        contact_parts.append(profile.location)
    if profile.github:
        contact_parts.append(profile.github.replace("https://", ""))

    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, " | ".join(contact_parts), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(40)

    # --- Summary ---
    if profile.summary:
        _section_header(pdf, "SUMMARY", accent)
        pdf.set_text_color(*dark)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, _clean(profile.summary))
        pdf.ln(3)

    # --- Experience ---
    if profile.experiences:
        _section_header(pdf, "EXPERIENCE", accent)
        for exp in profile.experiences:
            pdf.set_text_color(*dark)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(120, 6, _clean(exp.title), new_x="RIGHT", new_y="TOP")

            date_str = f"{exp.start_date} - {'Present' if exp.current else exp.end_date}"
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*medium)
            pdf.cell(0, 6, _clean(date_str), align="R", new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(*accent)
            company_loc = exp.company
            if exp.location:
                company_loc += f", {exp.location}"
            pdf.cell(0, 5, _clean(company_loc), new_x="LMARGIN", new_y="NEXT")

            if exp.description:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*dark)
                pdf.multi_cell(0, 4.5, _clean(exp.description))

            for h in exp.highlights:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*dark)
                pdf.cell(5)
                pdf.cell(5, 4.5, chr(8226))  # bullet
                pdf.multi_cell(0, 4.5, _clean(h))

            pdf.ln(3)

    # --- Education ---
    if profile.education:
        _section_header(pdf, "EDUCATION", accent)
        for edu in profile.education:
            pdf.set_text_color(*dark)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(120, 5, _clean(edu.school), new_x="RIGHT", new_y="TOP")

            date_str = f"{edu.start_date or ''} - {edu.end_date or ''}".strip(" -")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*medium)
            pdf.cell(0, 5, _clean(date_str), align="R", new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*dark)
            degree_line = edu.degree
            if edu.field_of_study:
                degree_line += f" in {edu.field_of_study}"
            if edu.grade:
                degree_line += f" | {edu.grade}"
            pdf.cell(0, 5, _clean(degree_line), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    # --- Skills ---
    if profile.skills:
        _section_header(pdf, "SKILLS", accent)
        pdf.set_text_color(*dark)
        pdf.set_font("Helvetica", "", 10)

        # Wrap skills in chips
        x = pdf.get_x()
        y = pdf.get_y()
        for skill in profile.skills:
            w = pdf.get_string_width(skill) + 8
            if x + w > 195:
                x = 10
                y += 7
                pdf.set_xy(x, y)
            pdf.set_fill_color(*light_bg)
            pdf.set_text_color(*dark)
            pdf.cell(w, 6, f" {skill} ", fill=True, new_x="RIGHT", new_y="TOP")
            x += w + 2
        pdf.set_xy(10, y + 9)

    # --- Projects ---
    if profile.projects:
        _section_header(pdf, "PROJECTS", accent)
        for proj in profile.projects:
            pdf.set_text_color(*dark)
            pdf.set_font("Helvetica", "B", 10)
            name = proj.name
            if proj.url:
                name += f"  ({proj.url.replace('https://', '')})"
            pdf.cell(0, 5, _clean(name), new_x="LMARGIN", new_y="NEXT")

            if proj.description:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*dark)
                pdf.multi_cell(0, 4.5, _clean(proj.description))

            if proj.technologies:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*accent)
                pdf.cell(0, 4, "Tech: " + ", ".join(proj.technologies), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    # --- Certifications ---
    if profile.certifications:
        _section_header(pdf, "CERTIFICATIONS", accent)
        for cert in profile.certifications:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*dark)
            pdf.cell(5)
            pdf.cell(5, 5, chr(8226))
            pdf.multi_cell(0, 5, _clean(cert))

    # Save
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    pdf.output(tmp.name)
    return tmp.name


def _section_header(pdf, title, color):
    """Draw a section header."""
    pdf.ln(2)
    pdf.set_text_color(*color)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    # Underline
    pdf.set_draw_color(*color)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)


def _clean(text: str) -> str:
    """Clean text for PDF — handle special characters."""
    if not text:
        return ""
    # Replace problematic characters
    replacements = {
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2026": "...",
        "\u20b9": "Rs. ",  # Rupee sign
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove any remaining non-latin-1 characters
    try:
        text.encode("latin-1")
        return text
    except UnicodeEncodeError:
        return text.encode("latin-1", errors="replace").decode("latin-1")


def _save_html_fallback(profile: Profile, template: str) -> str:
    """Fallback: save as HTML if fpdf2 not available."""
    html = generate_html(profile, template)
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w")
    tmp.write(html)
    tmp.close()
    return tmp.name


def _html_modern(profile: Profile) -> str:
    """Modern template as HTML."""
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #212121; max-width: 800px; margin: 0 auto; padding: 40px; }}
.header {{ background: #2962FF; color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }}
.header h1 {{ font-size: 28px; margin-bottom: 5px; }}
.header .headline {{ font-size: 14px; opacity: 0.9; margin-bottom: 10px; }}
.header .contact {{ font-size: 12px; opacity: 0.8; }}
.section {{ margin-bottom: 20px; }}
.section h2 {{ color: #2962FF; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #2962FF; padding-bottom: 4px; margin-bottom: 10px; }}
.section p, .section li {{ font-size: 13px; line-height: 1.6; }}
.exp-item, .edu-item {{ margin-bottom: 12px; }}
.exp-item .title {{ font-weight: bold; font-size: 14px; }}
.exp-item .date {{ float: right; color: #666; font-size: 12px; }}
.exp-item .company {{ color: #2962FF; font-style: italic; font-size: 13px; }}
.exp-item ul {{ margin-left: 20px; margin-top: 5px; }}
.skills {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.skill {{ background: #f0f4ff; color: #2962FF; padding: 4px 10px; border-radius: 15px; font-size: 12px; }}
.project-name {{ font-weight: bold; }}
.project-tech {{ color: #2962FF; font-size: 11px; }}
</style></head><body>
<div class="header">
    <h1>{_esc(profile.name)}</h1>
    <div class="headline">{_esc(profile.headline)}</div>
    <div class="contact">
        {' | '.join(filter(None, [profile.email, profile.phone, profile.location, profile.github.replace('https://','') if profile.github else '']))}
    </div>
</div>"""

    if profile.summary:
        html += f"""<div class="section">
    <h2>Summary</h2>
    <p>{_esc(profile.summary)}</p>
</div>"""

    if profile.experiences:
        html += '<div class="section"><h2>Experience</h2>'
        for exp in profile.experiences:
            date = f"{exp.start_date} - {'Present' if exp.current else exp.end_date}"
            html += f"""<div class="exp-item">
                <span class="date">{_esc(date)}</span>
                <div class="title">{_esc(exp.title)}</div>
                <div class="company">{_esc(exp.company)}{f', {exp.location}' if exp.location else ''}</div>
                {'<p>' + _esc(exp.description) + '</p>' if exp.description else ''}
                {'<ul>' + ''.join(f'<li>{_esc(h)}</li>' for h in exp.highlights) + '</ul>' if exp.highlights else ''}
            </div>"""
        html += '</div>'

    if profile.education:
        html += '<div class="section"><h2>Education</h2>'
        for edu in profile.education:
            date = f"{edu.start_date or ''} - {edu.end_date or ''}".strip(" -")
            degree = edu.degree
            if edu.field_of_study:
                degree += f" in {edu.field_of_study}"
            html += f"""<div class="edu-item">
                <span class="date">{_esc(date)}</span>
                <div class="title">{_esc(edu.school)}</div>
                <div>{_esc(degree)}{f' | {edu.grade}' if edu.grade else ''}</div>
            </div>"""
        html += '</div>'

    if profile.skills:
        html += '<div class="section"><h2>Skills</h2><div class="skills">'
        for s in profile.skills:
            html += f'<span class="skill">{_esc(s)}</span>'
        html += '</div></div>'

    if profile.projects:
        html += '<div class="section"><h2>Projects</h2>'
        for proj in profile.projects:
            url = f' (<a href="{proj.url}">{_esc(proj.url.replace("https://",""))}</a>)' if proj.url else ''
            tech = f'<div class="project-tech">Tech: {", ".join(proj.technologies)}</div>' if proj.technologies else ''
            html += f"""<div style="margin-bottom:10px;">
                <div class="project-name">{_esc(proj.name)}{url}</div>
                <p>{_esc(proj.description)}</p>{tech}
            </div>"""
        html += '</div>'

    html += '</body></html>'
    return html


def _html_classic(profile: Profile) -> str:
    """Classic template — serif fonts, traditional layout."""
    return _html_modern(profile).replace("Segoe UI", "Georgia, serif").replace("#2962FF", "#1a1a1a")


def _html_minimal(profile: Profile) -> str:
    """Minimal template — clean, lots of whitespace."""
    return _html_modern(profile).replace("padding: 30px;", "padding: 20px;").replace("border-radius: 8px;", "border-left: 4px solid #2962FF; background: white;")


def _esc(text: str) -> str:
    """HTML escape."""
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
