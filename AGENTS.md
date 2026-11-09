# AGENTS.md

## Pull requests and releases

Label every PR; `.github/release.yml` sorts the generated release notes by label.

| Label | Use for |
|---|---|
| `breaking` | Anything users must act on to upgrade (also use a `feat!:`/`fix!:` title) |
| `feature` | New behavior |
| `fix` | Bug fix |
| `docs` | Docs only |
| `tests` | Tests and CI only |
| `skip-changelog` | Keep out of the release notes |

A PR with none of these lands under "Other". Release notes need What's new, Bug fixes and Breaking changes (see CONTRIBUTING.md).
