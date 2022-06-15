"""Base Rest
Parent object for all rest models. Primarily to hydrates the Image from the json response coming
from the Pignus API.

"""
from pignus.utils import date_utils


class RestBase:

    def save(self):
        return True

    def build(self, field_map: list, data: dict) -> bool:
        """Build the data into the Rest model. """
        for field in field_map:
            setattr(self, field["name"], None)

        if not data:
            return False

        for field_name, field_value in data.items():
            date_pattern = ["last_seen", "first_seen", "_ts"]
            _set = False
            for pat in date_pattern:
                if pat in field_name:
                    setattr(self, field_name, date_utils.date_from_json(field_value))
                    _set = True
                    break
            if not _set:
                setattr(self, field_name, field_value)
            _set = False
        return True

# End File: automox/pignus/src/pignus/models/rest_base.py
