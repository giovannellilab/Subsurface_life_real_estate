# Living Research Report source

`index.html` and `styles.css` are the canonical, tracked source for the public
Living Research Report. Build a sanitized static export with:

```sh
.venv/bin/python scripts/build_living_report.py --output-dir /tmp/living-report
```

The builder copies only the three named derived figure PNGs from ignored local
processed outputs. Review `/tmp/living-report` before replacing the contents of
the `gh-pages` branch. It never copies raw inputs, caches, manifests, tables, or
other local research data.

## Information hierarchy

1. Google Doc and scientific discussions: working scientific notebook and
   brainstorming; no public link is created by this repository.
2. `docs/SCIENTIFIC_FRAMEWORK.md`: canonical, version-controlled scientific
   synthesis.
3. `site/`: tracked source for the public Living Research Report.
4. `gh-pages`: generated and deployed public output.

## Review and deployment

1. Commit the tracked framework, source, builder, and ignore-rule changes on
   `main`.
2. Re-run the build into a fresh review directory and inspect its six files.
3. In a separate `gh-pages` checkout, replace only `.nojekyll`, `index.html`,
   `styles.css`, and the three named files under `assets/` with the reviewed
   export. Do not copy `data/` or a directory wholesale.
4. Run `git diff --check`, inspect the `gh-pages` file list, then commit and
   push that branch only after review approval.

The page links to its report source and deployment branch instead of a
self-referential commit hash, which cannot exist until after the page is
committed.
