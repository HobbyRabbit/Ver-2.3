import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_MAC


class ACInfinityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"AC Infinity {user_input[CONF_MAC]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_MAC): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
