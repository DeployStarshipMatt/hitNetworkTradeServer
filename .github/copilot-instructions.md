# Copilot Instructions for hitNetworkAutomation

## Project Overview
This repository automates trading and signal parsing for Discord and Blofin, structured into three main components:
- **discord-bot/**: Handles Discord bot logic, signal parsing, and trading client integration.
- **trading-server/**: Manages Blofin API authentication, trading operations, and server logic.
- **shared/**: Contains shared models and utilities for cross-component data exchange.

## Architecture & Data Flow
- Signals are parsed in `discord-bot/parser.py` and processed by the bot in `discord-bot/bot.py`.
- Trading actions are executed via `discord-bot/trading_client.py` and `trading-server/blofin_client.py`.
- Shared models in `shared/models.py` define data structures used across components.
- Communication between bot and server is via direct Python calls and shared models (no network microservices).

## Developer Workflows
- **Run all services**: Use `start_services.ps1` to launch both Discord bot and trading server.
- **Setup dependencies**: Run `setup.ps1` for initial environment setup (installs Python packages for all components).
- **Testing**: Run test scripts (e.g., `test_blofin_balance.py`, `test_parser_fil.py`) directly with Python. No unified test runner; test files are standalone.
- **Debugging**: Use print/log statements; no advanced logging or debugging frameworks are present.

## Project-Specific Patterns
- All inter-component data structures are defined in `shared/models.py` and imported as needed.
- Signal parsing logic is centralized in `discord-bot/parser.py`.
- Trading logic is split: Discord bot uses `trading_client.py`, server uses `blofin_client.py` and `blofin_auth.py`.
- Each major directory has its own `requirements.txt` for dependencies.
- Scripts (`*.ps1`) are used for orchestration and setup, not for business logic.

## Integration Points & Dependencies
- **External APIs**: Blofin trading API (see `trading-server/blofin_client.py`).
- **Discord API**: Used in `discord-bot/bot.py`.
- **Python 3.x** required; see `requirements.txt` in each component for packages.

## Examples
- To parse a signal: see `discord-bot/parser.py` for `parse_signal()` usage.
- To execute a trade: see `discord-bot/trading_client.py` and `trading-server/blofin_client.py` for `place_order()` patterns.
- To add a new shared model: update `shared/models.py` and import in relevant files.

## Conventions
- Use explicit imports from `shared/models.py` for data sharing.
- Keep orchestration logic in PowerShell scripts; keep business logic in Python modules.
- Tests are simple scripts, not formal test suites.

---
For questions or unclear patterns, review the relevant README files or ask for clarification.
