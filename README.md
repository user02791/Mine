# Mine

## Next Card Up

A training plan built around a rotating three-card deck — Push, Pull, Legs + Arms — so that
missing a day never breaks a schedule. Short sessions using dumbbells, an EZ bar and machines;
progressive overload by double progression; training and eating through a GLP-1 deficit without
losing muscle; and a muscle-priority map aimed at a lean V-taper rather than upper-trap bulk.

| File | What it is |
|---|---|
| `next-card-up-manual.pdf` | The 23-page printable manual. Tabbed by section, one idea per page. |
| `next-card-up-manual.html` | Print source for the PDF. Fonts are embedded as data URIs; page numbers and cross-references are computed at render time. |
| `next-card-up.html` | Phone-first web version with a set logger and deck-position tracker. |

### Rebuilding the PDF

```
npm i -g playwright   # already present in this environment
node render.js next-card-up-manual.html next-card-up-manual.pdf
```

`render.js` reports any page whose content overflows its 8.5×11in box, which would otherwise be
silently clipped.
