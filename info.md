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
