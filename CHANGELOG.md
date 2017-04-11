## v1.0.0
 - Fix reading whisper_lock_writes from cluster config in carbon_sync (PR#77, @justincmoy)
 - Bumping version to 1.0.0 to match Graphite releases

## v0.2.3

 - support new versions of carbon (PR#74 @wdauchy)
 - lock whisper files during carbon-sync and whisper-fill (PR#48 @fillipog, PR#71 @deniszh)
 - Fixes and optimizations for carbonate (PR#68 @iksaif, PR#70 @deniszh)
 - Make the heal process resilient (PR#42 @jjneely, PR#69 @deniszh)
 - Add option to follow symlinks (PR#65 @tmak0)
 - Do not overwrite target WSP file if source is corrupt (PR#52 @jjneely)
 - 'carbon-stale' tool to help find metrics with blank/missing data (PR#30 @bitprophet)
 - remove shebang, not a cli script (PR#55 @piotr1212)
 - mention environment variables in README.md (PR#53 @fillipog)
 - Fixup badge link in readme (PR#66 @dozoisch)
 - Add dirty mode for sync (PR#39 @iksaif)
 - Read config-file and cluster options from environ (PR#49 @fillipog)

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
