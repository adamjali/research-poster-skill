# Rendering + self-QA

## Rendering a .pptx to an image (cross-platform)

    bash ${CLAUDE_SKILL_DIR}/scripts/render.sh "<poster.pptx>" "<out.pdf>" "<out.png>" 1.7

`render.sh` picks a renderer automatically:

1. **LibreOffice headless** (default, works on Linux / Windows / macOS): `soffice --headless
   --convert-to pdf`. This is the portable path; most environments have LibreOffice or can install it.
2. **Microsoft PowerPoint on macOS** (fallback): drives PowerPoint via AppleScript to export a PDF.
   It wraps the AppleScript in `with timeout of 280 seconds` (PowerPoint's default AppleEvent timeout
   is ~120 s and chart-heavy or large posters exceed it, giving error -1712), polls until PowerPoint
   is actually ready to be scripted (a fixed delay races the launch and gives -609 "Connection is
   invalid"), and retries up to 3 times. The first export on a machine also triggers a one-time macOS
   prompt to allow the terminal to control PowerPoint. Approve it, or the export fails silently. If
   you set `PYTHON=...`, that interpreter is used for the pypdfium2 rasterize step (handy when
   pypdfium2 lives in a conda env rather than system `python3`).

Then it rasterizes the PDF to PNG with **pypdfium2** (self-contained, no poppler needed). Render the
abstract PDF directly with pypdfium2 as well.

Note: LibreOffice and PowerPoint render charts slightly differently (fonts, spacing). If you tuned a
poster against one renderer, spot-check it in the other before final delivery if the audience will
open it in PowerPoint.

## Repair detection (native charts, macOS + PowerPoint only)

After building native charts on macOS, you can confirm none were stripped on open:

    bash ${CLAUDE_SKILL_DIR}/scripts/detect_repair.sh "<poster.pptx>"

It reports how many chart objects survived and whether a repair alert fired. If a chart went missing,
a doughnut/pie data-label position was set somewhere (see build-and-charts.md); remove it. Even
without this macOS-only check, following the safe-styling rule (never set a doughnut/pie data-label
position) prevents the repair on every platform.

## Self-QA loop (do this to a high bar before showing the user)

Render, look at the PNG, and check every item, then fix and re-render. Iterate until clean:

- No text overflow: nothing spills into the next section's header or the footer band.
- No clipping: chart data labels and axis labels are fully visible (give bars xlim headroom; keep
  doughnut labels off the slice edges).
- Type is big enough: title/headers/stats dominate; body and fine print (references, footer,
  affiliations, chart captions) are still comfortably readable, not tiny.
- Padding is breathable: even gaps, generous margins, nothing cramped; nothing floating in a void.
- Contrast is strong everywhere (label color vs its background).
- Columns align (tops and bottoms), the layout reads as one system.
- Numbers are correct and match the source (the build already asserts this; eyeball it too).
- Native charts survived (detector, macOS) and there is no repair prompt.
- The house-style palette, fonts, and logo match the reference when one was provided.

A picture is worth a thousand tokens: always view the render, do not judge from the code.
