#!/usr/bin/env python3
"""
Generate the Mutual Non-Disclosure, Confidentiality and Non-Circumvention
Agreement PDF for a medical robotics / engineering-innovation sales company.

Usage:
    python3 scripts/generate_nda.py [output.pdf]

Dependencies:
    pip install reportlab
"""

import sys

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Frame, KeepTogether, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# --------------------------------------------------------------------------
# Palette and page geometry
# --------------------------------------------------------------------------
NAVY = HexColor('#1F3A5F')
SLATE = HexColor('#43586E')
GOLD = HexColor('#8A6A34')
CRIMSON = HexColor('#7B2D26')
GREEN = HexColor('#2F5D46')
LIGHT = HexColor('#EDF1F6')
LIGHTER = HexColor('#F7F9FB')
BORDER = HexColor('#C2CDDA')
RULE = HexColor('#93A3B5')
MUTED = HexColor('#5C6B7A')

PAGE_W, PAGE_H = letter
LM = RM = 0.8 * inch
TM = 0.85 * inch
BM = 0.85 * inch
CONTENT_W = PAGE_W - LM - RM          # 6.9in == 496.8pt
TOC_TITLE_GAP = 30.0                  # room for the TOC page title

COMPANY = "[COMPANY LEGAL NAME, INC.]"
SHORT_NAME = "[COMPANY]"
DOC_TITLE = "Mutual NDA, Confidentiality and Non-Circumvention Agreement"
REVISION = "Rev. 1.0"

# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------
_ss = getSampleStyleSheet()

S = {}
S['body'] = ParagraphStyle(
    'body', parent=_ss['Normal'], fontName='Times-Roman', fontSize=8.3,
    leading=10.0, alignment=TA_JUSTIFY, spaceAfter=3.2,
    textColor=colors.black)
S['body_first'] = ParagraphStyle('body_first', parent=S['body'], spaceBefore=1)
S['bullet'] = ParagraphStyle(
    'bullet', parent=S['body'], leftIndent=15, bulletIndent=5,
    spaceAfter=1.4, bulletFontName='Times-Roman')
S['subbullet'] = ParagraphStyle(
    'subbullet', parent=S['bullet'], leftIndent=36, bulletIndent=24, fontSize=9)
S['h1'] = ParagraphStyle(
    'h1', parent=_ss['Normal'], fontName='Helvetica-Bold', fontSize=10.2,
    leading=12.2, textColor=NAVY, spaceBefore=8, spaceAfter=1)
S['h2'] = ParagraphStyle(
    'h2', parent=_ss['Normal'], fontName='Helvetica-Bold', fontSize=8.2,
    leading=10.2, textColor=SLATE, spaceBefore=4, spaceAfter=0.5)
S['h3'] = ParagraphStyle(
    'h3', parent=_ss['Normal'], fontName='Helvetica-BoldOblique', fontSize=8.8,
    leading=11, textColor=MUTED, spaceBefore=6, spaceAfter=2)
S['cell'] = ParagraphStyle(
    'cell', parent=_ss['Normal'], fontName='Times-Roman', fontSize=7.3,
    leading=9.0, alignment=TA_JUSTIFY)
S['cell_l'] = ParagraphStyle('cell_l', parent=S['cell'], alignment=0)
S['cell_b'] = ParagraphStyle(
    'cell_b', parent=S['cell_l'], fontName='Times-Bold')
S['cell_h'] = ParagraphStyle(
    'cell_h', parent=_ss['Normal'], fontName='Helvetica-Bold', fontSize=7.0,
    leading=8.8, textColor=colors.white, alignment=0)
S['callout'] = ParagraphStyle(
    'callout', parent=_ss['Normal'], fontName='Times-Roman', fontSize=7.7,
    leading=9.8, alignment=TA_JUSTIFY, textColor=HexColor('#2A3440'))
S['callout_h'] = ParagraphStyle(
    'callout_h', parent=_ss['Normal'], fontName='Helvetica-Bold', fontSize=7.6,
    leading=10, textColor=NAVY, spaceAfter=2)
S['caption'] = ParagraphStyle(
    'caption', parent=_ss['Normal'], fontName='Helvetica-Oblique', fontSize=7.2,
    leading=9.2, textColor=MUTED, alignment=TA_CENTER, spaceBefore=7,
    spaceAfter=6)
S['fig_title'] = ParagraphStyle(
    'fig_title', parent=_ss['Normal'], fontName='Helvetica-Bold', fontSize=7.6,
    leading=9.6, textColor=NAVY, spaceBefore=5, spaceAfter=4)

# Cover styles
S['cover_kicker'] = ParagraphStyle(
    'cover_kicker', parent=_ss['Normal'], fontName='Helvetica-Bold',
    fontSize=8.5, leading=12, textColor=GOLD, alignment=TA_CENTER)
S['cover_title'] = ParagraphStyle(
    'cover_title', parent=_ss['Normal'], fontName='Times-Bold', fontSize=23,
    leading=27, textColor=NAVY, alignment=TA_CENTER)
S['cover_sub'] = ParagraphStyle(
    'cover_sub', parent=_ss['Normal'], fontName='Times-Italic', fontSize=12,
    leading=16, textColor=SLATE, alignment=TA_CENTER)
S['cover_meta'] = ParagraphStyle(
    'cover_meta', parent=_ss['Normal'], fontName='Times-Roman', fontSize=9.5,
    leading=14, alignment=TA_CENTER, textColor=colors.black)
S['toc_note'] = ParagraphStyle(
    'toc_note', parent=S['body'], fontSize=7.5, leading=9.6,
    textColor=MUTED, alignment=TA_JUSTIFY)
S['sig'] = ParagraphStyle(
    'sig', parent=_ss['Normal'], fontName='Times-Roman', fontSize=8.5,
    leading=13)
S['sig_h'] = ParagraphStyle(
    'sig_h', parent=_ss['Normal'], fontName='Helvetica-Bold', fontSize=8,
    leading=11, textColor=NAVY, spaceAfter=1)


# --------------------------------------------------------------------------
# Flowable helpers
# --------------------------------------------------------------------------
def P(text, style='body'):
    return Paragraph(text, S[style])


def H1(number, text):
    p = Paragraph('%s.&nbsp;&nbsp;%s' % (number, text.upper()), S['h1'])
    p.toc_level = 0
    p.toc_text = '%s. %s' % (number, text)
    return p


def H2(number, text):
    label = ('%s&nbsp;&nbsp;%s' % (number, text)) if number else text
    p = Paragraph(label, S['h2'])
    p.toc_level = 1
    p.toc_text = ('%s %s' % (number, text)) if number else text
    return p


def H1_plain(text):
    p = Paragraph(text.upper(), S['h1'])
    p.toc_level = 0
    p.toc_text = text
    return p


def rule(color=RULE, thickness=0.7, space_before=1, space_after=7,
         width=None):
    t = Table([['']], colWidths=[width or CONTENT_W],
              rowHeights=[0.1])
    t.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), thickness, color),
        ('TOPPADDING', (0, 0), (-1, -1), space_before),
        ('BOTTOMPADDING', (0, 0), (-1, -1), space_after),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t


def bullets(items, style='bullet', marker='•'):
    return [Paragraph(t, S[style], bulletText=marker) for t in items]


def lettered(items, style='bullet'):
    out = []
    for i, t in enumerate(items):
        out.append(Paragraph(t, S[style],
                             bulletText='(%s)' % chr(ord('a') + i)))
    return out


def data_table(rows, col_widths, header=True, align_first_left=True,
               font_size=8.3, zebra=True):
    """rows[0] is the header row when header=True. Cells may be str or flowable."""
    data = []
    for r_i, row in enumerate(rows):
        out_row = []
        for c_i, cell in enumerate(row):
            if isinstance(cell, str):
                if header and r_i == 0:
                    out_row.append(Paragraph(cell, S['cell_h']))
                elif c_i == 0 and align_first_left:
                    out_row.append(Paragraph(cell, S['cell_b']))
                else:
                    out_row.append(Paragraph(cell, S['cell_l']))
            else:
                out_row.append(cell)
        data.append(out_row)

    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]
    if header:
        style += [
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('LINEBELOW', (0, 0), (-1, 0), 0.6, NAVY),
        ]
    if zebra:
        start = 1 if header else 0
        for i in range(start, len(data)):
            if (i - start) % 2 == 1:
                style.append(('BACKGROUND', (0, i), (-1, i), LIGHTER))
    t.setStyle(TableStyle(style))
    return t


def callout(label, text, accent=NAVY, bg=LIGHT):
    """Left-accented sidebar box used for Examples, Notes and Cautions."""
    inner = [Paragraph(label.upper(), S['callout_h']), Paragraph(text, S['callout'])]
    t = Table([['', inner]], colWidths=[3.2, CONTENT_W - 3.2])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), accent),
        ('BACKGROUND', (1, 0), (1, 0), bg),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('TOPPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ('LEFTPADDING', (1, 0), (1, 0), 8),
        ('RIGHTPADDING', (1, 0), (1, 0), 8),
        ('TOPPADDING', (1, 0), (1, 0), 5),
        ('BOTTOMPADDING', (1, 0), (1, 0), 5),
        ('BOX', (1, 0), (1, 0), 0.4, BORDER),
    ]))
    return KeepTogether([Spacer(1, 2), t, Spacer(1, 5)])


def signature_pair(left_role, left_party, right_role, right_party):
    """Two execution blocks side by side — half the height of stacked ones."""
    def col(role, party):
        return [
            Paragraph('<b>%s</b>' % role, S['sig_h']),
            Paragraph(party, S['sig']),
            Spacer(1, 7),
            Paragraph('By: _________________________________', S['sig']),
            Paragraph('Name: _______________________________', S['sig']),
            Paragraph('Title: ______________________________', S['sig']),
            Paragraph('Date: _______________________________', S['sig']),
            Paragraph('Notices: ____________________________', S['sig']),
        ]
    w = (CONTENT_W - 18) / 2.0
    t = Table([[col(left_role, left_party), col(right_role, right_party)]],
              colWidths=[w, w])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('LEFTPADDING', (1, 0), (1, 0), 18),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LINEBEFORE', (1, 0), (1, 0), 0.4, BORDER),
    ]))
    return t


def signature_block(role, party_label):
    rows = [
        [Paragraph('<b>%s</b>' % role, S['sig']), ''],
        [Paragraph('Entity: %s' % party_label, S['sig']), ''],
        [Paragraph('By: __________________________________', S['sig']),
         Paragraph('Date: ____________________', S['sig'])],
        [Paragraph('Name: ________________________________', S['sig']),
         Paragraph('Title: ____________________', S['sig'])],
        [Paragraph('Email for notices: ______________________________________',
                   S['sig']), ''],
    ]
    t = Table(rows, colWidths=[CONTENT_W * 0.58, CONTENT_W * 0.42])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 4), (1, 4)),
    ]))
    return t


def fill_lines(labels, col_widths):
    rows = [[Paragraph(l, S['cell_l']) for l in labels]]
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


# --------------------------------------------------------------------------
# Vector illustrations
# --------------------------------------------------------------------------
def flow_diagram(items, width=CONTENT_W, box_h=46, gap=19):
    """items: list of list-of-lines. First line is rendered bold."""
    n = len(items)
    box_w = (width - gap * (n - 1)) / float(n)
    d = Drawing(width, box_h + 16)
    cy = 8 + box_h / 2.0
    for i, lines in enumerate(items):
        x = i * (box_w + gap)
        d.add(Rect(x, 8, box_w, box_h, rx=3, ry=3,
                   fillColor=LIGHT, strokeColor=NAVY, strokeWidth=0.8))
        d.add(Rect(x, 8, box_w, 3, rx=0, ry=0,
                   fillColor=NAVY, strokeColor=None))
        d.add(String(x + 5, 8 + box_h - 10, 'STEP %d' % (i + 1),
                     fontName='Helvetica-Bold', fontSize=5.6, fillColor=GOLD))
        ty = 8 + box_h - 20
        for j, ln in enumerate(lines):
            d.add(String(x + box_w / 2.0, ty, ln, textAnchor='middle',
                         fontName='Helvetica-Bold' if j == 0 else 'Helvetica',
                         fontSize=6.9 if j == 0 else 6.3,
                         fillColor=NAVY if j == 0 else MUTED))
            ty -= 8.4
        if i < n - 1:
            ax0 = x + box_w + 4
            ax1 = x + box_w + gap - 4
            d.add(Line(ax0, cy, ax1 - 4.5, cy, strokeColor=SLATE,
                       strokeWidth=1.2))
            d.add(Polygon([ax1 - 5, cy - 3.4, ax1, cy, ax1 - 5, cy + 3.4],
                          fillColor=SLATE, strokeColor=SLATE))
    return d


def ladder_diagram(steps, width=CONTENT_W):
    """steps: list of (label, note), rendered narrow-to-wide, top to bottom.

    The label sits inside the bar; the note runs on its own full-width line
    beneath it, so a long note can never overflow a narrow bar.
    """
    bar_h, note_h, gap = 16.0, 10.0, 5.0
    row_h = bar_h + note_h + gap
    n = len(steps)
    d = Drawing(width, n * row_h)
    shades = [HexColor('#7C93AC'), HexColor('#5B7796'),
              HexColor('#3E5A78'), HexColor('#1F3A5F')]
    while len(shades) < n:
        shades.append(NAVY)
    for i, (label, note) in enumerate(steps):
        top = (n - 1 - i) * row_h
        y = top + note_h
        w = width * (0.44 + (0.56 / max(1, n - 1)) * i)
        d.add(Rect(0, y, w, bar_h, rx=2, ry=2,
                   fillColor=shades[i], strokeColor=None))
        d.add(String(8, y + 5, '%d.  %s' % (i + 1, label.upper()),
                     fontName='Helvetica-Bold', fontSize=7.0,
                     fillColor=colors.white))
        d.add(String(8, top + 1.5, note, fontName='Helvetica', fontSize=6.4,
                     fillColor=MUTED))
    return d


def figure(title, drawing, caption):
    return KeepTogether([
        Paragraph(title, S['fig_title']),
        drawing,
        Paragraph(caption, S['caption']),
    ])


# --------------------------------------------------------------------------
# Document template: running header / footer, outline, TOC notification
# --------------------------------------------------------------------------
class NDACanvas(pdfcanvas.Canvas):
    """Two-pass canvas so the footer can print 'Page X of Y'."""

    def __init__(self, *args, **kwargs):
        pdfcanvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_states = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self._decorate(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _decorate(self, total):
        self.saveState()
        # Running header
        self.setFont('Helvetica-Bold', 6.8)
        self.setFillColor(NAVY)
        self.drawString(LM, PAGE_H - 0.50 * inch, DOC_TITLE.upper())
        self.setFont('Helvetica-Bold', 6.8)
        self.setFillColor(CRIMSON)
        self.drawRightString(PAGE_W - RM, PAGE_H - 0.50 * inch,
                             'CONFIDENTIAL — RESTRICTED')
        self.setStrokeColor(RULE)
        self.setLineWidth(0.6)
        self.line(LM, PAGE_H - 0.60 * inch, PAGE_W - RM, PAGE_H - 0.60 * inch)

        # Running footer
        self.setStrokeColor(RULE)
        self.setLineWidth(0.6)
        self.line(LM, BM - 0.22 * inch, PAGE_W - RM, BM - 0.22 * inch)
        self.setFont('Helvetica', 6.6)
        self.setFillColor(MUTED)
        self.drawString(LM, BM - 0.36 * inch,
                        'Agreement No. [________]   |   Initials:  ____ / ____')
        self.drawCentredString(PAGE_W / 2.0, BM - 0.36 * inch,
                               'Page %d of %d' % (self._pageNumber, total))
        self.drawRightString(PAGE_W - RM, BM - 0.36 * inch,
                             '%s  |  %s' % (SHORT_NAME, REVISION))
        self.restoreState()


class NDADoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self, filename, pagesize=letter,
                                 leftMargin=LM, rightMargin=RM,
                                 topMargin=TM, bottomMargin=BM,
                                 title=DOC_TITLE,
                                 author=COMPANY,
                                 subject=('Confidentiality, non-disclosure and '
                                          'non-circumvention agreement'),
                                 creator='%s Legal Department' % SHORT_NAME,
                                 **kw)
        cover_frame = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM,
                            id='cover', leftPadding=0, rightPadding=0,
                            topPadding=0, bottomPadding=0)
        body_frame = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM,
                           id='body', leftPadding=0, rightPadding=0,
                           topPadding=0, bottomPadding=0)
        gutter = 20.0
        col_w = (CONTENT_W - gutter) / 2.0
        toc_h = PAGE_H - TM - BM - TOC_TITLE_GAP
        toc_frames = [
            Frame(LM, BM, col_w, toc_h, id='toc-left', leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0),
            Frame(LM + col_w + gutter, BM, col_w, toc_h, id='toc-right',
                  leftPadding=0, rightPadding=0, topPadding=0,
                  bottomPadding=0),
        ]
        self.addPageTemplates([
            PageTemplate(id='cover', frames=[cover_frame],
                         onPage=self._draw_cover_frame),
            PageTemplate(id='toc', frames=toc_frames,
                         onPage=self._draw_toc_title),
            PageTemplate(id='body', frames=[body_frame]),
        ])
        self._bookmark_n = 0

    @staticmethod
    def _draw_cover_frame(canv, doc):
        canv.saveState()
        canv.setStrokeColor(NAVY)
        canv.setLineWidth(1.6)
        canv.rect(0.55 * inch, 0.55 * inch, PAGE_W - 1.10 * inch,
                  PAGE_H - 1.10 * inch)
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(0.6)
        canv.rect(0.63 * inch, 0.63 * inch, PAGE_W - 1.26 * inch,
                  PAGE_H - 1.26 * inch)
        canv.restoreState()

    @staticmethod
    def _draw_toc_title(canv, doc):
        canv.saveState()
        canv.setFont('Helvetica-Bold', 10.8)
        canv.setFillColor(NAVY)
        canv.drawString(LM, PAGE_H - TM - 11, 'TABLE OF CONTENTS')
        canv.setStrokeColor(NAVY)
        canv.setLineWidth(1.0)
        canv.line(LM, PAGE_H - TM - 18, PAGE_W - RM, PAGE_H - TM - 18)
        canv.bookmarkPage('toc')
        canv.addOutlineEntry('Table of Contents', 'toc', level=0, closed=True)
        canv.restoreState()

    def beforeDocument(self):
        # Reset per build pass: multiBuild compares TOC entries between
        # passes, so the bookmark keys must be identical each time or the
        # index never registers as resolved.
        self._bookmark_n = 0

    def afterFlowable(self, flowable):
        text = getattr(flowable, 'toc_text', None)
        if text is None:
            return
        level = getattr(flowable, 'toc_level', 0)
        self._bookmark_n += 1
        key = 'bm%d' % self._bookmark_n
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=(level == 0))
        self.notify('TOCEntry', (level, text, self.page, key))


def build_toc():
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle('toc0', fontName='Helvetica-Bold', fontSize=7.9,
                       leading=10.6, textColor=NAVY, leftIndent=0,
                       firstLineIndent=0, spaceBefore=3.5, spaceAfter=0.5),
        ParagraphStyle('toc1', fontName='Times-Roman', fontSize=7.3,
                       leading=8.6, textColor=HexColor('#33414F'),
                       leftIndent=10, firstLineIndent=0, spaceBefore=0),
    ]
    toc.dotsMinLevel = 0
    return toc


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------
def cover_page():
    s = []
    s.append(Spacer(1, 74))
    s.append(P('CONFIDENTIAL LEGAL INSTRUMENT', 'cover_kicker'))
    s.append(Spacer(1, 4))
    s.append(rule(GOLD, 1.0, 0, 16))
    s.append(P('MUTUAL NON-DISCLOSURE,<br/>CONFIDENTIALITY AND<br/>'
               'NON-CIRCUMVENTION AGREEMENT', 'cover_title'))
    s.append(Spacer(1, 12))
    s.append(rule(GOLD, 1.0, 0, 14))
    s.append(P('Prepared for a medical device sales organisation specialising in '
               'surgical robotics, robotic-assisted instrumentation and '
               'engineering innovation', 'cover_sub'))
    s.append(Spacer(1, 34))

    meta = [
        ['Disclosing / Receiving Party (Company)', COMPANY],
        ['Counterparty', '[COUNTERPARTY LEGAL NAME]'],
        ['Agreement Number', '[________________]'],
        ['Effective Date', '[____ / ____ / 20____]'],
        ['Structure', 'Mutual (bilateral) — see Schedule A, Election 1'],
        ['Confidentiality Term', '5 years from disclosure; trade secrets, '
                                 'perpetual'],
        ['Non-Circumvention Term', '24 months from the later of the Effective '
                                   'Date or last Introduction'],
        ['Governing Law', 'State of [Delaware], United States'],
        ['Document Classification', 'Confidential — Restricted Distribution'],
    ]
    rows = [[Paragraph(a, S['cell_b']), Paragraph(b, S['cell_l'])] for a, b in meta]
    t = Table(rows, colWidths=[CONTENT_W * 0.40, CONTENT_W * 0.60])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER),
        ('BACKGROUND', (0, 0), (0, -1), LIGHTER),
    ]))
    s.append(t)
    s.append(Spacer(1, 30))
    s.append(callout(
        'Important notice — read before execution',
        'This instrument is a drafting template prepared as a business document. '
        'It is not legal advice and creates no attorney-client relationship. '
        'Confidentiality, restrictive-covenant and healthcare-compliance rules '
        'vary materially by jurisdiction and change over time. Before this '
        'Agreement is issued to any counterparty, licensed counsel in each '
        'jurisdiction where it will be used must review and adapt the bracketed '
        'elections, the restrictive covenants in Section 5, and the '
        'healthcare-compliance provisions in Sections 5.5 and 7.4. Bracketed '
        'text marks a decision the parties must make.',
        accent=CRIMSON, bg=HexColor('#FBF1F0')))
    s.append(Spacer(1, 10))
    s.append(P('<font size="7.5" color="#5C6B7A">%s &nbsp;|&nbsp; Legal '
               'Department &nbsp;|&nbsp; Document %s &nbsp;|&nbsp; '
               'Uncontrolled when printed</font>' % (COMPANY, REVISION),
               'cover_meta'))
    s.append(NextPageTemplate('toc'))
    s.append(PageBreak())
    return s


def toc_page(toc):
    s = []
    s.append(P('<b>How to use this document.</b> Sections 1&ndash;7 are the '
               'operative Agreement — the only text that binds the Parties on '
               'execution. Schedules A and B and Exhibit 1 are completed at '
               'signature and incorporated by reference. The Explanatory Guide '
               'is internal commentary, not a term of the Agreement; detach it '
               'before issuing this document.', 'toc_note'))
    s.append(Spacer(1, 5))
    s.append(rule(BORDER, 0.5, 0, 5, width=(CONTENT_W - 20) / 2.0))
    s.append(toc)
    s.append(NextPageTemplate('body'))
    s.append(PageBreak())
    return s


def section_1():
    s = []
    s.append(H1('1', 'Introduction'))
    s.append(rule(NAVY, 1.0, 1, 6))
    s.append(P('This Mutual Non-Disclosure, Confidentiality and '
               'Non-Circumvention Agreement (this <b>"Agreement"</b>) is made '
               'as of the Effective Date stated on the signature page between '
               '%s, a [Delaware] corporation of [address] '
               '(<b>"Company"</b>), and the counterparty identified on the '
               'signature page (<b>"Counterparty"</b>). Each is a '
               '<b>"Party"</b>; together, the <b>"Parties."</b>'
               % COMPANY, 'body_first'))

    s.append(H2('1.1', 'Purpose and Commercial Context'))
    s.append(P('Company designs, integrates, markets and sells surgical '
               'robotic systems, robotic-assisted instrumentation, capital '
               'equipment, control and vision software, disposables and the '
               'engineering and field-service programmes supporting them. It '
               'competes on information that is not public: kinematic and '
               'control-loop design, haptic tuning, instrument articulation '
               'and sterile-barrier mechanisms, verification and validation '
               'evidence, regulatory strategy, manufacturing and supplier '
               'know-how, installed-base and procedure-volume data, and the '
               'commercial architecture — price books, discount matrices, '
               'group purchasing organisation ("GPO") and integrated delivery '
               'network ("IDN") terms — by which its products reach the '
               'operating room. Disclosure of that to a competitor, or use of '
               'Company introductions to reach Company customers, clinicians, '
               'distributors or suppliers directly, causes harm money cannot '
               'readily measure or repair.'))
    s.append(P('The Parties wish to exchange such information solely to '
               'evaluate and, if they choose, pursue the transaction described '
               'in Schedule A (the <b>"Permitted Purpose"</b>) — for example a '
               'distribution or sales-agency appointment, a supply or '
               'contract-manufacturing arrangement, a clinical evaluation, a '
               'co-development project, a financing, or a prospective '
               'employment or consulting engagement. This Agreement governs '
               'that exchange and nothing more.'))

    s.append(H2('1.2', 'Parties and Affiliates'))
    s.append(P('This Agreement is mutual by default: each Party is Disclosing '
               'Party as to what it provides and Receiving Party as to what it '
               'receives. If Schedule A, Election 1 designates it as one-way, '
               'only Counterparty owes the Receiving Party obligations. Each '
               'Party contracts for itself and its Affiliates; an Affiliate '
               'that receives Confidential Information is bound as a '
               'Representative and the Party remains responsible for it.'))

    s.append(H2('1.3', 'Recitals'))
    s.append(P('The Parties acknowledge that (a) Company has invested '
               'substantial time, capital and skill in its Confidential '
               'Information and takes reasonable measures to keep it secret; '
               '(b) that information derives independent economic value from '
               'not being generally known to, or readily ascertainable by '
               'proper means by, persons who could profit from its disclosure '
               'or use; (c) the restrictions here are no broader than needed '
               'to protect legitimate interests in trade secrets, customer and '
               'clinician relationships and goodwill; and (d) each Party has '
               'had the opportunity to take independent legal advice.'))

    s.append(H2('1.4', 'Structure and Order of Precedence'))
    s.append(P('Sections 1 to 7 are the operative terms. Schedules A and B and '
               'Exhibit 1 are incorporated by reference and form part of this '
               'Agreement. On conflict, the operative terms prevail over the '
               'Schedules unless a Schedule expressly states that it amends a '
               'numbered Section. A later definitive agreement for the Covered '
               'Transaction prevails as to information exchanged after its '
               'effective date; this Agreement continues to govern everything '
               'disclosed before it.'))

    s.append(H2('1.5', 'Interpretation'))
    s.append(P('"Including" and "such as" are illustrative and never limiting; '
               'the singular includes the plural; "writing" includes '
               'electronic records and email; "days" are calendar days unless '
               'stated as business days; headings do not affect meaning; and '
               'no rule construing ambiguity against the drafter applies, the '
               'Parties having negotiated at arm’s length. A reference to a '
               'statute includes its regulations, as amended.'))
    return s


def section_2():
    s = []
    s.append(H1('2', 'Definitions'))
    s.append(rule(NAVY, 1.0, 1, 6))
    s.append(H2('2.1', 'Defined Terms'))
    defs = [
        ['Term', 'Meaning'],
        ['Affiliate',
         'Any entity controlling, controlled by or under common control with a '
         'Party, where control means over 50% of voting interests or the power '
         'to direct management.'],
        ['Confidential Information',
         'All non-public information of any kind, in any medium, disclosed by '
         'or on behalf of the Disclosing Party, or observed, accessed or '
         'derived by the Receiving Party in connection with the Permitted '
         'Purpose, whether or not marked, plus all Derivative Materials. '
         'Section 2.2 lists the categories.'],
        ['Covered Transaction',
         'The transaction described as the Permitted Purpose in Schedule A, '
         'and any successor, substitute or materially similar transaction '
         'involving substantially the same subject matter or parties.'],
        ['Derivative Materials',
         'Notes, analyses, summaries, extracts, models, test results or '
         'benchmarks prepared by the Receiving Party that contain, reflect or '
         'are derived from Confidential Information.'],
        ['Field',
         'The design, development, manufacture, regulatory clearance, '
         'marketing, distribution, sale, installation, service or clinical '
         'support of robotic and robotic-assisted surgical systems and their '
         'instruments, accessories, disposables, software and related '
         'engineering services.'],
        ['Introduction',
         'Any act by which one Party puts the other in contact with, '
         'identifies to it, or facilitates its access to a Protected '
         'Relationship — by meeting, correspondence, site visit, congress, '
         'demonstration or referral.'],
        ['Personal Data / PHI',
         'Personal Data: information relating to an identified or identifiable '
         'natural person. PHI: protected health information as defined at 45 '
         'C.F.R. § 160.103. Both are Confidential Information of the highest '
         'sensitivity and are also governed by Section 3.11.'],
        ['Protected Relationship',
         'Each customer or prospective customer, IDN, GPO, hospital, '
         'ambulatory surgery centre, surgeon or other clinician, key opinion '
         'leader, distributor, sales agent, supplier, contract manufacturer, '
         'tooling or sterilisation vendor, clinical investigator or site, '
         'regulatory consultant, investor, lender, employee or contractor of '
         'the Disclosing Party that is named in Schedule B or becomes known to '
         'the Receiving Party through an Introduction or through Confidential '
         'Information.'],
        ['Representatives',
         'A Party’s Affiliates and their directors, officers, employees, '
         'contractors, secondees, professional advisers, auditors and (where '
         'Section 4.3 permits) subcontractors — only those with a genuine need '
         'to know for the Permitted Purpose.'],
        ['Trade Secret',
         'Confidential Information qualifying as a trade secret under the '
         'Defend Trade Secrets Act of 2016, 18 U.S.C. § 1836 et seq., the '
         'Uniform Trade Secrets Act as enacted in the Governing State, or '
         'comparable law.'],
    ]
    s.append(data_table(defs, [CONTENT_W * 0.21, CONTENT_W * 0.79]))
    s.append(Spacer(1, 3))

    s.append(H2('2.2', 'Categories of Confidential Information'))
    s.append(P('Illustrative, not exhaustive — so that neither Party can later '
               'claim it did not understand what this Agreement protects.',
               'body_first'))
    cats = [
        ['Category', 'Representative examples in this business'],
        ['Engineering and design',
         'CAD models and assembly drawings; tolerance stacks; kinematic '
         'models; control-loop gains and haptic tuning; end-effector and '
         'articulation mechanisms; sterile barrier design; materials and '
         'coatings; design history files; FMEA and risk files; verification, '
         'EMC, biocompatibility and sterilisation data.'],
        ['Software, data and security',
         'Source code, firmware and build systems; instrument-tracking and '
         'computer-vision training data and model weights; calibration and '
         'registration routines; cybersecurity architecture, threat models, '
         'penetration-test findings and the software bill of materials.'],
        ['Clinical and regulatory',
         '510(k), De Novo and PMA strategy and submissions; FDA and notified '
         'body correspondence; EU MDR technical documentation; clinical '
         'protocols and unpublished study data; complaint, vigilance and '
         'adverse-event analyses; CAPA records; audit findings.'],
        ['Manufacturing and supply chain',
         'Supplier and contract-manufacturer identities and terms; tooling '
         'drawings; process parameters and yields; sterilisation and cleaning '
         'validations; bills of material and cost of goods; capacity, lead '
         'times and single-source dependencies.'],
        ['Commercial and sales',
         'Price books, floor pricing, discount and bundling matrices; GPO and '
         'IDN terms and rebate structures; tender and RFP responses; territory '
         'and quota plans; CRM pipeline and win/loss analyses; installed-base '
         'and procedure-volume data; surgeon and KOL lists; service and '
         'warranty economics.'],
        ['Corporate and financial',
         'Forecasts and models; unpublished financials; capitalisation and '
         'financing terms; board materials; partnership, licensing and '
         'acquisition pipelines; litigation strategy.'],
        ['Third-party and regulated data',
         'PHI and patient-identifiable data; Personal Data of clinicians and '
         'employees; information held under a duty of confidence owed to a '
         'third party; export-controlled technical data.'],
    ]
    s.append(data_table(cats, [CONTENT_W * 0.21, CONTENT_W * 0.79]))
    s.append(Spacer(1, 3))

    s.append(H2('2.3', 'Exclusions'))
    s.append(P('Confidential Information does not include information the '
               'Receiving Party can demonstrate:', 'body_first'))
    s.extend(lettered([
        'was lawfully in its possession, free of any duty of confidence, '
        'before disclosure;',
        'is or becomes public other than through an act or omission of the '
        'Receiving Party or its Representatives;',
        'is lawfully received from a third party free to disclose it; or',
        'was independently developed by personnel with no access to and no use '
        'of the Confidential Information.',
    ]))
    s.append(P('The Receiving Party bears the burden of establishing an '
               'exclusion by contemporaneous written or electronic records, '
               'produced within thirty (30) days of written request. A '
               'combination of features or data points is not excluded merely '
               'because the individual elements are; the combination must '
               'itself satisfy an exclusion.'))
    s.append(callout(
        'Example — why the combination rule matters',
        'That a named IDN buys robotic systems is public. That it buys them at '
        'a stated capital price, with a stated per-procedure disposable '
        'commitment, on a contract expiring in a stated quarter, negotiated '
        'through a named GPO tier, is not — even though a determined '
        'researcher could learn each fact separately. The compiled commercial '
        'picture is the protected asset, and Section 2.3 preserves it.'))
    return s


def section_3():
    s = []
    s.append(H1('3', 'Confidentiality'))
    s.append(rule(NAVY, 1.0, 1, 6))

    s.append(H2('3.1', 'Undertaking and Standard of Care'))
    s.append(P('The Receiving Party shall hold all Confidential Information in '
               'strict confidence and protect it with at least the degree of '
               'care it applies to its own most sensitive information of like '
               'kind, and never less than reasonable care. It shall not '
               'disclose Confidential Information except as Section 4 permits, '
               'and shall not use it other than for the Permitted Purpose.',
               'body_first'))

    s.append(H2('3.2', 'Purpose Limitation'))
    s.append(P('The Receiving Party shall not use Confidential Information, '
               'directly or indirectly, to design, develop, price, market, '
               'sell, service or seek regulatory clearance for any product or '
               'service in the Field; to inform a competing bid, tender or GPO '
               'response; to establish a competing supply chain; to trade in '
               'securities; to train, fine-tune or evaluate any '
               'machine-learning model other than the Disclosing Party’s; or '
               'to obtain any commercial advantage over the Disclosing '
               'Party.'))

    s.append(H2('3.3', 'Marking and Unmarked Disclosures'))
    s.append(P('The Disclosing Party will use reasonable efforts to mark '
               'tangible materials. Failure to mark waives nothing: '
               'information disclosed orally, visually or by demonstration — a '
               'cleanroom tour, a cadaver-lab session, a sales training call, '
               'an engineering screen-share — is Confidential Information if a '
               'reasonable person in the Receiving Party’s position would '
               'understand it to be confidential from its nature or the '
               'circumstances. Either Party may, but need not, confirm such a '
               'disclosure in writing within thirty (30) days.'))

    s.append(H2('3.4', 'Safeguards'))
    s.append(P('The Receiving Party shall maintain administrative, technical '
               'and physical safeguards appropriate to the sensitivity of the '
               'information, including at a minimum:', 'body_first'))
    s.extend(bullets([
        'encryption in transit and at rest on all devices and services, and '
        'multi-factor authentication on every account able to reach it;',
        'access limited to named Representatives on a documented need-to-know '
        'basis, logged, and revoked on role change or departure;',
        'storage only in systems the Receiving Party controls or has '
        'contracted for under written confidentiality terms — never personal '
        'accounts, unmanaged devices or consumer file-sharing;',
        'no entry of Confidential Information into any public or third-party '
        'generative artificial-intelligence service or model-training '
        'pipeline, unless the Disclosing Party consents in writing and the '
        'service contractually excludes the data from training and human '
        'review;',
        'segregation of source code, algorithms and design files in a '
        'controlled environment, clean-room separated from any competing '
        'development; and',
        'physical control of samples, loaned instruments, consoles and demo '
        'units, which remain the Disclosing Party’s property.',
    ]))

    s.append(H2('3.5', 'Duration of Obligations'))
    s.append(P('Obligations run for the periods below, measured from each '
               'disclosure, and survive termination.', 'body_first'))
    dur = [
        ['Class of information', 'Protection period', 'Rationale'],
        ['General Confidential Information', 'Five (5) years from disclosure',
         'Outlasts a product generation and a GPO cycle, yet stays a '
         'reasonable restraint.'],
        ['Trade Secrets', 'While it remains a trade secret',
         'A fixed expiry would extinguish trade-secret status by contract.'],
        ['Source code, algorithms, control and imaging models',
         'Ten (10) years, or while a Trade Secret, whichever is longer',
         'Core platform assets persist across product generations.'],
        ['Pricing architecture, GPO/IDN and tender terms',
         'Five (5) years, and until the relevant contract expires',
         'Pricing leakage is the most immediate competitive harm in device '
         'sales.'],
        ['PHI, Personal Data, third-party confidential data',
         'Perpetual, and as law requires',
         'Duties under HIPAA, state privacy law and the GDPR do not lapse '
         'with a contract term.'],
    ]
    s.append(data_table(dur, [CONTENT_W * 0.30, CONTENT_W * 0.27,
                              CONTENT_W * 0.43]))
    s.append(Spacer(1, 2))

    s.append(figure(
        'Figure 1 — Lifecycle of Confidential Information under this Agreement',
        flow_diagram([
            ['DISCLOSE', 'Marked or reasonably', 'apparent (§3.3)'],
            ['RESTRICT', 'Need-to-know only,', 'bound in writing (§4.3)'],
            ['USE', 'Permitted Purpose', 'and nothing else (§3.2)'],
            ['SECURE', 'Encryption, MFA,', 'logging, no AI (§3.4)'],
            ['RETURN', 'Certify destruction', 'on demand (§3.7)'],
        ]),
        'Each step is an independent obligation. A failure at any step is a '
        'breach, whether or not information ultimately reached a third party.'))

    s.append(H2('3.6', 'Compelled Disclosure'))
    s.append(P('If required to disclose by subpoena, court or arbitral '
               'order, regulatory demand or law, the Receiving Party shall, so '
               'far as legally permitted, give prompt written notice before '
               'disclosing so the Disclosing Party may seek a protective '
               'order; cooperate at the Disclosing Party’s expense; disclose '
               'only the portion legally compelled, on advice of counsel; and '
               'seek confidential treatment. Such a disclosure is not a breach '
               'and the information remains Confidential Information for all '
               'other purposes.'))

    s.append(H2('3.7', 'Return and Destruction'))
    s.append(P('On written request, or promptly on expiry, termination or '
               'abandonment of the Covered Transaction, the Receiving Party '
               'shall return or irretrievably destroy all Confidential '
               'Information and Derivative Materials held by it or its '
               'Representatives and deliver the certificate at Exhibit 1, '
               'signed by an authorised officer, within thirty (30) days. It '
               'may retain (a) one archival copy held by its legal function to '
               'evidence its obligations, (b) copies in routine backup systems '
               'that cannot reasonably be purged selectively, and (c) copies '
               'required by law, regulation, professional standard or '
               'litigation hold. Retained copies may not be accessed for any '
               'operational purpose and remain subject to this Agreement while '
               'retained, notwithstanding Section 3.5.'))

    s.append(H2('3.8', 'No Licence, No Warranty, No Obligation'))
    s.append(P('All Confidential Information and the intellectual property '
               'rights in it remain the Disclosing Party’s exclusive property. '
               'Nothing here grants, by implication, estoppel or otherwise, '
               'any licence under any patent, copyright, trade secret, '
               'trademark, design right or other intellectual property. '
               'Confidential Information is provided "AS IS"; the Disclosing '
               'Party makes no representation as to its accuracy and, absent '
               'fraud, has no liability for the Receiving Party’s reliance on '
               'it. Neither Party must disclose anything, continue '
               'discussions, or enter into any definitive agreement.'))

    s.append(H2('3.9', 'Feedback'))
    s.append(P('The Disclosing Party may use without restriction, attribution '
               'or compensation any suggestions, corrections or usability '
               'observations the Receiving Party gives on its products, '
               'prototypes or documentation. This transfers no pre-existing '
               'intellectual property of the Receiving Party and does not '
               'enlarge its right to use Confidential Information.'))

    s.append(H2('3.10', 'No Residual-Knowledge Rights'))
    s.append(P('This Agreement contains no residual-knowledge licence. Unaided '
               'memory is not a permission to use, disclose or reproduce '
               'Confidential Information, and reliance on memory is not a '
               'defence to a claim under this Agreement.'))

    s.append(H2('3.11', 'Regulated and Third-Party Data'))
    s.append(P('Neither Party will disclose PHI or Personal Data to the other '
               'unless lawful and necessary for the Permitted Purpose and the '
               'Parties have first executed any required HIPAA business '
               'associate agreement or data processing agreement, which '
               'controls over this Agreement to the extent of any conflict. '
               'Data will be de-identified or limited to the minimum necessary '
               'wherever the Permitted Purpose allows. Neither Party will '
               'export or transfer export-controlled technical data in '
               'violation of the Export Administration Regulations, ITAR or '
               'applicable sanctions, or disclose information held subject to '
               'a third party’s confidentiality rights without consent.'))
    return s


def section_4():
    s = []
    s.append(H1('4', 'Non-Disclosure'))
    s.append(rule(NAVY, 1.0, 1, 6))
    s.append(P('Section 3 governs how Confidential Information is handled. '
               'This Section governs to whom it may be given, and what the '
               'Receiving Party may not do with it.', 'body_first'))

    s.append(H2('4.1', 'Prohibited Disclosures'))
    s.append(P('Except as Sections 4.3 and 4.7 permit, the Receiving Party '
               'shall not disclose, publish or make available any '
               'Confidential Information to any person, and specifically '
               'shall not:', 'body_first'))
    s.extend(lettered([
        'disclose it to any competitor of the Disclosing Party in the Field, '
        'including any Restricted Recipient listed in Schedule B and its '
        'Affiliates, agents and advisers;',
        'present, publish or discuss it in any abstract, poster, journal '
        'article, congress presentation, podcast, webinar, investor deck, '
        'analyst call, press release, social-media post or marketing material;',
        'include it in, or use it to support, any patent, design, utility '
        'model or trademark application, or any regulatory submission of the '
        'Receiving Party;',
        'disclose it to any prospective investor, lender, acquirer or '
        'placement agent, or place it in any data room, without prior written '
        'consent; or',
        'use the Disclosing Party’s name, marks or product images, or the '
        'existence, status or terms of the discussions, in any public or '
        'promotional statement, except as Section 7.4 requires by law.',
    ]))

    s.append(H2('4.2', 'No Reverse Engineering or Teardown'))
    s.append(P('The Receiving Party shall not, and shall not permit any '
               'person to, reverse engineer, decompile, disassemble, tear '
               'down, x-ray, CT-scan, section, or chemically or '
               'metallurgically analyse any system, instrument, disposable, '
               'prototype, sample or software of the Disclosing Party — '
               'whether obtained under this Agreement or otherwise — or '
               'otherwise attempt to derive its composition, source code, '
               'algorithms, architecture, tolerances or manufacturing methods, '
               'except to the narrow extent such an act cannot lawfully be '
               'prohibited and then only on written notice. Competitive '
               'benchmarking against the Receiving Party’s own products is '
               'prohibited for the term of this Agreement.'))

    s.append(H2('4.3', 'Permitted Disclosures to Representatives'))
    s.append(P('The Receiving Party may disclose Confidential Information '
               'only to Representatives with a genuine need to know it for the '
               'Permitted Purpose who are bound by written confidentiality and '
               'non-use obligations at least as protective as this Agreement '
               'or, for professional advisers, by equivalent professional '
               'duties. Disclosure to a subcontractor requires prior written '
               'consent. The Receiving Party shall keep a current list of '
               'Representatives given access, produce it on request, and is '
               'fully responsible for any act or omission of a Representative '
               'that would breach this Agreement if done by the Receiving '
               'Party.'))

    s.append(H2('4.4', 'Personnel Controls'))
    s.append(P('The Receiving Party shall instruct each Representative before '
               'granting access; revoke access promptly on role change or '
               'departure; recover or confirm destruction of Confidential '
               'Information held by a departing Representative; and notify the '
               'Disclosing Party if a Representative with material access '
               'moves to a competitor in the Field within twelve (12) months '
               'of last access.'))

    s.append(H2('4.5', 'Incident Notification'))
    s.append(P('The Receiving Party shall notify the Disclosing Party in '
               'writing within forty-eight (48) hours of becoming aware of any '
               'actual or reasonably suspected loss, theft or unauthorised '
               'access, use or disclosure, describing the information '
               'affected, the circumstances, the persons involved and the '
               'containment steps taken. It shall investigate, cooperate with '
               'the Disclosing Party’s investigation, take all steps '
               'reasonably requested to retrieve the information and mitigate '
               'harm, and preserve evidence. Where PHI or Personal Data is '
               'involved the Parties shall coordinate on statutory breach '
               'notification, and neither shall name the other without prior '
               'consultation unless law requires it.'))

    s.append(H2('4.6', 'Verification'))
    s.append(P('Once in any twelve (12) month period, on ten (10) business '
               'days’ notice, the Disclosing Party may require written '
               'certification of compliance with Sections 3 and 4 and a '
               'description of the safeguards in place. On a reasonable, '
               'documented suspicion of breach it may also require an audit of '
               'the relevant systems by an independent auditor bound to '
               'confidentiality, during business hours and with minimal '
               'disruption. The Disclosing Party bears the cost unless a '
               'material breach is found.'))

    s.append(H2('4.7', 'Protected Disclosures — Carve-Outs'))
    s.append(P('Nothing in this Agreement limits, and no provision may be '
               'construed to limit, any of the following:', 'body_first'))
    s.extend(lettered([
        '<b>Defend Trade Secrets Act immunity notice (18 U.S.C. § 1833(b)).</b> '
        'An individual shall not be held criminally or civilly liable under '
        'any federal or state trade secret law for the disclosure of a trade '
        'secret that (i) is made in confidence to a federal, state or local '
        'government official, directly or indirectly, or to an attorney, '
        'solely for the purpose of reporting or investigating a suspected '
        'violation of law, or (ii) is made in a complaint or other document '
        'filed under seal in a lawsuit or other proceeding. An individual '
        'suing an employer for retaliation for reporting a suspected violation '
        'of law may disclose the trade secret to that individual’s attorney '
        'and use it in the court proceeding, if the individual files any '
        'document containing the trade secret under seal and does not disclose '
        'it except pursuant to court order;',
        'communicating with, filing a charge with, providing information to, '
        'or participating in an investigation by the FDA, EEOC, NLRB, SEC, '
        'Department of Justice, a state attorney general, a notified body or '
        'any other regulator — including reporting a suspected device-safety '
        'issue or violation of law — without notice to or approval from the '
        'other Party, and including receiving any whistleblower award;',
        'the exercise of rights under Section 7 of the National Labor '
        'Relations Act or comparable law, including discussing wages, hours '
        'and working conditions; or',
        'disclosure required by a court, arbitrator or law, subject to the '
        'notice procedure in Section 3.6.',
    ]))
    s.append(callout(
        'Why the § 1833(b) notice is here',
        'Under 18 U.S.C. § 1833(b)(3), an employer that omits this immunity '
        'notice from a contract governing the use of trade secrets with an '
        'employee — a term that reaches contractors and consultants — cannot '
        'recover exemplary damages or attorney fees under the DTSA against '
        'that individual. Deleting subsection (a) therefore forfeits two of '
        'the strongest federal remedies in Section 6.',
        accent=GOLD, bg=HexColor('#FBF6EC')))
    return s


def section_5():
    s = []
    s.append(H1('5', 'Non-Circumvention'))
    s.append(rule(NAVY, 1.0, 1, 6))

    s.append(H2('5.1', 'Purpose'))
    s.append(P('In medical device sales the relationship is often worth more '
               'than the document. Access to a hospital value-analysis '
               'committee, a GPO contracting officer, a high-volume robotic '
               'surgeon or a validated contract manufacturer is an asset built '
               'over years. This Section stops a Party using the access it '
               'gains here to go around the other Party rather than through '
               'it.', 'body_first'))

    s.append(H2('5.2', 'Undertaking'))
    s.append(P('During the Restricted Period neither Party shall, directly or '
               'indirectly, alone or through any Affiliate, Representative or '
               'other person:', 'body_first'))
    s.extend(lettered([
        'contact, solicit, negotiate or transact with, or accept business '
        'from, any Protected Relationship of the other Party, in the Field, '
        'for the Covered Transaction or any substantially similar opportunity, '
        'otherwise than through the other Party;',
        'induce or attempt to induce any Protected Relationship to terminate, '
        'reduce, decline to renew or alter to the other Party’s detriment its '
        'relationship with the other Party;',
        'use Confidential Information or any Introduction to identify, '
        'qualify, price, target or approach any Protected Relationship, '
        'including by sourcing from the other Party’s suppliers or contract '
        'manufacturers on the basis of that Party’s specifications, tooling, '
        'qualifications or negotiated terms;',
        'circumvent the other Party’s role in the Covered Transaction, '
        'including by restructuring, renaming or re-routing the opportunity '
        'through an Affiliate, nominee, consortium, distributor or newly '
        'formed entity; or',
        'solicit for employment or engagement, or hire or engage, any employee '
        'or contractor of the other Party with whom it had material contact in '
        'connection with the Permitted Purpose.',
    ]))

    s.append(H2('5.3', 'Restricted Period'))
    s.append(P('The <b>"Restricted Period"</b> is twenty-four (24) months from '
               'the later of the Effective Date and the last Introduction or '
               'last disclosure of Confidential Information, unless Schedule '
               'A, Election 4 states otherwise. It is tolled and extended day '
               'for day for any period during which a Party is in breach of '
               'this Section, to the extent the Governing State permits '
               'tolling.'))

    s.append(H2('5.4', 'Carve-Outs'))
    s.append(P('This Section does not restrict, and no breach arises from:',
               'body_first'))
    s.extend(bullets([
        'a relationship documented before the Effective Date at Schedule B, '
        'Part 3, or otherwise proved by contemporaneous records to predate the '
        'Introduction;',
        'a contact developed wholly independently of any Introduction and '
        'without use of Confidential Information, evidenced by contemporaneous '
        'records;',
        'a response to a genuinely public tender, RFP or GPO solicitation open '
        'to all qualified bidders that the restricted Party did not procure, '
        'prompt or influence;',
        'general advertising, job postings and untargeted agency searches, and '
        'the hiring of a person who responds to them or who was terminated by '
        'the other Party; or',
        'the ordinary continuation of a commercial relationship wholly outside '
        'the Field.',
    ]))

    s.append(H2('5.5', 'Healthcare Compliance Overlay'))
    s.append(P('This Section restrains the Parties only. Nothing in it '
               'requires, permits or rewards any referral, purchase, order or '
               'recommendation of an item or service reimbursable by a federal '
               'or state healthcare programme; restrains the independent '
               'clinical judgement of any physician; or interferes with '
               'patient access to care or an institution’s choice of '
               'technology. No payment under this Agreement is intended as an '
               'inducement within the federal Anti-Kickback Statute, 42 U.S.C. '
               '§ 1320a-7b(b), or the Physician Self-Referral Law, 42 U.S.C. '
               '§ 1395nn, and the Parties shall comply with those laws, with '
               'applicable transparency-reporting obligations, and with the '
               'Foreign Corrupt Practices Act and UK Bribery Act. Any '
               'application of this Section that would conflict with those '
               'laws is void, and the remainder stands.'))

    s.append(H2('5.6', 'Reasonableness and Reformation'))
    s.append(P('Each Party acknowledges these restraints are reasonable in '
               'scope, geography and duration, are necessary to protect '
               'legitimate interests in trade secrets, customer and clinician '
               'goodwill and specialised training, and will not prevent it '
               'from earning a livelihood. If a court or arbitrator finds any '
               'restraint overbroad, the Parties request that it be reformed '
               'and enforced to the maximum extent permitted rather than '
               'struck out; where reformation is not permitted, the restraint '
               'is severed and the remainder stands.'))

    s.append(H2('5.7', 'Jurisdictional Limits'))
    s.append(P('The employee non-solicitation and hiring restraint in Section '
               '5.2(e) does not apply, and is unenforceable, to the extent the '
               'law governing an individual’s engagement prohibits or limits '
               'it — including California Business and Professions Code '
               '§ 16600 et seq. and comparable statutes elsewhere. '
               'Restrictive-covenant law in this area is unsettled and moves '
               'quickly at both federal and state level; counsel must confirm '
               'the current position for each jurisdiction before this '
               'Agreement is used there. The remaining subsections of Section '
               '5.2, which protect trade secrets and transaction-specific '
               'confidentiality rather than restraining employment, are '
               'intended to be enforceable independently of Section 5.2(e).'))

    s.append(H2('5.8', 'Circumvention Fee'))
    s.append(P('If a Party circumvents the other in breach of this Section '
               'and derives revenue from a Protected Relationship as a result, '
               'the injured Party may elect, in place of proving actual '
               'damages and without limiting Section 6, to recover a fee equal '
               'to [____] per cent ([__]%) of gross revenue derived from that '
               'relationship during the Restricted Period and the [twelve '
               '(12)] months following — a reasonable approximation of the '
               'value of a diverted opportunity, which is difficult to '
               'quantify precisely.'))

    s.append(H2('5.9', 'Worked Examples'))
    s.append(P('Interpretive aids agreed by the Parties. Not exhaustive; they '
               'do not narrow Section 5.2.', 'body_first'))
    ex = [
        ['Scenario', 'Treatment', 'Reason'],
        ['Company introduces Counterparty, a distributor, to a regional IDN’s '
         'value-analysis committee. Two months later Counterparty quotes that '
         'IDN directly for a competing platform.',
         '<font color="#7B2D26"><b>Prohibited</b></font>',
         'Opportunity reached through an Introduction, in the Field. '
         '§5.2(a), (c).'],
        ['Counterparty learns from Company’s bill of materials which contract '
         'manufacturer builds Company’s articulating wrist, and approaches it '
         'to build a similar one.',
         '<font color="#7B2D26"><b>Prohibited</b></font>',
         'Supplier identified through Confidential Information. §5.2(c).'],
        ['Counterparty forms a new entity, assigns the opportunity to it, and '
         'that entity contracts with the introduced GPO.',
         '<font color="#7B2D26"><b>Prohibited</b></font>',
         '"Directly or indirectly" reaches nominees and new entities. '
         '§5.2(d).'],
        ['Counterparty had a signed distribution agreement with the same IDN '
         'for orthopaedic implants two years before the Effective Date, listed '
         'at Schedule B, Part 3, and continues it.',
         '<font color="#2F5D46"><b>Permitted</b></font>',
         'Documented pre-existing relationship, and outside the Field. §5.4.'],
        ['A hospital system publishes an open RFP for robotic systems on its '
         'portal; Counterparty, previously introduced to that system, bids on '
         'its own account.',
         '<font color="#2F5D46"><b>Permitted</b></font>',
         'Genuinely public solicitation, not procured or prompted. §5.4.'],
    ]
    s.append(data_table(ex, [CONTENT_W * 0.45, CONTENT_W * 0.15,
                             CONTENT_W * 0.40], align_first_left=False))
    return s


def section_6():
    s = []
    s.append(H1('6', 'Breach and Remedies'))
    s.append(rule(NAVY, 1.0, 1, 6))

    s.append(H2('6.1', 'Irreparable Harm'))
    s.append(P('Each Party acknowledges that Confidential Information and '
               'Protected Relationships are unique and that a breach or '
               'threatened breach of Sections 3, 4 or 5 causes immediate and '
               'irreparable harm for which damages are an inadequate remedy: '
               'once a control algorithm, a price book or a GPO term is known '
               'to a competitor it cannot be made unknown, and the loss of a '
               'clinician or IDN relationship compounds over years of '
               'procedure volume that cannot be reconstructed.',
               'body_first'))

    s.append(H2('6.2', 'Injunctive Relief and Specific Performance'))
    s.append(P('The injured Party may seek temporary, preliminary and '
               'permanent injunctive relief and specific performance in any '
               'court of competent jurisdiction, without proving actual '
               'damages and, to the fullest extent permitted by law, without '
               'posting a bond. Each Party waives any defence that an adequate '
               'remedy at law exists. This right is immediate and is not '
               'subject to the escalation procedure in Section 6.7 or to any '
               'agreement to arbitrate.'))

    s.append(H2('6.3', 'Monetary Relief'))
    s.append(P('The injured Party may also recover, as applicable and without '
               'double recovery for the same loss:', 'body_first'))
    s.extend(bullets([
        'actual damages, including lost profits and the cost of '
        'investigation, containment, remediation, notification and customer '
        'retention;',
        'the breaching Party’s unjust enrichment, including revenue diverted '
        'from a Protected Relationship;',
        'in the alternative, a reasonable royalty for unauthorised use of a '
        'Trade Secret;',
        'the circumvention fee under Section 5.8, at the injured Party’s '
        'election in place of proving actual damages for that breach;',
        'exemplary damages of up to twice the award, and reasonable attorney '
        'fees, for wilful and malicious misappropriation under 18 U.S.C. '
        '§ 1836(b)(3), subject to the notice at Section 4.7(a); and',
        'seizure and other relief under applicable trade-secret, '
        'computer-fraud and unfair-competition law.',
    ]))

    s.append(H2('6.4', 'Constructive Trust and Assignment'))
    s.append(P('Any intellectual property, application, registration or '
               'improvement conceived or reduced to practice using '
               'Confidential Information in breach of this Agreement is held '
               'in constructive trust for the Disclosing Party, and the '
               'breaching Party shall assign it and execute all documents '
               'needed to perfect that assignment, at its own cost.'))

    s.append(H2('6.5', 'Indemnity and Costs'))
    s.append(P('The breaching Party shall indemnify, defend and hold harmless '
               'the injured Party, its Affiliates and their personnel against '
               'all third-party claims, regulatory penalties, fines and '
               'losses, and all reasonable legal and expert costs arising out '
               'of the breach — including statutory privacy or '
               'security-incident liability from unauthorised disclosure of '
               'PHI or Personal Data. The prevailing Party in any enforcement '
               'action may recover its reasonable attorney fees and costs, '
               'including on appeal.'))

    s.append(H2('6.6', 'Cumulative Remedies; No Waiver; No Cap'))
    s.append(P('All rights and remedies are cumulative and additional to every '
               'other remedy at law or in equity. No failure or delay in '
               'exercising a right waives it, and no partial exercise '
               'precludes further exercise. Any limitation of liability or '
               'exclusion of consequential damages in any other agreement '
               'between the Parties does not apply to a breach of Sections 3, '
               '4 or 5 unless that agreement expressly says so by reference to '
               'this Section.'))

    s.append(H2('6.7', 'Escalation'))
    s.append(P('For a curable, non-disclosure-related breach — a lapse in '
               'safeguards, a missing Representative undertaking, a late '
               'certificate — the injured Party shall give written notice and '
               'the breaching Party has ten (10) business days to cure; '
               'failing cure, the Parties’ executives shall confer within a '
               'further fifteen (15) days. This is a precondition to a damages '
               'claim for such a breach only. No notice or waiting period '
               'applies to actual or threatened unauthorised disclosure, '
               'misappropriation of a Trade Secret, breach of Section 5, or '
               'any application under Section 6.2.'))

    s.append(figure(
        'Figure 2 — Escalation of remedies',
        ladder_diagram([
            ('Notice and cure',
             'Curable safeguard or administrative lapse — 10 business days to '
             'cure (§6.7). Not available for disclosure or circumvention.'),
            ('Executive escalation',
             'Named executives confer within 15 days; disclosures and the '
             'Covered Transaction suspended pending resolution.'),
            ('Emergency injunctive relief',
             'TRO, preliminary injunction and specific performance — '
             'immediate, no notice, no bond, no arbitration (§6.2).'),
            ('Full monetary and statutory relief',
             'Actual loss, unjust enrichment, reasonable royalty, '
             'circumvention fee, DTSA exemplary damages and fees '
             '(§§5.8, 6.3, 6.5).'),
        ]),
        'The ladder is not sequential for serious breaches: disclosure to a '
        'competitor or circumvention of a Protected Relationship starts at '
        'level 3.'))
    return s


def section_7():
    s = []
    s.append(H1('7', 'Governing Law'))
    s.append(rule(NAVY, 1.0, 1, 6))

    s.append(H2('7.1', 'Governing Law'))
    s.append(P('This Agreement and all claims arising out of or relating to it '
               'or to the Confidential Information, whether in contract, tort, '
               'statute or otherwise, are governed by the laws of the State of '
               '[Delaware] (the <b>"Governing State"</b>), without regard to '
               'conflict-of-laws rules. The UN Convention on Contracts for the '
               'International Sale of Goods does not apply. Where a mandatory '
               'law of another jurisdiction applies to a Party’s personnel or '
               'to Personal Data, that law prevails to the extent of the '
               'conflict and only to that extent.', 'body_first'))

    s.append(H2('7.2', 'Jurisdiction, Venue and Jury Waiver'))
    s.append(P('The Parties submit to the exclusive jurisdiction of the '
               'courts in [New Castle County, Delaware] and waive any '
               'objection to venue or claim of forum non conveniens, except '
               'that either Party may seek injunctive relief under Section 6.2 '
               'in any court with jurisdiction over the other Party or its '
               'assets. <b>To the fullest extent permitted by '
               'law, each Party knowingly and voluntarily waives any right to '
               'trial by jury in any proceeding arising out of this '
               'Agreement.</b> [Pre-dispute jury waivers are unenforceable in '
               'some states, including California — confirm before relying on '
               'this.]'))

    s.append(H2('7.3', 'Optional Arbitration [Elect in Schedule A]'))
    s.append(P('If Schedule A, Election 5 selects arbitration, any dispute '
               'not resolved under Section 6.7 shall be finally resolved by '
               'binding arbitration administered by [the American Arbitration '
               'Association under its Commercial Arbitration Rules] before '
               '[one] arbitrator [experienced in medical device disputes], '
               'seated in [Wilmington, Delaware], in English. The arbitration, '
               'the record and the award are confidential; judgment may be '
               'entered in any court of competent jurisdiction. Nothing here '
               'prevents either Party from seeking injunctive relief from a '
               'court under Section 6.2, and doing so does not waive the '
               'agreement to arbitrate.'))

    s.append(H2('7.4', 'Compliance with Law'))
    s.append(P('Each Party shall comply with all laws applicable to its '
               'performance, including the Anti-Kickback Statute and Physician '
               'Self-Referral Law, transparency-reporting requirements, the '
               'Food, Drug, and Cosmetic Act and FDA regulations, EU '
               'Regulation 2017/745 (MDR) where applicable, HIPAA and '
               'applicable privacy law, the Foreign Corrupt Practices Act and '
               'UK Bribery Act, and export-control and sanctions law. A Party '
               'may disclose the existence of this Agreement where securities '
               'law requires, on such notice as is practicable.'))

    s.append(H2('7.5', 'Severability, Amendment and Waiver'))
    s.append(P('Any provision held invalid or unenforceable shall be reformed '
               'to the minimum extent needed to make it enforceable and, '
               'failing that, severed, with the remainder continuing in full '
               'force. No amendment or waiver is effective unless in writing '
               'signed by an authorised representative of each Party.'))

    s.append(H2('7.6', 'Assignment and Successors'))
    s.append(P('Neither Party may assign this Agreement or delegate its '
               'obligations without the other’s prior written consent, except '
               'to a successor to all or substantially all of its business or '
               'assets in the Field that assumes this Agreement in writing — '
               'and consent may be withheld where the assignee is a '
               'competitor. Any purported assignment is otherwise void. '
               'Affiliates are intended third-party beneficiaries of Sections '
               '3 to 6; there are no others.'))

    s.append(H2('7.7', 'Notices'))
    s.append(P('Notices must be in writing and delivered to the addresses in '
               'Schedule A by personal delivery, nationally recognised courier '
               'or email with confirmation of receipt to the designated legal '
               'contact, and are effective on delivery or the next business '
               'day if delivered outside business hours. Notice of a breach or '
               'security incident must also be copied to the recipient’s legal '
               'contact.'))

    s.append(H2('7.8', 'Term, Termination and Survival'))
    s.append(P('This Agreement begins on the Effective Date and continues for '
               '[two (2)] years unless terminated earlier by either Party on '
               'thirty (30) days’ written notice. Termination ends only the '
               'obligation to make further disclosures: Sections 2 to 7 and '
               'every obligation as to Confidential Information already '
               'disclosed survive for the periods in Section 3.5, and the '
               'Restricted Period in Section 5.3 runs regardless of '
               'termination.'))

    s.append(H2('7.9', 'Entire Agreement and Counterparts'))
    s.append(P('This Agreement with its Schedules and Exhibit is the entire '
               'agreement on its subject matter and supersedes all prior '
               'understandings, oral or written. Each Party confirms it has '
               'not relied on any statement outside it, save that nothing '
               'excludes liability for fraud. It may be executed in '
               'counterparts and signed electronically; electronic signatures '
               'have the same effect as manuscript signatures under the ESIGN '
               'Act and UETA as enacted in the Governing State.'))

    s.append(H2('7.10', 'No Partnership or Exclusivity'))
    s.append(P('Nothing here creates a partnership, joint venture, agency, '
               'franchise, distributorship or employment relationship, grants '
               'authority to bind the other Party, or obliges either Party to '
               'deal exclusively with the other, to proceed with the Covered '
               'Transaction, or to refrain from any independent opportunity '
               'that uses no Confidential Information and does not breach '
               'Section 5.'))

    s.append(KeepTogether([
        Spacer(1, 7),
        H1_plain('Execution'),
        rule(NAVY, 1.0, 1, 6),
        P('<b>IN WITNESS WHEREOF</b>, the Parties have executed this Agreement '
          'by their duly authorised representatives as of the Effective Date. '
          'Each signatory represents that it is authorised to bind the Party '
          'for which it signs, and each Party confirms that it has read '
          'Sections 1 to 7 and the completed Schedules in full.',
          'body_first'),
        Spacer(1, 8),
        signature_pair('COMPANY', COMPANY,
                       'COUNTERPARTY', '[COUNTERPARTY LEGAL NAME]'),
    ]))

    s.append(Spacer(1, 16))
    s.append(Paragraph('Attachments completed at execution', S['h2']))
    s.append(P('Both Parties confirm the status of each attachment below. An '
               'attachment marked "not completed" is not thereby waived — the '
               'operative Section continues to apply on its own terms, and the '
               'Party relying on a carve-out bears the evidential burden set '
               'out there.', 'body_first'))
    att = [
        ['Attachment', 'Governs', 'Status at signing'],
        ['Schedule A.1 — Permitted Purpose',
         'Scope of every permitted use (§3.2)',
         '[ ] completed &nbsp;&nbsp; [ ] not completed'],
        ['Schedule A.2 — Elections',
         'Term, Restricted Period, forum, fee (§§3.5, 5.3, 5.8, 7.1)',
         '[ ] completed &nbsp;&nbsp; [ ] defaults apply'],
        ['Schedule A.3 — Notices and contacts',
         'Valid service of notice and incident reporting (§§4.5, 7.7)',
         '[ ] completed &nbsp;&nbsp; [ ] not completed'],
        ['Schedule B.1/B.2 — Protected Relationships and Restricted '
         'Recipients',
         'Named scope of §§4.1(a) and 5.2',
         '[ ] attached &nbsp;&nbsp; [ ] none named'],
        ['Schedule B.3 — Pre-existing relationships',
         'Carve-out from non-circumvention (§5.4)',
         '[ ] attached &nbsp;&nbsp; [ ] none claimed'],
        ['Exhibit 1 — Certificate of Return and Destruction',
         'Delivered on request or at close-out (§3.7)',
         '[ ] not due at signing'],
        ['HIPAA business associate agreement / data processing agreement',
         'Required before any PHI or Personal Data moves (§3.11)',
         '[ ] executed &nbsp;&nbsp; [ ] not applicable'],
    ]
    s.append(data_table(att, [CONTENT_W * 0.34, CONTENT_W * 0.38,
                              CONTENT_W * 0.28]))
    s.append(Spacer(1, 8))
    s.append(fill_lines(
        ['<font size="7.5">Executed original retained by:<br/><br/>'
         '________________________</font>',
         '<font size="7.5">Counterpart copies distributed to:<br/><br/>'
         '________________________</font>',
         '<font size="7.5">Date filed:<br/><br/>'
         '________________________</font>'],
        [CONTENT_W * 0.36, CONTENT_W * 0.38, CONTENT_W * 0.26]))
    return s


def schedules():
    s = []
    s.append(PageBreak())
    s.append(H1_plain('Schedule A — Permitted Purpose and Elections'))
    s.append(rule(NAVY, 1.0, 1, 7))
    s.append(P('Complete every field before execution. An election left blank '
               'takes the default shown in the operative Sections.',
               'body_first'))

    s.append(H2('A.1', 'Permitted Purpose'))
    s.append(fill_lines(
        ['<b>Describe the specific transaction or relationship being '
         'evaluated</b> (for example: "evaluation of Counterparty as an '
         'authorised distributor of Company’s robotic surgical platform in '
         '[territory]"):<br/><br/><br/><br/><br/><br/>'],
        [CONTENT_W]))
    s.append(Spacer(1, 8))

    s.append(H2('A.2', 'Elections'))
    el = [
        ['#', 'Election', 'Selection'],
        ['1', 'Structure of the Agreement',
         '[ ] Mutual (default)&nbsp;&nbsp;&nbsp;[ ] One-way — Counterparty is '
         'Receiving Party only'],
        ['2', 'General confidentiality term (§3.5)',
         '[ ] 5 years (default)&nbsp;&nbsp;&nbsp;[ ] ____ years'],
        ['3', 'Trade-secret protection (§3.5)',
         '[ ] Indefinite while a trade secret (default — do not vary without '
         'counsel)'],
        ['4', 'Restricted Period (§5.3)',
         '[ ] 24 months (default)&nbsp;&nbsp;&nbsp;[ ] 12 months'
         '&nbsp;&nbsp;&nbsp;[ ] ____ months'],
        ['5', 'Dispute resolution (§§7.2, 7.3)',
         '[ ] Courts of the Governing State (default)&nbsp;&nbsp;&nbsp;'
         '[ ] Binding arbitration under §7.3'],
        ['6', 'Governing State (§7.1)', 'State of ______________________'],
        ['7', 'Circumvention fee percentage (§5.8)', '________ %'],
        ['8', 'Term of the Agreement (§7.8)', '________ years from the '
                                              'Effective Date'],
    ]
    s.append(data_table(el, [CONTENT_W * 0.05, CONTENT_W * 0.35,
                             CONTENT_W * 0.60]))
    s.append(Spacer(1, 8))

    s.append(H2('A.3', 'Notices and Designated Contacts'))
    n = [
        ['', 'Company', 'Counterparty'],
        ['Legal notices to', '____________________', '____________________'],
        ['Address', '____________________', '____________________'],
        ['Email', '____________________', '____________________'],
        ['Security-incident contact (§4.5)', '____________________',
         '____________________'],
        ['Authorised Representatives with access (§4.3) — attach list',
         '[ ] attached', '[ ] attached'],
    ]
    s.append(data_table(n, [CONTENT_W * 0.34, CONTENT_W * 0.33,
                            CONTENT_W * 0.33]))

    s.append(PageBreak())
    s.append(H1_plain('Schedule B — Protected Relationships'))
    s.append(rule(NAVY, 1.0, 1, 7))
    s.append(P('This Schedule identifies relationships by name. It is '
               'illustrative of, and does not limit, the definition of '
               '"Protected Relationship" in Section 2.1, which also reaches '
               'relationships learned through an Introduction or through '
               'Confidential Information.', 'body_first'))

    s.append(H2('B.1', 'Part 1 — Protected Relationships of Company'))
    p1 = [
        ['Category', 'Named party', 'Introduced on', 'Notes'],
        ['IDN / hospital / ASC', '', '', ''],
        ['GPO', '', '', ''],
        ['Surgeon / KOL / clinical site', '', '', ''],
        ['Distributor / sales agent', '', '', ''],
        ['Supplier / contract manufacturer', '', '', ''],
        ['Investor / lender', '', '', ''],
    ]
    s.append(data_table(p1, [CONTENT_W * 0.28, CONTENT_W * 0.28,
                             CONTENT_W * 0.16, CONTENT_W * 0.28]))
    s.append(Spacer(1, 8))

    s.append(H2('B.2', 'Part 2 — Restricted Recipients (§4.1(a))'))
    s.append(P('Confidential Information may not be disclosed to the following '
               'entities or their Affiliates, agents or advisers under any '
               'circumstances:', 'body_first'))
    s.append(fill_lines(['1. ______________________________&nbsp;&nbsp;&nbsp;'
                         '2. ______________________________<br/><br/>'
                         '3. ______________________________&nbsp;&nbsp;&nbsp;'
                         '4. ______________________________'], [CONTENT_W]))
    s.append(Spacer(1, 8))

    s.append(H2('B.3', 'Part 3 — Pre-Existing Relationships (§5.4)'))
    s.append(P('Relationships each Party had established before the Effective '
               'Date and which are therefore carved out of Section 5.2. A '
               'relationship not listed here must be proved by '
               'contemporaneous records.', 'body_first'))
    p3 = [
        ['Party claiming', 'Counterpart named', 'Relationship since',
         'Evidence held'],
        ['[ ] Company [ ] Counterparty', '', '', ''],
        ['[ ] Company [ ] Counterparty', '', '', ''],
        ['[ ] Company [ ] Counterparty', '', '', ''],
    ]
    s.append(data_table(p3, [CONTENT_W * 0.28, CONTENT_W * 0.28,
                             CONTENT_W * 0.20, CONTENT_W * 0.24]))

    s.append(PageBreak())
    s.append(H1_plain('Exhibit 1 — Certificate of Return and Destruction'))
    s.append(rule(NAVY, 1.0, 1, 7))
    s.append(P('To be signed by an authorised officer and delivered within '
               'thirty (30) days of a request under Section 3.7.',
               'body_first'))
    s.append(Spacer(1, 6))
    s.append(P('The undersigned, on behalf of ______________________________ '
               '(the "Receiving Party"), certifies with respect to the Mutual '
               'Non-Disclosure, Confidentiality and Non-Circumvention '
               'Agreement dated ____________ (Agreement No. __________) that:'))
    s.extend(lettered([
        'all Confidential Information and Derivative Materials in tangible '
        'form have been returned to the Disclosing Party or destroyed beyond '
        'recovery;',
        'all electronic copies have been permanently deleted from all systems, '
        'devices, cloud services, collaboration tools and personal '
        'repositories under the Receiving Party’s or its Representatives’ '
        'control, and no copy has been entered into any model-training or '
        'generative artificial-intelligence service;',
        'all Representatives who received Confidential Information have been '
        'instructed accordingly and have confirmed compliance;',
        'all loaned equipment, instruments, samples and demonstration units '
        'have been returned in the condition received, ordinary wear excepted; '
        'and',
        'the only retained copies are those permitted by Section 3.7, '
        'described below, which remain subject to the Agreement:',
    ]))
    s.append(fill_lines(['Description of retained copies, the system holding '
                         'them and the reason for retention:<br/><br/><br/>'],
                        [CONTENT_W]))
    s.append(Spacer(1, 12))
    s.append(signature_pair('CERTIFYING OFFICER', '____________________',
                            'COUNTERSIGNED (if required)',
                            '____________________'))
    return s


def explanatory_guide():
    s = []
    s.append(PageBreak())
    s.append(H1_plain('Explanatory Guide (Internal Commentary)'))
    s.append(rule(GOLD, 1.0, 1, 7))
    s.append(callout(
        'Status of this guide',
        'This guide explains the drafting choices in the Agreement so that '
        'commercial, engineering and sales teams can apply it consistently. '
        'It is internal commentary, not a term of the Agreement, and it is '
        'not legal advice. Remove it before issuing the Agreement to a '
        'counterparty.', accent=GOLD, bg=HexColor('#FBF6EC')))

    s.append(H2('G.1', 'What each section does'))
    g = [
        ['Section', 'What it does', 'Why it is drafted this way'],
        ['1 Introduction',
         'Identifies the Parties, states the Permitted Purpose and records '
         'the recitals.',
         'The recitals in §1.3 are evidence. Courts assessing a restrictive '
         'covenant look for a stated legitimate interest and an '
         'acknowledgement that reasonable secrecy measures exist; §1.3 '
         'supplies both on the face of the document.'],
        ['2 Definitions',
         'Fixes the vocabulary, lists the categories of protected information '
         'and states the four standard exclusions.',
         'The category table in §2.2 is deliberately specific to robotics and '
         'device sales: generic NDAs fail when a recipient argues it did not '
         'understand that a discount matrix or a supplier identity was '
         'covered. The combination rule in §2.3 protects compiled commercial '
         'data whose individual elements are public.'],
        ['3 Confidentiality',
         'Sets the standard of care, purpose limitation, safeguards, '
         'protection periods and the return-and-destroy process.',
         'The tiered periods in §3.5 avoid the common error of putting a fixed '
         'expiry on trade secrets, which can extinguish their status. The AI '
         'restriction in §3.4 closes a route by which specifications now '
         'routinely leak.'],
        ['4 Non-Disclosure',
         'Controls who may receive the information and bans reverse '
         'engineering, IP filings and publication.',
         'A confidentiality clause without §4.3 is unenforceable in practice: '
         'flow-down obligations to Representatives make the recipient '
         'answerable for its own staff and advisers. §4.7 preserves statutory '
         'rights a contract cannot waive, and the DTSA notice preserves '
         'exemplary damages and fee recovery.'],
        ['5 Non-Circumvention',
         'Stops a Party using access gained under the Agreement to reach the '
         'other Party’s customers, clinicians, distributors or suppliers '
         'directly.',
         'The provision most often litigated and most often struck down for '
         'overbreadth. It is bounded by a defined Field, a defined set of '
         'Protected Relationships, a fixed Restricted Period and real '
         'carve-outs, and carries a reformation clause and the '
         'healthcare-compliance overlay in §5.5.'],
        ['6 Breach and Remedies',
         'Establishes irreparable harm, injunctive relief, monetary and '
         'statutory relief, indemnity and an escalation path.',
         'The irreparable-harm acknowledgement in §6.1 is what gets an '
         'injunction heard quickly. §6.6 prevents a liability cap in a later '
         'supply or distribution agreement from silently capping exposure for '
         'a trade-secret breach — a frequent and expensive oversight.'],
        ['7 Governing Law',
         'Chooses the law and forum and carries the boilerplate.',
         'The forum clause carves out injunctive relief so emergency '
         'applications can be brought where the assets or the defendant are, '
         'not only in the chosen forum.'],
    ]
    s.append(data_table(g, [CONTENT_W * 0.17, CONTENT_W * 0.35,
                            CONTENT_W * 0.48]))
    s.append(Spacer(1, 6))

    s.append(H2('G.2', 'Before this Agreement is used — counsel checklist'))
    s.extend(bullets([
        '<b>Confirm the restrictive-covenant position.</b> Enforceability of '
        'the employee non-solicit in §5.2(e), and of non-circumvention '
        'generally, varies by state and country and has been unsettled at '
        'federal level; confirm the current rule in every jurisdiction where '
        'the Agreement will be signed or enforced, and adjust §5.7.',
        '<b>Confirm the jury waiver and choice of law.</b> Pre-dispute jury '
        'waivers are unenforceable in some states, and a Delaware choice of '
        'law will not displace mandatory employment or privacy law where a '
        'Representative works.',
        '<b>Decide arbitration deliberately.</b> Arbitration buys '
        'confidentiality of the proceeding — valuable in a trade-secret '
        'dispute — at the cost of speed on emergency relief. §7.3 keeps the '
        'court route open for injunctions either way.',
        '<b>Execute the privacy agreements first.</b> If PHI or Personal Data '
        'will move, a business associate agreement or data processing '
        'agreement must be in place before the first disclosure; §3.11 '
        'assumes it, and this Agreement is not a substitute for it.',
        '<b>Complete Schedule B honestly and early.</b> The carve-out in §5.4 '
        'for pre-existing relationships is the counterparty’s main defence '
        'and the Company’s main evidentiary protection. Filling it in at '
        'signature avoids the argument later.',
        '<b>Fix the circumvention fee percentage.</b> Leaving §5.8 blank '
        'discards the alternative to proving diverted profit, which is often '
        'the hardest element of a circumvention claim.',
        '<b>Match the term to the deal.</b> A five-year tail suits a '
        'distribution evaluation; a co-development discussion touching control '
        'algorithms should use the ten-year tier in §3.5.',
    ]))

    s.append(H2('G.3', 'Operational practice for the deal team'))
    s.extend(bullets([
        'Mark documents before they leave the building, and confirm sensitive '
        'oral and demonstration disclosures in writing — §3.3 protects '
        'unmarked disclosures, but the written confirmation is what makes the '
        'claim easy to prove.',
        'Keep the Representative access list current from day one — it is the '
        'first document requested in any dispute.',
        'Log every Introduction with a date: the Restricted Period in §5.3 '
        'runs from the last one, and an undated Introduction is hard to '
        'enforce.',
        'Never paste specifications, price books or GPO terms into a public '
        'AI assistant, and route any AI tooling request through the '
        'consent process in §3.4.',
        'Trigger §4.5 within 48 hours of a suspected incident, not after the '
        'internal investigation concludes.',
        'Send the Exhibit 1 certificate routinely when a discussion ends, '
        'whether or not the counterparty asks.',
    ]))
    s.append(Spacer(1, 5))
    s.append(rule(BORDER, 0.5, 0, 4))
    s.append(P('<font size="7.5" color="#5C6B7A">End of document. Prepared for '
               '%s. Not legal advice — obtain review by licensed counsel in '
               'each applicable jurisdiction before execution.</font>'
               % COMPANY, 'body'))
    return s


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def main():
    out = sys.argv[1] if len(sys.argv) > 1 else (
        'Medical_Robotics_Mutual_NDA.pdf')
    doc = NDADoc(out)
    toc = build_toc()

    story = []
    story += cover_page()
    story += toc_page(toc)
    story += section_1()
    story += section_2()
    story += section_3()
    story += section_4()
    story += section_5()
    story += section_6()
    story += section_7()
    story += schedules()
    story += explanatory_guide()

    doc.multiBuild(story, canvasmaker=NDACanvas)
    print('Wrote %s' % out)


if __name__ == '__main__':
    main()
