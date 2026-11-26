
import csv
from decimal import Decimal

from services.billing_service import BillingService
from services.input_service import InputService
from services.registration_service import RegistrationService
from services.pricing_service import PricingService


def test_tenure_discount_calculation():

    billing = BillingService()

    pricing_details = {
        "total_ncf": Decimal("130"),
        "total_channel_charges": Decimal("100"),
        "tenure_months": 12
    }

    bill = billing.calculate_bill(pricing_details)

    assert bill["discount"] == Decimal("10.00")
    assert bill["discount_pct"] == 10
    assert bill["discounted_channel_charges"] == Decimal("90.00")


def test_six_month_discount():

    billing = BillingService()

    pricing_details = {
        "total_ncf": Decimal("130"),
        "total_channel_charges": Decimal("100"),
        "tenure_months": 6
    }

    bill = billing.calculate_bill(pricing_details)

    assert bill["discount"] == Decimal("5.00")
    assert bill["discount_pct"] == 5


def test_no_discount_for_short_tenure():

    billing = BillingService()

    pricing_details = {
        "total_ncf": Decimal("130"),
        "total_channel_charges": Decimal("100"),
        "tenure_months": 3
    }

    bill = billing.calculate_bill(pricing_details)

    assert bill["discount"] == Decimal("0.00")
    assert bill["discount_pct"] == 0


def test_gst_calculation():

    billing = BillingService()

    pricing_details = {
        "total_ncf": Decimal("130"),
        "total_channel_charges": Decimal("100"),
        "tenure_months": 12
    }

    bill = billing.calculate_bill(pricing_details)

    # NCF 130 + discounted charges 90 = 220.
    # GST = 220 * 18% = 39.60.
    assert bill["taxable_amount"] == Decimal("220.00")
    assert bill["gst"] == Decimal("39.6000")


def test_final_amount_rounding():

    billing = BillingService()

    pricing_details = {
        "total_ncf": Decimal("130"),
        "total_channel_charges": Decimal("1"),
        "tenure_months": 0
    }

    bill = billing.calculate_bill(pricing_details)

    # 131 + 23.58 = 154.58, rounded to 155.
    assert bill["final_amount"] == Decimal("155")


def test_fta_only_bill():

    billing = BillingService()

    pricing_details = {
        "total_ncf": Decimal("130"),
        "total_channel_charges": Decimal("0"),
        "tenure_months": 0
    }

    bill = billing.calculate_bill(pricing_details)

    assert bill["ncf"] == Decimal("130")
    assert bill["channel_charges"] == Decimal("0")
    assert bill["gst"] == Decimal("23.40")
    assert bill["final_amount"] == Decimal("153")


def test_csv_reports_generation(tmp_path):

    registration = RegistrationService()
    input_service = InputService()
    pricing_service = PricingService(registration)
    billing_service = BillingService()

    input_service.register_all(
        "data/channels.csv",
        "data/bouquets.csv",
        "data/subscribers.csv",
        registration
    )

    billing_records = []

    for subscriber in registration.subscribers.values():

        pricing_details = pricing_service.calculate_subscriber_pricing(
            subscriber
        )

        bill = billing_service.calculate_bill(pricing_details)

        billing_records.append((subscriber, pricing_details, bill))

    # Generate reports inside pytest's temporary directory.
    import os

    original_directory = os.getcwd()

    try:
        os.chdir(tmp_path)

        output_files = billing_service.generate_csv_reports(
            billing_records,
            registration.errors
        )

        assert len(output_files) == 3

        # Check bills.csv.
        with open(output_files["bills"], newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        assert len(rows) == 25
        assert rows[0]["subscriber_id"] == "SUB-001"
        assert rows[-1]["subscriber_id"] == "SUB-025"

        # Check bill_lines.csv.
        with open(output_files["bill_lines"], newline="", encoding="utf-8") as file:
            bill_lines = list(csv.DictReader(file))

        assert len(bill_lines) > 0

        total_lines = [
            row for row in bill_lines
            if row["line_type"] == "TOTAL"
        ]

        assert len(total_lines) == 25

        # Check errors.csv.
        with open(output_files["errors"], newline="", encoding="utf-8") as file:
            errors = list(csv.DictReader(file))

        assert len(errors) == 3

    finally:
        os.chdir(original_directory)
