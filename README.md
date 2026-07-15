![maintained](https://img.shields.io/maintenance/yes/2026.svg)
[![hacs_badge](https://img.shields.io/badge/hacs-default-green.svg)](https://github.com/custom-components/hacs)
[![ha_version](https://img.shields.io/badge/home%20assistant-2024.10%2B-green.svg)](https://www.home-assistant.io)
![version](https://img.shields.io/badge/version-2.1.0-green.svg)
![stability](https://img.shields.io/badge/stability-stable-green.svg)
[![CI](https://github.com/DSorlov/swemail/workflows/CI/badge.svg)](https://github.com/DSorlov/swemail/actions/workflows/ci.yaml)
[![hassfest](https://github.com/DSorlov/swemail/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/DSorlov/swemail/actions/workflows/hassfest.yaml)
[![HACS](https://github.com/DSorlov/swemail/workflows/HACS%20Validation/badge.svg)](https://github.com/DSorlov/swemail/actions/workflows/hacs.yaml)
[![maintainer](https://img.shields.io/badge/maintainer-dsorlov-blue.svg)](https://github.com/DSorlov)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Svensk Postutdelning / Swedish Mail Delivery
============================================

A small integration to provide information about delivery days for Postnord and Citymail in any swedish postal code as defined by Postnord and Citymail. The integration will create a sensor for each postal code, and also separate sensors for Postnord and/or Citymail as specified. The common sensor will show the next delivery date regardless of operator.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the "+" button
4. Search for "Svensk Postutdelning"
5. Install the integration
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/dsorlov/swemail/releases)
2. Extract the `custom_components/swemail` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Svensk Postutdelning"
4. Follow the configuration steps.

## Localization

I have tried to use machine translation to create a few useable translations. Please correct me if there are any major wrongs or you are missing some languages:

- :uk: English (en.json) - English
- :sweden: Swedish (sv.json) - Svenska
- :iceland: Icelandic (is.json) - Íslenska
- :denmark: Danish (da.json) - Dansk
- :norway: Norwegian (no.json) - Norsk
- :finland: Finnish (fi.json) - Suomi
- :es: Spanish (es.json) - Español
- :tr: Turkish (tr.json) - Türkçe
- :saudi_arabia: Arabic (ar.json) - العربية
- :ukraine: Ukrainian (uk.json) - Українська
- :fr: French (fr.json) - Français

## Entities

For each configured postal code a device is created with:

- **Days until delivery** sensor(s) – number of days until the next delivery (per provider, plus a combined sensor when several providers are enabled).
- **Delivery today / tomorrow** binary sensors – `on` when mail is delivered that day. Great for automations.
- **Delivery calendar** – upcoming delivery days as all-day calendar events (works with Home Assistant calendar triggers).
- Optional (opt-in via the integration options): a **next delivery date** sensor and a **postal city** sensor per provider.

Attributes on the days sensors include `next_delivery`, `upcoming_delivery`, `postal_city` and `last_update`.

## Automations

### Blueprints (one-click import)

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fdsorlov%2Fswemail%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fswemail%2Fmail_delivery_today.yaml) **Notify when mail is delivered today**

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fdsorlov%2Fswemail%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fswemail%2Fmail_delivery_tomorrow.yaml) **Reminder the evening before a delivery day**

### Device triggers

When creating an automation, pick the "Mail Delivery" device and choose a trigger such as *"Mail is delivered today"* or *"Mail is delivered tomorrow"* — no templates required.

### Events

The integration fires the following events you can trigger on:

- `swemail_delivery_today` – fired when the next delivery becomes today. Data: `postal_code`, `provider`, `next_delivery`.
- `swemail_next_delivery_changed` – fired when the next delivery date changes. Data: `postal_code`, `provider`, `next_delivery`, `previous`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- :bug: [Report a Bug](https://github.com/dsorlov/snmpPrinter/issues)
- :bulb: [Request a Feature](https://github.com/dsorlov/snmpPrinter/issues)
- :book: [Documentation](https://github.com/dsorlov/snmpPrinter)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
