from .coordinator import ACInfinityCoordinator

DOMAIN = "ac_infinity"

async def async_setup_entry(hass, entry):
    coordinator = ACInfinityCoordinator(
        hass,
        entry.data["mac"],
        entry.title,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["switch"],
    )

    return True
