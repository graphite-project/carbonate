## How to contribute:

- Fork the repo
- Run script/bootstrap to setup your dev environment
- Create a feature branch
- Add some tests and code
- Run script/test to verify your changes
- Submit a Pull Request

Tests for any changes are greatly appreciated. The CI job also lints the code and is pretty strict. Please respect the lint warnings, or make a note in the issue if you think a rule should be disabled.

## How to release:

1. Create a `release-x.y.z` branch off of master.
1. Review the merge commits with `git log --merges ${last_tag}..HEAD` and update `CHANGELOG.md`.
1. Bump the carbonate version in `carbonate/__init__.py`.
1. Push the branch to GitHub and create a PR for discussion.
1. Merge the PR.
1. Run `script/release`.
