"""Support for TPLink number entities."""

from __future__ import annotations

import logging
from typing import Final

from kasa import Device, Feature

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TPLinkConfigEntry
from .coordinator import TPLinkDataUpdateCoordinator
from .entity import (
    CoordinatedTPLinkFeatureEntity,
    TPLinkFeatureEntityDescription,
    async_refresh_after,
    entities_for_device_and_its_children,
)

_LOGGER = logging.getLogger(__name__)


class TPLinkNumberEntityDescription(
    NumberEntityDescription, TPLinkFeatureEntityDescription
):
    """Base class for a TPLink feature based sensor entity description."""


NUMBER_DESCRIPTIONS: Final = (
    TPLinkNumberEntityDescription(
        key="smooth_transition_on",
        mode=NumberMode.BOX,
    ),
    TPLinkNumberEntityDescription(
        key="smooth_transition_off",
        mode=NumberMode.BOX,
    ),
    TPLinkNumberEntityDescription(
        key="auto_off_minutes",
        mode=NumberMode.BOX,
    ),
    TPLinkNumberEntityDescription(
        key="temperature_offset",
        mode=NumberMode.BOX,
    ),
    TPLinkNumberEntityDescription(
        key="target_temperature",
        mode=NumberMode.BOX,
    ),
)

NUMBER_DESCRIPTIONS_MAP = {desc.key: desc for desc in NUMBER_DESCRIPTIONS}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: TPLinkConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    data = config_entry.runtime_data
    parent_coordinator = data.parent_coordinator
    children_coordinators = data.children_coordinators
    device = parent_coordinator.device

    entities = entities_for_device_and_its_children(
        device=device,
        coordinator=parent_coordinator,
        feature_type=Feature.Type.Number,
        entity_class=Number,
        child_coordinators=children_coordinators,
    )
    async_add_entities(entities)


class Number(CoordinatedTPLinkFeatureEntity, NumberEntity):
    """Representation of a feature-based TPLink sensor."""

    entity_description: TPLinkNumberEntityDescription

    def __init__(
        self,
        device: Device,
        coordinator: TPLinkDataUpdateCoordinator,
        *,
        feature: Feature,
        parent: Device | None = None,
    ) -> None:
        """Initialize the sensor."""
        description = self._description_for_feature(
            TPLinkNumberEntityDescription,
            feature,
            NUMBER_DESCRIPTIONS_MAP,
            native_min_value=feature.minimum_value,
            native_max_value=feature.maximum_value,
        )
        super().__init__(
            device,
            coordinator,
            description=description,
            feature=feature,
            parent=parent,
        )
        self._async_call_update_attrs()

    @async_refresh_after
    async def async_set_native_value(self, value: float) -> None:
        """Set feature value."""
        await self._feature.set_value(int(value))

    @callback
    def _async_update_attrs(self) -> None:
        """Update the entity's attributes."""
        self._attr_native_value = self._feature.value
