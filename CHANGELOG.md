# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] (2023-05-19)

### Fixes
- Fixed [#19](https://github.com/DSorlov/swemail/issues/19) 
- Fixed [#20](https://github.com/DSorlov/swemail/issues/20)


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