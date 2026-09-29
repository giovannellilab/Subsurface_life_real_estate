"""Validate the tracked Living Research Report source and a fresh sanitized build."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from build_living_report import ROOT, build, validate_built_images, validate_source_html


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="Optional directory for the temporary/public build")
    args = parser.parse_args()
    source = (ROOT / "site/index.html").read_text(encoding="utf-8")
    validate_source_html(source)
    if args.output_dir:
        build(args.output_dir)
        built = (args.output_dir / "index.html").read_text(encoding="utf-8")
        validate_built_images(args.output_dir, built)
        destination = args.output_dir
    else:
        with tempfile.TemporaryDirectory(prefix="living-report-") as temp:
            destination = Path(temp)
            build(destination)
            built = (destination / "index.html").read_text(encoding="utf-8")
            validate_built_images(destination, built)
    print(f"Living Report validation passed: frozen A–H sections, M1–M6 roadmap, and every local image reference resolve ({destination}).")


if __name__ == "__main__":
    main()
