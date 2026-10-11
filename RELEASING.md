# Releasing

Releases are automated by `python-semantic-release`, configured in `pyproject.toml`'s
`[tool.semantic_release]` and run by `.github/workflows/release.yml` on every push to `main`
that changes `src/`:

1. `semantic-release version` inspects Conventional Commit messages since the last tag.
2. It bumps `version` in `pyproject.toml`, re-locks `uv.lock` to match (`build_command`),
   regenerates `CHANGELOG.md`, creates a `vX.Y.Z` git tag and a GitHub release for it — with no
   further human approval.
3. `release.yml`'s `docs` job then runs `.github/workflows/docs-release.yml`, which builds the
   user manual with snowball and attaches it to that release. It is called directly because a
   release created with `GITHUB_TOKEN` fires no `release` event.

There is no manual release step and no PyPI publish (see `PACKAGING.md`) — pushing a `src/`
change to `main` is the release trigger itself. A push that touches only docs, tests or CI does
not run the release workflow; its commits land in the next release's changelog, and
`workflow_dispatch` runs a release by hand. Because of that, `porth-umbrella`'s publish-gated
commit policy (project `CLAUDE.md`) requires human approval **before** a push to this repo's
`main`, since there is no checkpoint after it lands — see `development/smppai/review-addendum.md` step 9.
