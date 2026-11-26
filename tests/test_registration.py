
import pytest

from services.input_service import InputService
from services.registration_service import RegistrationService


@pytest.fixture
def registration():
    service = RegistrationService()
    input_service = InputService()

    input_service.register_all(
        "data/channels.csv",
        "data/bouquets.csv",
        "data/subscribers.csv",
        service
    )

    return service


# --------------------------------
# REGISTRATION COUNT TESTS
# --------------------------------

def test_channel_registration_count(registration):
    assert len(registration.channels) == 260


def test_valid_bouquets_registered(registration):
    assert len(registration.bouquets) == 9


def test_subscribers_registered(registration):
    assert len(registration.subscribers) == 25


# --------------------------------
# INVALID BOUQUET TESTS
# --------------------------------

def test_invalid_bouquet_rejected(registration):
    assert registration.get_bouquet("BQ-07") is None


def test_invalid_bouquet_error_logged(registration):

    errors = [
        error for error in registration.errors
        if error["item_id"] == "BQ-07"
        and error["source"] == "bouquets.csv"
    ]

    assert len(errors) == 1
    assert "exceeds" in errors[0]["reason"]


# --------------------------------
# INVALID SUBSCRIBER SELECTIONS
# --------------------------------

def test_rejected_bouquet_ignored(registration):

    subscriber = registration.get_subscriber("SUB-013")

    assert "BQ-07" not in subscriber.connections[0].bouquet_ids
    assert "BQ-03" in subscriber.connections[0].bouquet_ids


def test_unknown_channel_ignored(registration):

    subscriber = registration.get_subscriber("SUB-014")

    assert "CH-999" not in subscriber.connections[0].channel_ids


def test_invalid_selection_errors_logged(registration):

    error_ids = {
        error["item_id"]
        for error in registration.errors
    }

    assert "BQ-07" in error_ids
    assert "CH-999" in error_ids


def test_total_registration_errors(registration):
    assert len(registration.errors) == 3


# --------------------------------
# DUPLICATE SELECTION TEST
# --------------------------------

def test_duplicate_channel_selection_removed(registration):

    subscriber = registration.get_subscriber("SUB-015")

    channel_ids = subscriber.connections[0].channel_ids

    assert len(channel_ids) == len(set(channel_ids))
    assert channel_ids.count("CH-005") == 1


# --------------------------------
# MULTI-TV HOUSEHOLD TEST
# --------------------------------

def test_multi_tv_connections_identified(registration):

    first_tv = registration.get_subscriber("SUB-010")
    second_tv = registration.get_subscriber("SUB-011")

    assert first_tv.address_id == second_tv.address_id
    assert first_tv.connection_no == 1
    assert second_tv.connection_no == 2
