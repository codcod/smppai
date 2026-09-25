# Releasing

Releases are automated by `python-semantic-release`, configured in `pyproject.toml`'s
`[tool.semantic_release]` and run by `.github/workflows/release.yml` on every push to `main`:

1. `semantic-release version` inspects Conventional Commit messages since the last tag.
2. It bumps `version` in `pyproject.toml`, re-locks `uv.lock` to match (`build_command`),
   regenerates `CHANGELOG.md`, and creates a `vX.Y.Z` git tag — with no further human approval.

There is no manual release step and no PyPI publish (see `PACKAGING.md`) — pushing to `main` is
the release trigger itself. Because of that, `porth-umbrella`'s publish-gated commit policy
(project `CLAUDE.md`) requires human approval **before** a push to this repo's `main`, since
there is no checkpoint after it lands — see `development/smppai/review-addendum.md` step 9.
