# Fingerscore

A web-based tool for annotating piano fingerings on sheet music.

Upload a MusicXML score, mark your own fingerings on each note, and export a PDF with fingering annotations.

## Features

- Upload MusicXML files and render them as interactive sheet music
- Click on notes to annotate fingerings (1-5)
- Keyboard shortcuts for efficient continuous annotation
- Smart detection of repeated measures with batch fingering application
- Export annotated scores as PDF
- Mobile-friendly with measure zoom mode

## Tech Stack

- **Backend**: FastAPI + music21 + verovio (Python)
- **Frontend**: Vanilla HTML/CSS/JS + Verovio.js
- **Rendering**: Verovio (MusicXML → SVG)
- **Export**: Verovio + cairosvg (MusicXML → SVG → PDF)

## Quick Start

```bash
conda activate fingerscore
pip install -e .
uvicorn backend.main:app --reload
```

Then open http://localhost:8000 in your browser.

## License

MIT
