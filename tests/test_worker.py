"""Regression tests for the HttpWorker parsing logic.

These cover the bugs fixed in 2.1.0:
- #42  PostNord data keyed on a string instead of the int postal code.
- #38/#41  Empty / "N/A" PostNord delivery raising errors / log spam.
- #42  CityMail scraping being fragile.

The worker is imported directly (falling back to an isolated loader) so the
tests run without a full Home Assistant installation.
"""

import importlib.util
import sys
import types
from pathlib import Path

try:  # Preferred: Home Assistant available (CI)
    from custom_components.swemail.const import (
        CONF_PROVIDER_CITYMAIL,
        CONF_PROVIDER_POSTNORD,
    )
    from custom_components.swemail.api import HttpWorker
except Exception:  # noqa: BLE001 - fall back to isolated import without HA
    COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "swemail"
    if "swemail" not in sys.modules:
        _pkg = types.ModuleType("swemail")
        _pkg.__path__ = [str(COMPONENT)]
        sys.modules["swemail"] = _pkg

    def _load(name, path, is_pkg=False):
        locations = [str(Path(path).parent)] if is_pkg else None
        spec = importlib.util.spec_from_file_location(
            name, path, submodule_search_locations=locations
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    _const = _load("swemail.const", COMPONENT / "const.py")
    _api = _load("swemail.api", COMPONENT / "api" / "__init__.py", is_pkg=True)
    HttpWorker = _api.HttpWorker
    CONF_PROVIDER_POSTNORD = _const.CONF_PROVIDER_POSTNORD
    CONF_PROVIDER_CITYMAIL = _const.CONF_PROVIDER_CITYMAIL


CITYMAIL_HTML = """
<div class="result">
  <h2>11122 STOCKHOLM</h2>
  <p>Citymail delar ut brev på detta postnummer.</p>
  Nästa utdelningsdag: <span class="boldGreen">2026-07-20</span>
</div>
"""

CITYMAIL_NO_MATCH = "<h2>När delar vi ut brev i ditt område?</h2>"


def test_postnord_keyed_on_int_postalcode():
    """#42: data must be keyed on the int postal code, not the JSON string."""
    worker = HttpWorker()
    worker._handle_pn_data(
        {
            "postalCode": "11122",
            "city": "Stockholm",
            "delivery": "17 juli, 2026",
            "upcoming": "21 juli, 2026",
        },
        11122,
    )
    provider = worker.data[CONF_PROVIDER_POSTNORD]
    assert 11122 in provider
    assert "11122" not in provider
    assert provider[11122]["next_delivery"] == "2026-07-17"
    assert provider[11122]["upcoming_delivery"] == "2026-07-21"
    assert provider[11122]["postal_city"] == "Stockholm"


def test_postnord_empty_or_na_delivery_is_graceful():
    """#38/#41: empty / N/A delivery must not raise and yields empty dates."""
    worker = HttpWorker()
    worker._handle_pn_data(
        {"postalCode": "47530", "city": "", "delivery": "N/A", "upcoming": "N/A"},
        47530,
    )
    provider = worker.data[CONF_PROVIDER_POSTNORD]
    assert provider[47530]["next_delivery"] == ""
    assert provider[47530]["upcoming_delivery"] == ""


def test_parse_pn_date():
    worker = HttpWorker()
    assert worker._parse_pn_date("17 juli, 2026") == "2026-07-17"
    assert worker._parse_pn_date("5 maj, 2026") == "2026-05-05"
    assert worker._parse_pn_date("") == ""
    assert worker._parse_pn_date("N/A") == ""
    assert worker._parse_pn_date(None) == ""


def test_citymail_parses_date_and_city():
    """#42: robust CityMail scraping keyed on the int postal code."""
    worker = HttpWorker()
    worker._handle_cm_data(CITYMAIL_HTML, 11122)
    provider = worker.data[CONF_PROVIDER_CITYMAIL]
    assert 11122 in provider
    assert provider[11122]["next_delivery"] == "2026-07-20"
    assert provider[11122]["postal_city"] == "Stockholm"


def test_citymail_no_match_is_graceful():
    """A postal code without coverage yields empty data, no exception."""
    worker = HttpWorker()
    worker._handle_cm_data(CITYMAIL_NO_MATCH, 11122)
    provider = worker.data[CONF_PROVIDER_CITYMAIL]
    assert provider[11122]["next_delivery"] == ""
    assert provider[11122]["postal_city"] == ""
