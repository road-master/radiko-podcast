# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`radiko-podcast` is a Python CLI tool that automatically downloads and archives Japanese internet radio (radiko) programs beyond the standard 7-day availability window. It fetches program schedules from the Radiko API, tracks download status in SQLite, and archives audio as `.m4a` files using FFmpeg.

## Commands

```bash
# Install dependencies
uv sync

# Run all tests
invoke test.all

# Run a single test
invoke test -- -k test_name

# Format code
invoke style

# Check formatting without fixing
invoke style --check

# Standard linting (ruff, flake8, mypy, pylint)
invoke lint

# Full linting (adds radon, xenon, semgrep, bandit)
invoke lint.deep

# Build distribution for PyPI
invoke dist
```

## Architecture

### Data Flow

```
config.yml → RadikoPodcast (orchestrator)
                 └── ProgramSchedule (every 24h at 5:15 AM JST)
                       ├── RadikoApi → XML → XmlParser → XmlConverter → SQLAlchemy models (SQLite)
                       └── ProgramDownloader → RadikoArchiver → asyncffmpeg → .m4a file
```

### Key Components

**Entry point**: `radikopodcast/cli.py` (Click CLI) → `radikopodcast/radiko_podcast.py` (`RadikoPodcast` class)

**Concurrency**: `asyncio` event loop with `ProcessTaskPoolExecutor` for parallel FFmpeg downloads (`number_process` config key).

**Radiko API layer** (`radikopodcast/radikoapi/`): Fetches station list and daily program schedules as XML. Uses `defusedxml` for security.

**XML parsing** (`radikopodcast/radikoxml/`): `XmlParser` base with error collection; `XmlParserProgram`/`XmlParserStation` parse elements; `XmlConverter` converts to SQLAlchemy models.

**Database** (`radikopodcast/database/`): SQLite via SQLAlchemy ORM. `Station` and `Program` models. Program status state machine: `ARCHIVABLE → ARCHIVING → ARCHIVED | SUSPENDED | FAILED`. `ProgramSchedule` re-fetches the past 7 days each cycle and cleans up programs older than 7 days.

**Archiving**: `RadikoArchiver` + `RadikoStreamSpecFactory` build FFmpeg stream specs; `asyncffmpeg` runs FFmpeg in subprocess.

**Configuration** (`radikopodcast/config.py`): YAML loaded into a dataclass via `yamldataclassconfig`. Fields: `area_id` (ISO 3166-2:JP), `number_process`, `stop_if_file_exists`, `keywords` (title keyword list). Example at `config.yml.dist`.

**Datetime**: All times are JST (UTC+9). `RadikoDatetime` in `radikopodcast/radiko_datetime.py` handles Radiko's `YYYYMMDDHHmmss` format.

### Global Singletons

`radikopodcast/__init__.py` exposes `Session` (SQLAlchemy session factory) and `CONFIG` (loaded config) as module-level globals used throughout the package.

## Testing Patterns

- `pytest` with `pytest-asyncio`, `pytest-freezegun`, `pytest-mock`, `pytest-resource-path`
- Tests in `tests/` mirror source structure
- XML/data fixtures loaded via `pytest-resource-path`
- Time-dependent logic tested with `freezegun`

## Code Conventions

- **Type hints**: Full strict mypy (with SQLAlchemy plugin)
- **Docstrings**: Google style, enforced by `docformatter`
- **Line length**: 119 characters
- **Imports**: Managed by ruff/isort — when adding a new import alongside its usage, make both changes in a single `Write` call (not separate `Edit` calls) to avoid linter stripping the import between edits
