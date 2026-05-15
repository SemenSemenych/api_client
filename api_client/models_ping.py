import datetime

from pydantic import BaseModel, ConfigDict


class PingOptionsModel(BaseModel):
    packets: int | None = None
    protocol: str | None = None
    port: int | None = None
    ipVersion: int | None = None


class ProbePropsModel(BaseModel):
    continent: str | None = None
    region: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    asn: int | None = None
    longitude: float | None = None
    latitude: float | None = None
    network: str | None = None
    tags: list[str] | None = None
    resolvers: list[str] | None = None


class TimingsModel(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    ttl: int
    rtt: float


class StatsModel(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    min: float | None = None
    max: float | None = None
    avg: float | None = None
    total: int | None = None
    loss: int | None = None
    rcv: int | None = None
    drop: int | None = None


class ResultPropsModel(BaseModel):
    status: str
    rawOutput: str | None = None
    resolvedAddress: str | None = None
    resolvedHostname: str | None = None
    timings: list[TimingsModel]
    stats: StatsModel


class ResultsAnswerModel(BaseModel):
    probe: ProbePropsModel
    result: ResultPropsModel


class ProbeResultModel(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    id: str
    type: str
    status: str
    createdAt: datetime.datetime
    updatedAt: datetime.datetime
    target: str
    probesCount: int
    measurementOptions: PingOptionsModel
    results: list[ResultsAnswerModel] | None = None
