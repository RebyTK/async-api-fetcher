from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    email: str
    city: str | None = None


class WeatherResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    location: str
    country: str | None = None
    temperature: float
    humidity: float
    wind_speed: float


class CountryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    population: int
    region: str
