from pydantic import BaseModel


class CreateLimitsModel(BaseModel):
    """ Moder for getting limits """
    type: str
    limit: int
    remaining: int
    reset: int

class CreateMeasurementModel(BaseModel):
    create: CreateLimitsModel


class MeasurementModel(BaseModel):
    measurements: CreateMeasurementModel


class LimitsModel(BaseModel):
    rateLimit: MeasurementModel
