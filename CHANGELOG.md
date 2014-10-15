## v0.2.2

- Load `/opt/graphite/lib` into python's path when executing any binstubs
- Bugfix in carbon-sieve where `--node` was not specified (@kamaradclimber)
- Bugfix in carbon-sieve where main cluster doesn't exist (@seanpquig)
- Add new carbon-path tool :sparkles: (@bitprophet)
- Bugfix in whisper-aggregate
- Make carbon-sieve filter correctly with long address formats (@tail)
- Add `-s` flag to carbon-lookup that displays IP/hostname only
- Support passing options to rsync during carbon-sync (@jphines)

## v0.2.1

- Improved CLI entry points
- Support for whisper 0.9.9
- Fix time.time() usage bug
- Error out if whisper-fill source/dest don't exist

## v0.2.0

- Initial release
