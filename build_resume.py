#!/usr/bin/env python3
"""Generate Sohini Banerjee's resume as a designed A4 PDF (no external deps).

Layout: deep-blue sidebar (contact, skills, education, certifications) with a
clean main column (name, summary, achievements, focus, interests).
"""

PAGE_W, PAGE_H = 595.28, 841.89  # A4 in points

SIDEBAR_W = 214          # left column width (filled navy)
MAIN_X = 240             # main column left edge
RIGHT_M = 42             # main column right margin
MAIN_W = PAGE_W - MAIN_X - RIGHT_M

# Palette
NAVY    = (0.16, 0.23, 0.42)   # sidebar fill
ACCENT  = (0.30, 0.42, 0.75)   # headings / bars on main
TEXT    = (0.13, 0.16, 0.22)   # body text
MUTED   = (0.46, 0.49, 0.57)   # muted secondary text (main)
WHITE   = (1.00, 1.00, 1.00)
SIDE_MU = (0.80, 0.84, 0.92)   # muted text on sidebar

# Helvetica AFM widths (per 1000 units) for wrapping.
WIDTHS = {
    ' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667,
    '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333, '.': 278,
    '/': 278, '0': 556, '1': 556, '2': 556, '3': 556, '4': 556, '5': 556,
    '6': 556, '7': 556, '8': 556, '9': 556, ':': 278, ';': 278, '<': 584,
    '=': 584, '>': 584, '?': 556, '@': 1015, 'A': 667, 'B': 667, 'C': 722,
    'D': 722, 'E': 667, 'F': 611, 'G': 778, 'H': 722, 'I': 278, 'J': 500,
    'K': 667, 'L': 556, 'M': 833, 'N': 722, 'O': 778, 'P': 667, 'Q': 778,
    'R': 722, 'S': 667, 'T': 611, 'U': 722, 'V': 667, 'W': 944, 'X': 667,
    'Y': 667, 'Z': 611, '[': 278, '\\': 278, ']': 278, '^': 469, '_': 556,
    '`': 333, 'a': 556, 'b': 556, 'c': 500, 'd': 556, 'e': 556, 'f': 278,
    'g': 556, 'h': 556, 'i': 222, 'j': 222, 'k': 500, 'l': 222, 'm': 833,
    'n': 556, 'o': 556, 'p': 556, 'q': 556, 'r': 333, 's': 500, 't': 278,
    'u': 556, 'v': 500, 'w': 722, 'x': 500, 'y': 500, 'z': 500, '{': 334,
    '|': 260, '}': 334, '~': 584,
    '\u2022': 350, '\u2013': 333, '\u2014': 555, '@': 1015,
}

WIN = {"\u2022": "\x95", "\u2013": "\x96", "\u2014": "\x97", "\u2018": "\x91",
       "\u2019": "\x92", "\u201c": "\x93", "\u201d": "\x94", "\u2026": "\x85"}


def width(s, size):
    return sum(WIDTHS.get(c, 556) for c in s) * size / 1000.0


def win_enc(s):
    enc = "".join(WIN.get(c, c) for c in s).encode("latin-1", "replace")
    return enc.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def rgb(t):
    return "%.3f %.3f %.3f" % t


class Resume(object):
    """Low-level PDF content builder."""

    def __init__(self):
        self.pages = [[]]
        self.y = PAGE_H - 46

    def cur(self):
        return self.pages[-1]

    def ensure(self, needed):
        if self.y - needed < 40:
            self.new_page()

    def new_page(self):
        self.pages.append([])
        self.y = PAGE_H - 46

    def set_fill(self, color):
        self.cur().append(b"%s rg\n" % rgb(color).encode())

    def fill_rect(self, x, y, w, h, color=None):
        if color:
            self.cur().append(b"%s rg\n" % rgb(color).encode())
        self.cur().append(b"%s %s %s %s re f\n" % (
            str(x).encode(), str(y).encode(),
            str(w).encode(), str(h).encode()))

    def draw(self, x, y, s, size=10, font=b"/F1", color=TEXT, leading=13):
        self.ensure(leading)
        self.cur().append(b"%s rg\n" % rgb(color).encode())
        self.cur().append(
            b"BT\n%s %s Tf\n%s %s Td\n(%s) Tj\nET\n"
            % (font, str(size).encode(), str(x).encode(), str(y).encode(),
               win_enc(s)))
        self.y = y - leading
        return self.y

    def space(self, pts):
        self.y -= pts


class Sidebar(object):
    """White-on-navy content helpers for the left column."""

    def __init__(self, r):
        self.r = r
        self.x = 22
        self.maxw = SIDEBAR_W - 44

    def title(self, text):
        self.r.space(14)
        self.r.y -= 3
        self.r.fill_rect(self.x, self.r.y + 9, 28, 2.2, ACCENT)
        self.r.draw(self.x, self.r.y, text.upper(), size=9, font=b"/F2",
                    color=WHITE, leading=11)
        self.r.y -= 2

    def label_value(self, label, value, lead=11.5):
        self.r.ensure(lead * 2)
        self.r.draw(self.x, self.r.y, "".join(c for c in label.upper()),
                    size=7.2, font=b"/F2", color=SIDE_MU, leading=8.6)
        self.r.space(2)
        size = 8.6
        if width(value, size) > self.maxw:
            size = max(6.5, size * (self.maxw / width(value, size)))
        self.para(value, size=size, color=WHITE, maxw=self.maxw, lead=11.2)
        self.r.space(1)

    def bullet(self, text, size=8.6, lead=11.2, color=WHITE):
        self.r.ensure(lead)
        self.r.draw(self.x, self.r.y, "\u2022", size=size, color=ACCENT, leading=lead)
        self.r.y += lead - 2
        self.para(text, size=size, color=color, maxw=self.maxw - 12, indent=12, lead=lead)
        self.r.y -= 1

    def para(self, s, size=8.6, color=WHITE, maxw=None, indent=0, lead=11.2):
        maxw = maxw or self.maxw
        font = b"/F1"
        words = s.split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if width(trial, size) <= maxw - indent:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        self.r.ensure(len(lines) * lead)
        for ln in lines:
            self.r.draw(self.x + indent, self.r.y, ln, size=size, font=font,
                        color=color, leading=lead)
            self.r.y -= 1
        self.r.space(1)

    def line_blank(self):
        self.r.space(1)


class Main(object):
    """Helpers for the main (white) column."""

    def __init__(self, r):
        self.r = r
        self.x = MAIN_X
        self.maxw = MAIN_W

    def title(self, text):
        self.r.ensure(20)
        self.r.space(6)
        self.r.fill_rect(self.x, self.r.y + 10, 30, 2.4, ACCENT)
        self.r.draw(self.x, self.r.y, text.upper(), size=10.5, font=b"/F2",
                    color=NAVY, leading=12)
        self.r.y -= 5

    def para(self, s, size=9.5, color=TEXT, indent=0, maxw=None, bold=False,
             lead=13.2):
        maxw = maxw or self.maxw
        font = b"/F2" if bold else b"/F1"
        words = s.split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if width(trial, size) <= maxw - indent:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        self.r.ensure(len(lines) * lead)
        for ln in lines:
            self.r.draw(self.x + indent, self.r.y, ln, size=size, font=font,
                        color=color, leading=lead)
            self.r.y -= 1
        self.r.space(2)

    def ace_bullet(self, s, size=9.5, lead=13.2):
        self.r.ensure(lead)
        by = self.r.y - 3
        self.r.fill_rect(self.x, by, 5.2, 5.2, ACCENT)
        self.r.y -= 1
        self.para(s, size=size, indent=14, lead=lead)
        self.r.y -= 1

    def role(self, role, meta):
        self.r.ensure(30)
        self.r.draw(self.x, self.r.y, role, size=10.5, font=b"/F2",
                    color=TEXT, leading=13.5)
        self.r.draw(self.x, self.r.y, meta, size=9, font=b"/F3",
                    color=MUTED, leading=11.5)
        self.r.space(2)


def build():
    r = Resume()
    side = Sidebar(r)
    main = Main(r)

    # ---- Sidebar fill (full height) ----
    r.fill_rect(0, 0, SIDEBAR_W, PAGE_H, NAVY)

    # ================= SIDEBAR =================
    r.y = PAGE_H - 60
    side.title("Contact")
    side.label_value("Email", "sohini1236@gmail.com")
    side.label_value("Phone", "+91 8013250607 (WhatsApp)")
    side.label_value("Location", "Ichhapur, West Bengal, India")
    side.label_value("LinkedIn", "linkedin.com/in/sohini-banerjee-4b967115b")

    side.title("Skills")
    side.bullet("Project Management & Planning (Project+)")
    side.bullet("Agile Project Management · Scrum · Kanban")
    side.bullet("Team Coordination & Stakeholder Management")
    side.bullet("Conflict Resolution & Teamwork")
    side.bullet("Public Speaking & Presentations")
    side.bullet("Recruitment & Onboarding")
    side.bullet("International Project Experience")
    side.bullet("MS Office · Google Workspace")
    side.bullet("HTML/CSS · Python/SQL · Procedural Programming")

    side.title("Education")
    side.bullet("BTech, Computer Science & Engineering - Hooghly Engineering & Technology College (2025)")
    side.bullet("Class X & XII - Kendriya Vidyalaya No. 1, Ichhapore")

    side.title("Certifications")
    side.bullet("Google Project Management (Coursera) - 6 courses, 2025", lead=12.4)
    side.bullet("Accelerate Your Job Search (LinkedIn Learning)")

    # ================= MAIN =================
    r.y = PAGE_H - 66
    r.draw(MAIN_X, r.y, "SOHINI", size=24, font=b"/F2", color=NAVY, leading=27)
    r.draw(MAIN_X, r.y, "BANERJEE", size=24, font=b"/F2", color=ACCENT, leading=27)
    r.y -= 2
    r.draw(MAIN_X, r.y,
           "Project Management  |  Marketing  |  HR  |  Teaching",
           size=9.5, font=b"/F3", color=MUTED, leading=12)
    r.y -= 7
    r.fill_rect(MAIN_X, r.y + 3, MAIN_W, 0.9, ACCENT)
    r.space(8)

    main.title("Professional Summary")
    main.para(
        "Engineer by degree, communicator by instinct, organizer at heart. A 2025 BTech (CSE) graduate who "
        "swapped code for coordination - now Google-certified in Project Management and a first-position "
        "debate champion in English and Hindi. I bring the same energy I used winning debates to planning "
        "projects, rallying teams, and making complex ideas simple. Seeking an entry-level role in project "
        "management, marketing, HR, or training where I can learn fast and deliver real impact.")

    main.title("Experience")
    main.role("Project Management Intern",
              "Pehchaan The Street School (Trust) · Remote · 2026 (2-week programme)")
    main.ace_bullet("Coordinated volunteers and assisted with planning and delivery of initiatives supporting "
                    "street-school students")
    main.ace_bullet("Tracked deadlines and kept distributed team members aligned on schedules, tasks, "
                    "and follow-ups")
    main.ace_bullet("Pitched and promoted campaigns to drive participation and awareness, translating the "
                    "team's goals into clear calls to action")

    main.title("Achievements")
    main.ace_bullet("Debate Champion - first position in English and Hindi debate competitions, showcasing "
                    "exceptional public speaking, argumentation, and quick thinking")
    main.ace_bullet("Extempore Champion - recognized for confident, on-the-spot speaking before groups")
    main.ace_bullet("Poetry Recitation - first in English, third in Hindi, highlighting creativity and "
                    "expressive communication")
    main.ace_bullet("Organizational Recognition - appreciation certificate from the General Manager, "
                    "Metal & Steel Factory, for first position in their organizational debate")

    main.title("Interests")
    main.para("Teaching & sharing knowledge, public speaking, writing, management analytics, and learning "
              "people-management practices.")

    return r.pages


def serialize(pages):
    out = []
    next_obj = 1
    catalog_obj = next_obj; next_obj += 1
    pages_obj = next_obj; next_obj += 1
    f1_obj = next_obj; next_obj += 1
    f2_obj = next_obj; next_obj += 1
    f3_obj = next_obj; next_obj += 1

    content_nums, page_nums = [], []
    for _ in pages:
        content_nums.append(next_obj); next_obj += 1
        page_nums.append(next_obj); next_obj += 1

    out.append(b"%d 0 obj << /Type /Catalog /Pages %d 0 R >> endobj\n"
               % (catalog_obj, pages_obj))
    kids = b" ".join(b"%d 0 R" % p for p in page_nums)
    out.append(b"%d 0 obj << /Type /Pages /Kids [%s] /Count %d >> endobj\n"
               % (pages_obj, kids, len(pages)))
    out.append(b"%d 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n" % f1_obj)
    out.append(b"%d 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj\n" % f2_obj)
    out.append(b"%d 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >> endobj\n" % f3_obj)

    res = (b"<< /Font << /F1 %d 0 R /F2 %d 0 R /F3 %d 0 R >> >>"
           % (f1_obj, f2_obj, f3_obj))
    for cn, pn, ops in zip(content_nums, page_nums, pages):
        stream = b"\n".join(ops)
        out.append(b"%d 0 obj << /Length %d >>\nstream\n%s\nendstream\nendobj\n"
                   % (cn, len(stream), stream))
        out.append(b"%d 0 obj << /Type /Page /Parent %d 0 R /MediaBox [0 0 %s %s] "
                   b"/Resources %s /Contents %d 0 R >> endobj\n"
                   % (pn, pages_obj, str(PAGE_W).encode(), str(PAGE_H).encode(), res, cn))

    header = b"%PDF-1.4\n"
    parts = [header] + out
    body = b"".join(parts)

    offsets, pos = [], len(header)
    for b in out:
        offsets.append(pos)
        pos += len(b)

    xref = b"xref\n0 %d\n0000000000 65535 f \n" % next_obj
    for o in offsets:
        xref += b"%010d 00000 n \n" % o
    trailer = (b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
               % (next_obj, catalog_obj, len(body)))
    return body + xref + trailer


if __name__ == "__main__":
    pages = build()
    data = serialize(pages)
    with open("resume/SohiniBanerjee-Resume.pdf", "wb") as f:
        f.write(data)
    print("PDF written: resume/SohiniBanerjee-Resume.pdf  pages:", len(pages))