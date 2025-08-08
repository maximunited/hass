# Home Assistant Configuration

This repository contains the configuration files, custom components, and resources for a Home Assistant instance. It is designed to be modular, maintainable, and easy to extend for smart home automation and monitoring.

## Features
- Modular YAML configuration (split by domain)
- Custom components and integrations
- Device and area organization
- Automations, scripts, and scenes
- Backup and recovery files
- Community and custom Lovelace UI resources

## Directory Structure
- `configuration.yaml` — Main entry point for Home Assistant
- `automations.yaml` — All automations (or `automation/` folder if split)
- `custom_components/` — Custom integrations
- `www/` — Lovelace UI resources (cards, icons, images)
- `sensors/`, `switches.yaml`, `scenes.yaml`, etc. — Domain-specific configs
- `secrets.yaml` — Sensitive credentials (not for public sharing)
- `backups/` — Backup files
- `.storage/` — Home Assistant internal storage (do not edit manually)

## Setup
1. Clone this repository:
   ```sh
   git clone https://github.com/maximunited/hass.git
   ```
2. Copy the example secrets file and fill in your own values:
   ```sh
   cp secrets.yaml.sample secrets.yaml
   # Then edit secrets.yaml and provide your real credentials and secrets
   ```
3. Review and adjust `configuration.yaml` for your environment.
4. Place custom resources in `custom_components/` and `www/` as needed.
5. Start Home Assistant (Docker, venv, or supervised).

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
