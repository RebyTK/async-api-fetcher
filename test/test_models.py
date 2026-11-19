from async_api_fetcher.models import CountryResponse, UserResponse, WeatherResponse

# Test 1: User
user = UserResponse.model_validate(
    {
        "id": 1,
        "name": "Leanne Graham",
        "email": "test@example.com",
        "city": "Gwenborough",
    }
)

print("\nUSER MODEL")
print(user)
print(user.model_dump())


# Test 2: Weather
weather = WeatherResponse.model_validate(
    {
        "location": "Delhi",
        "country": "India",
        "temperature": 25.1,
        "humidity": 39,
        "wind_speed": 7.1,
    }
)

print("\nWEATHER MODEL")
print(weather)


# Test 3: Country
country = CountryResponse.model_validate(
    {"name": "India", "population": 1429404000, "region": "Asia"}
)

print("\nCOUNTRY MODEL")
print(country)
