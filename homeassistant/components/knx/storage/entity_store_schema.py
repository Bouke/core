"""KNX entity store schema."""
import voluptuous as vol

from homeassistant.components.switch import (
    DEVICE_CLASSES_SCHEMA as SWITCH_DEVICE_CLASSES_SCHEMA,
)
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import ENTITY_CATEGORIES_SCHEMA

from ..validation import (
    ga_list_validator,
    ga_list_validator_optional,
    sync_state_validator,
)

BASE_ENTITY_SCHEMA = vol.Schema(
    {
        vol.Optional("name", default=None): vol.Maybe(str),
        vol.Optional("device_info", default=None): vol.Maybe(str),
        vol.Optional("entity_category", default=None): vol.Any(
            ENTITY_CATEGORIES_SCHEMA, vol.SetTo(None)
        ),
        vol.Optional("sync_state", default=True): sync_state_validator,
    }
)

SWITCH_SCHEMA = BASE_ENTITY_SCHEMA.extend(
    {
        vol.Optional("device_class", default=None): vol.Maybe(
            SWITCH_DEVICE_CLASSES_SCHEMA
        ),
        vol.Optional("invert", default=False): bool,
        vol.Required("switch_address"): ga_list_validator,
        vol.Required("switch_state_address"): ga_list_validator_optional,
        vol.Optional("respond_to_read", default=False): bool,
    }
)

ENTITY_STORE_DATA_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required("platform"): vol.Coerce(Platform),
            vol.Required("data"): dict,
        },
        extra=vol.ALLOW_EXTRA,
    ),
    cv.key_value_schemas(
        "platform",
        {
            Platform.SWITCH: vol.Schema(
                {vol.Required("data"): SWITCH_SCHEMA}, extra=vol.ALLOW_EXTRA
            )
        },
    ),
)

CREATE_ENTITY_BASE_SCHEMA = {
    vol.Required("platform"): str,
    vol.Required("data"): dict,  # validated by ENTITY_STORE_DATA_SCHEMA
}

UPDATE_ENTITY_BASE_SCHEMA = {
    vol.Required("unique_id"): str,
    **CREATE_ENTITY_BASE_SCHEMA,
}