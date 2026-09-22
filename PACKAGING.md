# Packaging

`smppai` is a `hatchling`-built, `src/`-layout package. The importable module name (`smpp`,
`src/smpp/`) differs from the distribution name (`smppai`, `pyproject.toml`'s `[project].name`) —
`from smpp import SMPPClient`, not `from smppai import ...` (see `README.md`'s quick-start; this
mismatch already caused one bug, tracked as `porth`'s POR-001).

Not currently published to PyPI — `release.yml`'s `publish-pypi` job exists but is commented
out, so a release today only creates a git tag and bumps the version; it doesn't reach PyPI.
