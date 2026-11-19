import argparse


def positive_int(value: str) -> int:

    try:
        number = int(value)

    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "User ID must be an integer"
        ) from exc

    if number <= 0:
        raise argparse.ArgumentTypeError(
            "User ID must be positive"
        )

    return number


def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Async Multi-API Fetcher CLI"
    )

    parser.add_argument(
        "--user-id",
        type=positive_int,
        required=True,
        help="ID of the user to fetch"
    )

    parser.add_argument(
        "--weather-location",
        type=str,
        required=True,
        help="City for weather information"
    )

    parser.add_argument(
        "--country",
        type=str,
        required=True,
        help="Country to fetch information about"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching and always fetch fresh API data"
    )


    return parser.parse_args()
