
import pytest
from decimal import Decimal

from services.input_service import InputService
from services.registration_service import RegistrationService
from services.pricing_service import PricingService


@pytest.fixture
def setup_engine():
    registration = RegistrationService()
    input_service = InputService()

    input_service.register_all(
        "data/channels.csv",
        "data/bouquets.csv",
        "data/subscribers.csv",
        registration
    )

    pricing = PricingService(registration)

    return registration, pricing


# --------------------------------
# NCF BOUNDARY TESTS
# --------------------------------

@pytest.mark.parametrize(
    "channel_count, expected_ncf",
    [
        (0, "0"),
        (1, "130"),
        (200, "130"),
        (201, "150"),
        (225, "150"),
        (226, "160"),
        (251, "160")
    ]
)
def test_ncf_calculation(setup_engine, channel_count, expected_ncf):

    _, pricing = setup_engine

    result = pricing.calculate_ncf(channel_count)

    assert result == Decimal(expected_ncf)


# --------------------------------
# SUBSCRIBER PRICING TESTS
# --------------------------------

def test_first_connection_ncf(setup_engine):

    registration, pricing = setup_engine

    subscriber = registration.get_subscriber("SUB-001")

    result = pricing.calculate_subscriber_pricing(subscriber)

    assert result["total_ncf"] == Decimal("130")


def test_second_connection_ncf(setup_engine):

    registration, pricing = setup_engine

    subscriber = registration.get_subscriber("SUB-011")

    result = pricing.calculate_subscriber_pricing(subscriber)

    assert result["total_ncf"] == Decimal("52")


def test_second_connection_keeps_full_channel_charges(setup_engine):

    registration, pricing = setup_engine

    subscriber = registration.get_subscriber("SUB-011")

    result = pricing.calculate_subscriber_pricing(subscriber)

    assert result["total_channel_charges"] == Decimal("78.23")


# --------------------------------
# DUPLICATE CHANNEL TEST
# --------------------------------

def test_duplicate_channel_selection_counted_once(setup_engine):

    registration, pricing = setup_engine

    subscriber = registration.get_subscriber("SUB-015")

    result = pricing.calculate_subscriber_pricing(subscriber)

    assert result["connections"][0]["unique_channel_count"] == 11


# --------------------------------
# BOUQUET OVERLAP TEST
# --------------------------------

def test_alacarte_channels_covered_by_bouquet_are_dropped(setup_engine):

    registration, pricing = setup_engine

    subscriber = registration.get_subscriber("SUB-016")

    result = pricing.calculate_subscriber_pricing(subscriber)

    connection = result["connections"][0]

    assert connection["dropped_alacarte_count"] == 2
