from pydantic import BaseModel, ConfigDict

class NewProbeModel(BaseModel):
    id: str
    probesCount: int

