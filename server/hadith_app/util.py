from datetime import datetime
from flask.json.provider import DefaultJSONProvider

from hadith_app.service.hadith_service import HadithDto


class AppJSONProvider(DefaultJSONProvider):
    def __init__(self, app):
        super().__init__(app)

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, HadithDto):
            obj_dict = {k: v for k, v in obj.__dict__.items() if v is not None}
            return obj_dict
        elif isinstance(obj, dict):
            return {k: v for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [item for item in obj if item is not None]
        return super().default(obj)
