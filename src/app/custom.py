"""Modulo para definir comportamientos customizables de la aplicacion."""

import json
from quart.json.provider import DefaultJSONProvider
from .app import app

class CustomJSONProvider(DefaultJSONProvider):
    """Evitar que se ordenen las llaves al serializar el json."""

    def dumps(self, obj, **kwargs):
        kwargs.setdefault("sort_keys", False)
        return json.dumps(obj, **kwargs)

app.json_provider_class = CustomJSONProvider
app.json = app.json_provider_class(app)
