# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] (2026-07-15)
Feature and bug fix release: automation-friendly entities and triggers plus fixes for sensors becoming unavailable and log spam.

### Added
- Binary sensors **Delivery Today** and **Delivery Tomorrow** (combined, plus per-provider "today"), so automations can trigger on a simple on/off state without templates.
- **Calendar** entity exposing upcoming delivery days as all-day events, enabling Home Assistant calendar triggers (closes [#40](https://github.com/DSorlov/swemail/issues/40)).
- **Device triggers**: pick the "Mail Delivery" device in the automation editor and choose *"Mail is delivered today/tomorrow"*.
- **Events** fired by the coordinator: `swemail_delivery_today` and `swemail_next_delivery_changed` (with `postal_code`, `provider`, `next_delivery`).
- **Automation blueprints** with one-click import links in the README for "notify when mail is delivered today" and "reminder the evening before".
- New `upcoming_delivery` attribute exposing the delivery after the next one (from PostNord's `upcoming` field, which was previously discarded). On the combined sensor it is also available as `<provider>_upcoming_delivery` and `next_upcoming_delivery`. This is particularly useful for the "fasta dagar" pilot areas where it hints at the two fixed weekly days.
- Diagnostics support: download redacted config entry and coordinator data from the integration's "Download diagnostics" button for easier troubleshooting.
- Optional extra entities (opt-in via the integration options, off by default): when enabled, each provider also gets a first-class next delivery **date** sensor and a **postal city** sensor, grouped under the existing device. Existing entities are unchanged.

### Fixed
- PostNord sensors stuck as `unavailable` ([#42](https://github.com/DSorlov/swemail/issues/42)): delivery data was cached under a string postal code key while the sensor looked it up with an integer key, so the value was never found. Data is now consistently keyed on the integer postal code.
- Log spam and `list index out of range` for areas without a scheduled date ([#38](https://github.com/DSorlov/swemail/issues/38), [#41](https://github.com/DSorlov/swemail/issues/41)): empty or unexpected PostNord `delivery` responses (e.g. the "fasta dagar" pilot) are now handled gracefully and logged at debug level instead of raising an error every update.
- More robust CityMail parsing ([#42](https://github.com/DSorlov/swemail/issues/42)): the HTML scraping is resilient to whitespace/newlines and no longer silently retains stale data when a postal code is not covered.
- Rewrote the broken system health page so it reports the active coordinators instead of referencing the removed v1 worker object.
- Options flow now uses the modern `self.config_entry` pattern, removing the deprecated config entry handling.
- Provider selection made in the options flow now actually takes effect (setup reads the merged config data and options).

### Changed
- Use the `Platform` enum for platform setup and cleaned up leftover copy-paste docstrings.
- Reuse Home Assistant's shared aiohttp session (`async_get_clientsession`) instead of creating a new session on every API call.
- Moved the data update coordinator into a dedicated `coordinator.py` module and reload the entry automatically when its options change.
- Added `strings.json` as the translation source and regression tests (pytest) covering the PostNord key, empty/"N/A" delivery, and CityMail parsing.
- Renamed the internal `woker` package to `api` (import paths updated; no user-facing change).

## [2.0.0] (2025-10-02)
Major architecture overhaul to completely modernize the integration
Removing Clearbit dependency and improvements in blocking http io operations.

### Added
- New Language Support: Added translations for Danish (da), Norwegian (no), Finnish (fi), Spanish (es), Turkish (tr), Arabic (ar), and Ukrainian (uk)
- Migration handling: Automatic upgrade from v1.x to v2.x with proper version tracking

### Changed
- Replaced requests with aiohttp - Eliminated blocking I/O operations
- Improved device info - Better device registry integration
- Enhanced attribute management - More efficient and reliable state updates
- Better date handling - Fixed midnight edge case calculations
- Concurrent API calls - All provider data fetched simultaneously for better performance

### Fixed
- Translation display: Removed device class override that caused "2d" format instead of "om två dagar"
- Config flow deprecation: Updated options flow to use modern HomeAssistant 2025.12+ patterns
- Upgrade compatibility: Added proper migration from v1.x installations

### Removed
- Clearbit API calls - no logo is available because it simply is not an asked for feature
- Duration device class - Allows custom translations to work properly

### Performance Improvements
- Non-blocking operations - All network calls are now async
- Reduced update frequency - Coordinator prevents redundant API calls
- Better resource management - Proper session handling and cleanup

## [1.0.7] (2023-06-12)

### Fixes
- Fixed [#23](https://github.com/DSorlov/swemail/issues/23). Thanks to @thulin82

## [1.0.6] (2023-05-19)

### Fixes
- Fixed [#19](https://github.com/DSorlov/swemail/issues/19) and [#22](https://github.com/DSorlov/swemail/issues/22) Translation file updated format. Thanks @angarok
- Fixed [#21](https://github.com/DSorlov/swemail/issues/21) Grammar and spelling. Thanks @thulin82


## [1.0.5] (2023-02-09)

### Fixes
- Fixed [#16](https://github.com/DSorlov/swemail/issues/16) async_forward_entry_setups. Thanks @KentEkl

## [1.0.4] (2022-05-29)

### Fixes
- Fixed errors in hacs manifest

## [1.0.3] (2022-02-26)

### Fixes
- Fixed [#7](https://github.com/DSorlov/swemail/issues/7) documentation updates
- Fixed [#8](https://github.com/DSorlov/swemail/issues/8) fixing illegal state

### Added
- Merged [PR #6](https://github.com/DSorlov/swemail/pull/6) adding french translation, thanks @matfouc
- Added comparison links to version headers in changelog

## [1.0.2] (2022-02-21)

If your integration lacks a title and icon, remove it and add it again.
This will solve the issue. It will work without title but it looks nicer
with a tit

### Fixes
- Fixed [#1](https://github.com/DSorlov/swemail/issues/1)
- Fixed [#2](https://github.com/DSorlov/swemail/issues/2)
- Fixed [#3](https://github.com/DSorlov/swemail/issues/3), thanks to @ehn for pull

### Added
- Now checks the postcode for validity before submitting it to the configuration

## [1.0.1] (2022-02-18)

### Fixes
- Fixed initial configuration bug, did not create sensors correctly without reboot
- Fixed error calculating combined sensor due to stupidity on my behalf
- Fixed stupid documentation errors (copy-paste errors)

### Changed
- To make templating easier additional values were moved to subclasses in sensor values
- Added translations for Swedish and English and for sensor values 

## [1.0.0] (2022-02-17)

### Initial release
- This is a great day indeed.

[keep-a-changelog]: http://keepachangelog.com/en/1.0.0/
[1.0.3]: https://github.com/DSorlov/swemail/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/DSorlov/swemail/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/DSorlov/swemail/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/dsorlov/swemail