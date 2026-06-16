# Release Checklist

Use this when preparing a public GitHub release.

## Must pass

- [ ] `python3 -m pytest`
- [ ] `python3 -m bookskill_studio doctor`
- [ ] `python3 -m bookskill_studio demo --output demo-output`
- [ ] `python3 -m bookskill_studio validate demo-output`
- [ ] `python3 -m bookskill_studio install demo-output --skills-home /tmp/test-skills`
- [ ] `python3 -m bookskill_studio open-report demo-output`

## README and repo hygiene

- [ ] README first screen explains the outcome in one glance
- [ ] quickstart works from a clean clone
- [ ] `CHANGELOG.md` has a v0.1.0 entry
- [ ] repository description is short and specific
- [ ] repo topics are added on GitHub
- [ ] license is visible and correct
- [ ] `.gitignore` keeps generated demo output out of commits

## Publishing

- [ ] tag `v0.1.0`
- [ ] create GitHub release notes
- [ ] attach a screenshot or terminal demo in the release discussion
