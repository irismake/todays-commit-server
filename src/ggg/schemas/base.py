import json

from pydantic import BaseModel, ConfigDict

class GggBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def to_json(self):
        return json.loads(self.model_dump_json())
