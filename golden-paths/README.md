# Golden Paths

Golden paths define expected Product Factory OS runtime behavior by product category.

They are intentionally machine-readable so validators and future runtime commands can compare generated projects against expected route, starter, artifacts, and gates.

Golden paths complement `tests/snapshots/route-snapshots.json`:

- route snapshots prove natural-language skill routing;
- golden paths prove product-type starter selection, required artifacts, and minimum gates.

Golden paths also anchor harness templates: the selected topology should have guides and sensors that cover maintainability, architecture fitness, and behaviour before a generated project is treated as repeatable.
