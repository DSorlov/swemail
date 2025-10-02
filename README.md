![maintained](https://img.shields.io/maintenance/yes/2025.svg)
[![hacs_badge](https://img.shields.io/badge/hacs-default-green.svg)](https://github.com/custom-components/hacs)
[![ha_version](https://img.shields.io/badge/home%20assistant-2024.10%2B-green.svg)](https://www.home-assistant.io)
![version](https://img.shields.io/badge/version-2.0.0-green.svg)
![stability](https://img.shields.io/badge/stability-stable-green.svg)
[![CI](https://github.com/DSorlov/swemail/workflows/CI/badge.svg)](https://github.com/DSorlov/swemail/actions/workflows/ci.yaml)
[![hassfest](https://github.com/DSorlov/swemail/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/DSorlov/swemail/actions/workflows/hassfest.yaml)
[![HACS](https://github.com/DSorlov/swemail/workflows/HACS%20Validation/badge.svg)](https://github.com/DSorlov/swemail/actions/workflows/hacs.yaml)
[![maintainer](https://img.shields.io/badge/maintainer-dsorlov-blue.svg)](https://github.com/DSorlov)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Svensk Postutdelning / Swedish Mail Delivery
============================================

A small and simple integration to provide information about delivery days for Postnord and Citymail in any swedish postal code.

## Install using HACS

* If you haven't already you must have [HACS installed](https://hacs.xyz/docs/setup/download).
* Go into HACS and search for Svensk Postutdelning under the Integrations headline. Install it. You will need to restart Home Assistant to finish the process.
* Once that is done, try to reload your GUI (caching issues could prevent the integration to be shown).
* Goto Integrations and add Svensk Postutdelning or Swedish Mail Delivery (depending on language)
* Enter postal code and select your providers
* Sensors are created and updated. Enjoy!
  - One sensor for each selected provider
  - An additional combined sensor regardless of provider

