"""Login Model

"""
from pignus.models.base import Base


FIELD_MAP = [
    {
        "name": "user_id",
        "type": "int",
    },
    {
        "name": "request_id",
        "type": "str",
    },
    {
        "name": "request_ip",
        "type": "str",
    },
    {
        "name": "request_agent",
        "type": "str",
    },
    {
        "name": "request_uri",
        "type": "str",
    },
    {
        "name": "request_method",
        "type": "str",
    },
    {
        "name": "request_payload",
        "type": "text",
    },
    {
        "name": "response_code",
        "type": "int",
    },
    {
        "name": "access_perm_slug",
        "type": "str",
    },
    {
        "name": "authenticated",
        "type": "bool",
        "default": False
    },
]


class Request(Base):

    model_name = "request"

    def __init__(self, conn=None, cursor=None):
        super(Request, self).__init__(conn, cursor)
        self.table_name = "requests"
        self.metas = {}
        self.field_map = FIELD_MAP
        self.setup()


# End File: automox/pignus/src/pignus/models/request.py
