## master (unreleased)
 - Refactor log lines to use native interpolation (#129, @drawks)
 - Resolves issue #127 - python3 safe stdout handling (#128, @drawks)
 - Changed mutable default argument in test_fill.py and test_sync.py (#126, @aastha12)

## v1.1.8
 - support for Aggregated-Consistent Hash (#121 / #56, @deniszh / @klynch)
 - handle transient network failures and support custom staging dir path (#122, @ryangsteele)

## v1.1.7
 - fixes python3 TypeError (#113, @l4r-s)
 - Change write mode to non-binary. (#111, @hdost)
 -  Add python3 testing (#110, @hdost)
 - add codecov (#112, @piotr1212)

## v1.1.6
 - Python 3 support (PR#107, @piotr1212)
 - Use --copy-dest, enabling the rsync algorithm when copying from remote to staging (PR#106, @luke-heberling)
 - fix lint errors (PR#105, @YevhenLukomskyi)
 - specify long_description_content_type, so that package description is properly rendered on pypi.org (PR#104, @YevhenLukomskyi)

## v1.1.4
 - Use the scandir version of os.walk if possible (PR#99, @deejay1)
 - Include LICENSE in MANIFEST.in (PR#100, @deejay1)

## v1.1.3
 - Fixing carbon router hash (PR#93, @deniszh)
 - Adding LICENSE file to pypi package (PR#97, @deniszh)

## v1.1.2
 - carbon-sync: expose --overwrite to copy all non-null datapoints (PR#89, @jehiah)
 - fill: fix bugs causing some data points not to be copied (PR#90, @jehiah)

## v1.1.1
 - passing empty list for nodes seems to work (PR#87, @olevchyk)

## v1.0.2
 - (Experimental) support for fnv1a_ch hashing (PR#83, @deniszh)

## v1.0.0
 - Bumping version to 1.0.0 to match Graphite releases
 - unpin Twisted, remove py26 support (PR#78, @iksaif). Carbonate should still be Python 2.6 compatible, but newer Twisted is not
 - Fix reading whisper_lock_writes from cluster config in carbon_sync (PR#77, @justincmoy)

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
