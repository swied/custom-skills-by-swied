# Format and rich-content support

## Format matrix

| Extension | Intended use | Equations | Rendered diagrams |
| --- | --- | --- | --- |
| `.md`, `.markdown` | Self-contained rendered Markdown | Inline SVG by default; PNG or native TeX on request | Inline SVG by default; PNG on request |
| `.pdf` | Fixed-layout distribution and printing | Native Typst typesetting | SVG |
| `.docx` | Editable Microsoft Word document | Native OMML equations | SVG; Pandoc can add a PNG fallback when `rsvg-convert` is available |
| `.odt` | Editable OpenDocument text | Native MathML | SVG |
| `.rtf` | Legacy interchange | Local PNG equation images | PNG |
| `.html`, `.htm` | Standalone web document | Embedded MathML | Embedded SVG |
| `.epub` | EPUB3 ebook | MathML | SVG |
| `.pptx` | PowerPoint slide deck | Native OMML equations | PNG for broad compatibility |
| `.tex` | Editable LaTeX source | Native LaTeX math | PNG in a sibling media directory |
| `.typ` | Editable Typst source | Native Typst math | SVG in a sibling media directory |

Prefer native equation objects over pictures. They remain searchable,
accessible, scalable, and—where the application supports it—editable. Use SVG
for generated visuals when the complete destination pipeline supports it; use
PNG when a legacy or presentation writer does not handle SVG reliably.

Rendered Markdown uses base64 data URIs inside HTML `img` elements because
standard Markdown has no portable syntax for embedding image bytes. This keeps
generated diagrams and equations in one file without leaving temporary or
sibling assets. Some hosted Markdown platforms sanitize data URIs; choose
standalone HTML instead when the destination platform does so. Existing image
links in the source remain links.

PPTX assumes slide-oriented Markdown: headings define slide boundaries and
normal presentation-layout constraints apply. An arbitrary long-form document
will convert, but it may not make a useful deck without source adaptation.

## Recognized rich blocks

- `mermaid`: Render with Mermaid CLI (`mmdc`).
- `dot` or `graphviz`: Render with Graphviz (`dot`).
- `math`, `latex-math`, or `tex-math`: Treat as a display equation rather than
  ordinary source code.

Mermaid and Graphviz are declarative renderers. Do not treat `python`, `r`,
`bash`, `javascript`, `jupyter`, or another general-purpose language as a
rendering directive; automatic execution would be unsafe and non-deterministic.

## Sensible future additions

Add these only with explicit demand and isolated dependency checks:

- PlantUML for UML-heavy repositories.
- D2 for architecture diagrams.
- Vega-Lite for declarative data visualizations.
- WaveDrom for digital timing diagrams.
- TikZ/Asymptote for specialized technical figures.
- LilyPond or ABC for music notation.

Each renderer should consume only its declarative fence, run locally without a
network service, produce SVG first and PNG second, preserve useful title/alt
metadata, and offer an opt-out flag. Keep executable notebook and plotting
workflows in a separate, explicitly trusted skill.

## Formats intentionally not first-class

Pandoc exposes many additional writers, including DocBook, JATS, AsciiDoc,
reStructuredText, man pages, and several HTML slide systems. They are useful
interchange or publishing targets, but each needs its own fidelity contract and
tests. Add one deliberately rather than accepting every Pandoc writer through
an unchecked extension.
