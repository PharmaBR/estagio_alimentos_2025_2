#!/usr/bin/env python3
"""
Utility to inspect DOCX merge fields (Word MERGEFIELD) in a .docx template.
Usage: python inspect_docx_mergefields.py <docx_file>
"""
import sys
try:
    from mailmerge import MailMerge
except ImportError:
    print("Missing dependency 'docx-mailmerge'. Install with: pip install docx-mailmerge")
    sys.exit(1)

def inspect_merge_fields(path: str) -> set[str]:
    """Opens the DOCX and returns a set of merge field names."""
    with MailMerge(path) as doc:
        fields = doc.get_merge_fields()  # set of field names
    return fields

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python inspect_docx_mergefields.py <docx_file>")
        sys.exit(1)
    path = sys.argv[1]
    try:
        fields = inspect_merge_fields(path)
        if fields:
            print("Merge fields found:")
            for f in sorted(fields):
                print(f"  - {f}")
        else:
            print("No merge fields found in the document.")
    except Exception as e:
        print(f"Error inspecting merge fields: {e}")
        sys.exit(1)