# Medical Robotics NDA

A mutual non-disclosure, confidentiality and non-circumvention agreement
tailored to a medical device sales organisation working in surgical robotics
and engineering innovation, generated as a print-ready PDF.

## Contents

| File | Description |
| --- | --- |
| `Medical_Robotics_Mutual_NDA.pdf` | The generated 14-page agreement |
| `scripts/generate_nda.py` | ReportLab generator — the single source of truth for the document |

## Document structure

| Pages | Part |
| --- | --- |
| 1 | Cover sheet, deal summary, execution notice |
| 2 | Two-column table of contents (also a PDF bookmark outline) |
| 3–9 | **Operative agreement**, Sections 1–7 |
| 10 | Execution page and attachment checklist |
| 11–13 | Schedule A, Schedule B, Exhibit 1 |
| 14 | Explanatory guide (internal commentary — detach before issuing) |

The seven operative sections are Introduction, Definitions, Confidentiality,
Non-Disclosure, Non-Circumvention, Breach and Remedies, and Governing Law.

## Regenerating the PDF

```bash
pip install reportlab
python3 scripts/generate_nda.py Medical_Robotics_Mutual_NDA.pdf
```

Edit the text in `scripts/generate_nda.py` and re-run — never edit the PDF
directly. The constants at the top of the script (`COMPANY`, `SHORT_NAME`,
`REVISION`, the colour palette and the page geometry) control branding and
layout. Bump `REVISION` whenever the operative text changes.

The build runs `multiBuild`, so the table of contents and the "Page X of Y"
footers resolve over two passes automatically.

## Before the agreement is used

The document is a drafting template, not legal advice. Bracketed text marks a
decision the parties must make, and Schedules A and B must be completed at
signature. Confidentiality, restrictive-covenant and healthcare-compliance
rules vary by jurisdiction and change over time, so licensed counsel in each
relevant jurisdiction should review and adapt it — in particular the
restrictive covenants in Section 5 and the healthcare-compliance provisions in
Sections 5.5 and 7.4 — before it is issued to any counterparty.
