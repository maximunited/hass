# Home Assistant Configuration

This repository contains the configuration files, custom components, and resources for a Home Assistant instance. It is designed to be modular, maintainable, and easy to extend for smart home automation and monitoring.

## Features

- Modular YAML configuration (split by domain)
- Custom components and integrations
- Device and area organization
- Automations, scripts, and scenes
- Backup and recovery files
- Community and custom Lovelace UI resources

## Troubleshooting

- **[repo-docs/HA_DIAGNOSTICS.md](repo-docs/HA_DIAGNOSTICS.md)** — this **repository’s** troubleshooting notes (not official Home Assistant docs): log/MCP findings, integration health, in-repo fixes vs HA UI work. Update when you resolve issues. **Cursor:** `.cursor/rules/homeassistant-repo-docs.mdc` asks the agent to read that file for HA-related tasks; you can also attach **`@repo-docs/HA_DIAGNOSTICS.md`**.

## Directory Structure

- `repo-docs/` — Notes for **this repo** (e.g. diagnostics / troubleshooting), not core HA product documentation
- `.cursor/rules/` — Cursor project rules. **Karpathy-style coding guidelines** are loaded via a symlink to [`vendor/andrej-karpathy-skills`](vendor/andrej-karpathy-skills) (see below). Other rules: load `repo-docs/HA_DIAGNOSTICS.md` for HA troubleshooting; do not edit `custom_components/` / `www/community/` without explicit confirmation
- `vendor/andrej-karpathy-skills/` — Git submodule: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) (Cursor rule source; update with `git pull` inside this directory or via `git submodule update --remote` from the repo root—see **Updating vendored Cursor guidelines**)
- `configuration.yaml` — Main entry point for Home Assistant
- `automations.yaml` — All automations (or `automation/` folder if split)
- `custom_components/` — Custom integrations
- `www/` — Lovelace UI resources (cards, icons, images)
- `sensors/`, `switches.yaml`, `scenes.yaml`, etc. — Domain-specific configs
- `secrets.yaml` — Sensitive credentials (not for public sharing)
- `backups/` — Backup files
- `.storage/` — Home Assistant internal storage (do not edit manually)

## Setup

1. Clone this repository **including submodules** (needed for Cursor Karpathy guidelines under `vendor/andrej-karpathy-skills`):

   ```sh
   git clone --recurse-submodules https://github.com/maximunited/hass.git
   ```

   If you already cloned without submodules, fetch them once:

   ```sh
   git submodule update --init --recursive
   ```

2. (Optional, recommended on PEP 668 systems) Create a venv and install dev tools:

   ```sh
   cd hass
   python3 -m venv .venv
   .venv/bin/pip install -r requirements-dev.txt
   .venv/bin/pre-commit install
   ```

3. Copy the example secrets file and fill in your own values:

   ```sh
   cp secrets.yaml.sample secrets.yaml
   # Then edit secrets.yaml and provide your real credentials and secrets
   ```

4. Review and adjust `configuration.yaml` for your environment.
5. Place custom resources in `custom_components/` and `www/` as needed.
6. Start Home Assistant (Docker, venv, or supervised).

## Updating vendored Cursor guidelines

The [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) submodule powers `.cursor/rules/karpathy-guidelines.mdc` (symlink). To pull upstream `main` and record the new submodule commit in this repo:

```sh
cd vendor/andrej-karpathy-skills
git pull origin main
cd ../..
git add vendor/andrej-karpathy-skills
git commit -m "Bump andrej-karpathy-skills submodule"
```

Alternative from the repository root:

```sh
git submodule update --remote vendor/andrej-karpathy-skills
git add vendor/andrej-karpathy-skills
git commit -m "Bump andrej-karpathy-skills submodule"
```

## Pre-commit Hooks

This repository includes pre-commit hooks to validate and format YAML files before commits.

### Installation

1. Install pre-commit and dependencies:

   ```sh
   pip install -r requirements-dev.txt
   # Or install individually:
   pip install pre-commit yamllint
   # Markdown: pre-commit installs markdownlint-cli (Node; v0.41.x supports Node 18+)
   ```

2. Install the git hooks:

   ```sh
   pre-commit install
   ```

### Usage

Pre-commit hooks will automatically run on `git commit`. They will:

- Check YAML syntax
- Lint YAML files for style issues (`yamllint`)
- Lint Markdown files (`markdownlint` via `markdownlint-cli`)
- Remove trailing whitespace
- Ensure files end with newlines
- Validate Home Assistant configuration (if `hass` command is available)
- Check for merge conflicts and private keys

To run hooks manually on all files:

```sh
pre-commit run --all-files
```

To skip hooks for a specific commit:

```sh
git commit --no-verify
```

## Contributing

Pull requests are welcome! Please:

- Follow the existing file structure and naming conventions
- Test your changes before submitting
- Do not include sensitive information

## License

See [LICENSE](LICENSE) for details.

## Credits

- [Home Assistant](https://www.home-assistant.io/)
- Community custom components and card authors

---

For questions or suggestions, open an issue or contact the repository maintainer.
