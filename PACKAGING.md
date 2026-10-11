# Packaging

`smppai` is a `hatchling`-built, `src/`-layout package. The importable module name (`smpp`,
`src/smpp/`) differs from the distribution name (`smppai`, `pyproject.toml`'s `[project].name`) —
`from smpp import SMPPClient`, not `from smppai import ...` (see `README.md`'s quick-start; this
mismatch already caused one bug, tracked as `porth`'s POR-001).

Not currently published to PyPI: `release.yml` has no publish step (its `id-token: write`
permission is unused). A release creates a git tag and a GitHub release, with the user
manual attached (see `RELEASING.md`), but nothing reaches PyPI.
