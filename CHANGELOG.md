# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2022-05-18
### Changed
- Use default line length for Black formatting instead of 120.
### Fixed
- Fix bugs in `ecomment.strip` so it passes the tests.
## [0.1.2] - 2022-06-25
### Added
- Initial test for `ecomment read` cli command.
### Changed
- Use absolute imports for tests.
- Rename file-data to file\_data.
### Fixed
- Return files in 'files' from 'read' to make the response valid json.
- Remove extra newlines from markup output.
