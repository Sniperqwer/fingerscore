"""Step 2: Technical verification script.
Tests verovio PDF generation and music21 fingering read/write.
"""
import os
import sys
import tempfile

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample_score.musicxml")


def test_verovio_svg():
    """Test verovio renders MusicXML to SVG."""
    import verovio
    tk = verovio.toolkit()
    tk.loadFile(SAMPLE_PATH)
    svg = tk.renderToSVG(1)
    assert len(svg) > 100, "SVG output too short"
    assert "<svg" in svg, "Not valid SVG"
    print(f"[OK] verovio SVG rendering: {len(svg)} chars")
    return svg


def test_verovio_pdf_methods():
    """Check if verovio has direct PDF output."""
    import verovio
    tk = verovio.toolkit()
    methods = [m for m in dir(tk) if "pdf" in m.lower()]
    print(f"[INFO] verovio PDF methods: {methods or 'none'}")
    render_methods = [m for m in dir(tk) if "render" in m.lower()]
    print(f"[INFO] verovio render methods: {render_methods}")


def test_cairosvg_pdf(svg):
    """Test SVG -> PDF conversion via cairosvg."""
    import cairosvg
    pdf_bytes = cairosvg.svg2pdf(bytestring=svg.encode("utf-8"))
    pdf_path = os.path.join(tempfile.gettempdir(), "test_fingerscore.pdf")
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    size = os.path.getsize(pdf_path)
    assert size > 100, "PDF too small"
    print(f"[OK] cairosvg SVG->PDF: {size} bytes -> {pdf_path}")


def test_music21_parse():
    """Test music21 parses the sample MusicXML."""
    import music21
    score = music21.converter.parse(SAMPLE_PATH)
    print(f"[OK] music21 parse: title={score.metadata.title}, parts={len(score.parts)}")
    notes = list(score.parts[0].recurse().notes)
    print(f"[OK] Found {len(notes)} notes: {[n.nameWithOctave for n in notes]}")
    return score


def test_music21_fingering_write(score):
    """Test adding fingering via music21 and exporting."""
    from music21 import articulations, converter
    notes = list(score.parts[0].recurse().notes)
    notes[0].articulations.append(articulations.Fingering(1))
    notes[1].articulations.append(articulations.Fingering(2))
    notes[2].articulations.append(articulations.Fingering(3))

    xml_data = converter.toData(score, "musicxml")
    xml_str = xml_data if isinstance(xml_data, str) else xml_data.decode("utf-8")
    assert "<fingering" in xml_str, "Fingering not found in music21 export"
    print("[OK] music21 fingering write: <fingering> found in exported MusicXML")

    # Save for round-trip test
    tmp_path = os.path.join(tempfile.gettempdir(), "test_m21_fingering.musicxml")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(xml_str)
    return tmp_path


def test_lxml_fingering_write():
    """Test adding fingering via lxml directly."""
    from lxml import etree
    tree = etree.parse(SAMPLE_PATH)
    root = tree.getroot()
    notes_xml = root.findall(".//note")
    print(f"[INFO] lxml found {len(notes_xml)} <note> elements")

    # Add fingering to first note
    note_el = notes_xml[0]
    notations = etree.SubElement(note_el, "notations")
    technical = etree.SubElement(notations, "technical")
    fingering = etree.SubElement(technical, "fingering")
    fingering.text = "1"

    result = etree.tostring(tree, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()
    assert "<fingering>1</fingering>" in result, "lxml fingering not found"
    print("[OK] lxml fingering write: <fingering>1</fingering> present")

    tmp_path = os.path.join(tempfile.gettempdir(), "test_lxml_fingering.musicxml")
    with open(tmp_path, "wb") as f:
        f.write(etree.tostring(tree, xml_declaration=True, encoding="UTF-8"))
    return tmp_path


def test_fingering_roundtrip(musicxml_path, source=""):
    """Test that music21 can read back fingering from a modified MusicXML."""
    from music21 import converter, articulations
    score = converter.parse(musicxml_path)
    found = []
    for note in score.parts[0].recurse().notes:
        fingerings = [a for a in note.articulations if isinstance(a, articulations.Fingering)]
        if fingerings:
            found.append((note.nameWithOctave, fingerings[0].fingerNumber))
    if found:
        print(f"[OK] Roundtrip ({source}): read back fingerings: {found}")
    else:
        print(f"[WARN] Roundtrip ({source}): no fingerings read back")


def test_verovio_renders_fingering(musicxml_path):
    """Test that verovio renders fingering numbers in the SVG."""
    import verovio
    tk = verovio.toolkit()
    tk.loadFile(musicxml_path)
    svg = tk.renderToSVG(1)
    # Check if fingering numbers appear in SVG
    has_fingering = any(f">{i}<" in svg for i in ["1", "2", "3"])
    if has_fingering:
        print("[OK] verovio SVG includes fingering numbers")
    else:
        print("[WARN] verovio SVG may not show fingering numbers (check visually)")
    return svg


if __name__ == "__main__":
    print("=" * 60)
    print("Step 2: Technical Verification")
    print("=" * 60)

    print("\n--- 1. Verovio SVG Rendering ---")
    svg = test_verovio_svg()

    print("\n--- 2. Verovio PDF Methods ---")
    test_verovio_pdf_methods()

    print("\n--- 3. CairoSVG PDF Generation ---")
    test_cairosvg_pdf(svg)

    print("\n--- 4. music21 Parse ---")
    score = test_music21_parse()

    print("\n--- 5. music21 Fingering Write ---")
    m21_path = test_music21_fingering_write(score)

    print("\n--- 6. lxml Fingering Write ---")
    lxml_path = test_lxml_fingering_write()

    print("\n--- 7. Fingering Roundtrip (music21 -> music21) ---")
    test_fingering_roundtrip(m21_path, source="music21")

    print("\n--- 8. Fingering Roundtrip (lxml -> music21) ---")
    test_fingering_roundtrip(lxml_path, source="lxml")

    print("\n--- 9. Verovio Renders Fingering ---")
    svg_with_finger = test_verovio_renders_fingering(m21_path)

    print("\n" + "=" * 60)
    print("Verification complete!")
    print("=" * 60)
