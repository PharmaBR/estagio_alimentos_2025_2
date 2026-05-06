#!/usr/bin/env python3
"""
Utility to inspect PDF form fields (widget annotations) and their positions.
Usage: python inspect_pdf_fields.py <pdf_file>
"""
import sys
import fitz  # PyMuPDF
import json

def inspect_pdf(path: str) -> list[dict]:
    """Opens a PDF and returns a list of form fields with metadata."""
    doc = fitz.open(path)
    fields = []
    for page_index, page in enumerate(doc):
        widgets = page.widgets()
        if not widgets:
            continue
        for w in widgets:
            fields.append({
                "page": page_index + 1,
                "field_name": w.field_name,
                "field_type": w.field_type,
                "value": w.field_value,
                "rect": [
                    w.rect.x0, w.rect.y0,
                    w.rect.x1, w.rect.y1
                ]
            })
    return fields

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspect_pdf_fields.py <pdf_file>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    try:
        result = inspect_pdf(pdf_path)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("No form fields (widget annotations) found in the PDF.")
    except Exception as e:
        print(f"Error inspecting PDF: {e}")
        sys.exit(1)