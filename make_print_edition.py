"""Compile the project reports and figures into a dated, printable PDF.

Usage: python make_print_edition.py
Output: ../bendlab_print_edition_<date>.pdf  (next to the repo, not inside
it: the dated snapshot is stored separately from the repository it records).

Every page carries the snapshot date in the footer so that pages from
different versions can be distinguished. The script contains a minimal
Markdown renderer based on fpdf2, supporting headings, paragraphs, lists,
code blocks, tables and full-width images.
"""

import re
import datetime
import numpy as np  # noqa: F401  (kept for parity with repo scripts)
from fpdf import FPDF

DATE = "2026-10-14"
DOCS = [
    ("README.md", "Repository overview"),
    ("PROBLEM_STATEMENT.md", "Problem statement"),
    ("docs/EXPLAINER.md", "Project overview"),
    ("docs/EXPLAINER_PART2.md", "Project overview: experiment series and validation"),
    ("docs/RESULTS_ROUND0.md", "Results I: model fitting and parameter degeneracy"),
    ("docs/RESULTS_ROUND1.md", "Results II: experiment series 1 and independent audit"),
    ("docs/RESULTS_ROUND2_ZT9.md", "Results III: ZT9 diagnostic analysis"),
    ("docs/ADAPTIVE_IDENTIFICATION.md", "Adaptive identification experiment: design specification"),
    ("docs/DATA_SOURCES.md", "Data sources"),
    ("docs/DATA_CONTRACT.md", "Data contract"),
]
EXTRA_FIGS = [("results/figures/real_seedlings_dashboard.png",
               "Appendix A: measured sunflower trajectories and model predictions"),
              ("results/figures/zt9_diagnostic_dashboard.png",
               "Appendix B: ZT9 diagnostic analysis")]

SAFE = {0x2014: "-", 0x2013: "-", 0x2026: "...", 0x2192: "->",
        0x2212: "-", 0x2265: ">=", 0x2264: "<=", 0x2248: "~",
        0x00D7: "x", 0x2019: "'", 0x2018: "'", 0x201C: '"', 0x201D: '"',
        0x207B: "-", 0x00B9: "1", 0x00B2: "2", 0x00B3: "3", 0x2074: "4"}


def safe(s):
    # Render mathematical notation readably with the core PDF fonts:
    # remove TeX delimiters and expand the small set of commands used here.
    s = s.replace("$$", "").replace("$", "")
    for tex, plain in ((r"\dot{\theta}", "d(theta)/dt"),
                       (r"\dot{r}", "d(r)/dt"),
                       (r"\operatorname{clip}", "clip"),
                       (r"\theta", "theta"), (r"\tau", "tau"),
                       (r"\phi", "phi"), (r"\varepsilon", "epsilon"),
                       (r"\sin", "sin"), (r"\times", "x"),
                       (r"_{\max}", "_max"), (r"^\circ", " deg"),
                       (r"\mathrm{h}", "h"), (r"\left", ""),
                       (r"\right", ""), (r"\qquad", " "), (r"\,", " "),
                       (r"\!", "")):
        s = s.replace(tex, plain)
    return s.translate(SAFE)


class Print(FPDF):
    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120)
        self.cell(0, 8, "BendLab print edition, snapshot %s - page %d/%d"
                  % (DATE, self.page_no(), self.pages_count), align="C")
        self.set_text_color(0)


pdf = Print()
pdf.set_auto_page_break(True, 20)

# ---- cover page -------------------------------------------------------------
pdf.add_page()
pdf.set_font("Helvetica", "B", 30)
pdf.cell(0, 20, "BendLab", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 13)
pdf.cell(0, 9, "Parameter identifiability in a minimal model of phototropic stem bending",
         align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 9, "PRINT EDITION - snapshot of %s" % DATE, align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 10)
pdf.multi_cell(0, 6, align="C", text=(
    "Anadi Tripathi and Umaid. This print edition reproduces the contents of the\n"
    "GitHub repository Yash-Tripath1/Bendlab as a dated snapshot. The snapshot\n"
    "date is printed in the footer of every page so that versions can be\n"
    "distinguished."))
pdf.ln(8)
pdf.set_font("Helvetica", "B", 12)
pdf.cell(0, 8, "Contents", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 10)
for _, label in DOCS:
    pdf.cell(0, 6.5, "-  " + label, new_x="LMARGIN", new_y="NEXT")
for _, label in EXTRA_FIGS:
    pdf.cell(0, 6.5, "-  " + label, new_x="LMARGIN", new_y="NEXT")

INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def render_inline(text, size):
    for chunk in INLINE.split(safe(text)):
        if not chunk:
            continue
        if chunk.startswith("**"):
            pdf.set_font("Helvetica", "B", size)
            pdf.write(5, chunk[2:-2])
            pdf.set_font("Helvetica", "", size)
        elif chunk.startswith("`"):
            pdf.set_font("Courier", "", size - 1)
            pdf.write(5, chunk[1:-1])
            pdf.set_font("Helvetica", "", size)
        elif chunk.startswith("["):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", chunk)
            pdf.set_font("Helvetica", "B", size)
            pdf.write(5, m.group(1))
            pdf.set_font("Helvetica", "", size - 1)
            pdf.write(5, " (" + m.group(2) + ")")
            pdf.set_font("Helvetica", "", size)
        elif chunk.startswith("*") and len(chunk) > 2:
            pdf.set_font("Helvetica", "I", size)
            pdf.write(5, chunk[1:-1])
            pdf.set_font("Helvetica", "", size)
        else:
            pdf.write(5, chunk)


def wrap(text, w):
    out, cur = [], ""
    for word in text.replace("\n", " ").split():
        while len(word) > w:
            space = w - len(cur)
            if space > 0:
                cur += word[:space]
                word = word[space:]
            out.append(cur)
            cur = ""
        if cur and len(cur) + len(word) + 1 > w:
            out.append(cur)
            cur = ""
        cur = (cur + " " + word).strip()
    if cur:
        out.append(cur)
    return out or [""]


def render_table(lines):
    rows = []
    for ln in lines:
        cells = [safe(c.strip()) for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    ncol = max(len(r) for r in rows)
    widths = {2: [34, 70], 3: [26, 30, 48], 4: [22, 24, 28, 30]}
    wch = widths.get(ncol, [104 // ncol] * ncol)
    chw = 1.55  # courier 7.5pt char width, mm
    pdf.set_font("Courier", "B", 7.5)
    for i, r in enumerate(rows):
        wrapped = [wrap(c, w) for c, w in zip(r + [""] * (ncol - len(r)), wch)]
        h = max(len(w) for w in wrapped)
        if pdf.get_y() + h * 4.2 > 275:
            pdf.add_page()
        pdf.set_font("Courier", "B" if i == 0 else "", 7.5)
        for li in range(h):
            x = 12
            for w, col in zip(wch, wrapped):
                pdf.set_xy(x, pdf.get_y() if li == 0 else pdf.get_y())
                pdf.cell(w * chw, 4.2, (col[li] if li < len(col) else "")[:w])
                x += w * chw
            pdf.ln(4.2)
        if i == 0:
            pdf.set_font("Courier", "", 7.5)
    pdf.ln(3)


def render_doc(path):
    pdf.add_page()
    lines = open(path, encoding="utf-8").read().split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            pdf.set_font("Courier", "", 7.5)
            pdf.set_fill_color(240)
            for cl in code:
                if pdf.get_y() > 272:
                    pdf.add_page()
                    pdf.set_font("Courier", "", 7.5)
                    pdf.set_fill_color(240)
                for piece in [cl[j:j + 105] for j in range(0, max(len(cl), 1), 105)] or [""]:
                    pdf.cell(0, 4.2, "  " + safe(piece), fill=True,
                             new_x="LMARGIN", new_y="NEXT")
            pdf.set_fill_color(255)
            pdf.ln(2)
            continue
        m = re.match(r"!?\[([^\]]*)\]\(([^)]+)\)", s)
        if m and s.startswith("!") and (m.group(2).endswith(".png")
                                        or m.group(2).endswith(".jpg")):
            if pdf.get_y() > 150:
                pdf.add_page()
            pdf.image(m.group(2), x=12, w=186)
            pdf.set_font("Helvetica", "I", 8)
            pdf.cell(0, 5, safe(m.group(1)), align="C",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            i += 1
            continue
        if s.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            render_table(tbl)
            continue
        if s.startswith("#"):
            lvl = len(s) - len(s.lstrip("#"))
            sizes = {1: 17, 2: 13, 3: 11}
            if pdf.get_y() > 260:
                pdf.add_page()
            pdf.ln(3 if lvl == 1 else 2)
            pdf.set_font("Helvetica", "B", sizes.get(lvl, 10))
            pdf.multi_cell(0, 7, safe(s.lstrip("# ").strip()))
            pdf.ln(1)
            i += 1
            continue
        if s in ("---", "***"):
            pdf.ln(2)
            pdf.set_draw_color(160)
            pdf.line(12, pdf.get_y(), 198, pdf.get_y())
            pdf.ln(3)
            i += 1
            continue
        if s.startswith(">"):
            pdf.set_x(18)
            pdf.set_font("Helvetica", "I", 9.5)
            pdf.multi_cell(180, 5, safe(s.lstrip("> ")))
            pdf.ln(2)
            i += 1
            continue
        if s.startswith(("- ", "* ")) or re.match(r"\d+\. ", s):
            marker = "  -  " if not s[0].isdigit() else "  " + s.split(" ")[0] + "  "
            body = re.sub(r"^(\d+\. |- |\* )", "", s)
            if pdf.get_y() > 268:
                pdf.add_page()
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(10, 5.5, marker.strip())
            pdf.set_x(22)
            render_inline(body, 10)
            pdf.ln(6)
            i += 1
            continue
        para = [s]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r"(#|```|\||!|\[|>|- |\* |\d+\. )", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        if pdf.get_y() > 268:
            pdf.add_page()
        pdf.set_font("Helvetica", "", 10)
        render_inline(" ".join(para), 10)
        pdf.ln(7)


for path, _ in DOCS:
    render_doc(path)

for path, label in EXTRA_FIGS:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, label, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.image(path, x=6, w=198)

out = "../bendlab_print_edition_%s.pdf" % DATE
pdf.output(out)
print("wrote", out, "pages:", pdf.pages_count)
