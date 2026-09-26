# Figure style and reporting conventions

These defaults apply to project-generated figures. They govern presentation,
not data selection or scientific interpretation.

- **Viridis is the default sequential scientific colormap.** For discrete
  ordered categories, sample distinguishable values from Viridis.
- Do not force Viridis onto genuinely diverging data. Use a scientifically
  appropriate diverging palette in that case and document the choice with the
  figure-generation code or caption.
- Avoid arbitrary decorative color choices. Use color to encode a documented
  variable or analytical distinction.
- Figures must be publication-quality and readable on both the web and a
  manuscript page. Prefer accessible contrast, legible type, and direct labels
  where practical.
- Axes must name the variable and give its units. Captions must state the
  analyzed population and important transformations or filtering.
- Never silently remove outliers, transform axes or data, smooth data, or
  change population definitions. State each such choice explicitly and report
  N where it is scientifically relevant.
- Prefer vector output (SVG or PDF) for line- or text-heavy figures when
  practical, and provide an optimized web representation when needed.
- Keep figure-generation code reproducible. The shared
  `subsurface_life_real_estate.plotting` helper sets the current Viridis default
  used by the existing analysis modules.

Existing figures retain their documented analytical population and processing
rules; updating a style default does not retroactively alter those results.
