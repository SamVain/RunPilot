# Release Checklist

## v0.1.0 (Alpha)

### Pre-release
- [ ] Unit tests passing
- [ ] Manual test on 2 environments (ideally Windows + Linux or Docker + non-Docker)
- [ ] README updated
- [ ] LICENSE added (Apache 2.0)
- [ ] CHANGELOG updated
- [ ] Version set to 0.1.0 in code

### Tag and publish
- [ ] `git commit -am "Release v0.1.0"`
- [ ] `git tag v0.1.0`
- [ ] `git push origin v0.1.0`

### Post-release
- [ ] Create GitHub Release notes from CHANGELOG
- [ ] Open milestone for v0.2.0
- [ ] Create issues for next features
