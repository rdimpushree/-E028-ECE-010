
from services.input_service import InputService
from services.registration_service import RegistrationService
from services.pricing_service import PricingService
from services.billing_service import BillingService


# Initialize services.
registration = RegistrationService()
input_service = InputService()
pricing_service = PricingService(registration)
billing_service = BillingService()


# Load and register all CSV data.
input_service.register_all(
    "data/channels.csv",
    "data/bouquets.csv",
    "data/subscribers.csv",
    registration
)


# Calculate bills for all subscribers.
billing_records = []

for subscriber in registration.subscribers.values():

    pricing_details = pricing_service.calculate_subscriber_pricing(
        subscriber
    )

    bill = billing_service.calculate_bill(pricing_details)

    billing_records.append((
        subscriber,
        pricing_details,
        bill
    ))


# Generate the three required CSV reports.
output_files = billing_service.generate_csv_reports(
    billing_records,
    registration.errors
)


print("\n========== BILLING COMPLETED ==========")

for report, path in output_files.items():
    print(f"{report}: {path}")

print("\nTotal subscribers billed:", len(billing_records))
print("Total registration errors:", len(registration.errors))

print("\nSample bill: SUB-001")

for subscriber, pricing_details, bill in billing_records:
    if subscriber.subscriber_id == "SUB-001":
        print("NCF:", bill["ncf"])
        print("Channel charges:", bill["channel_charges"])
        print("Discount:", bill["discount"])
        print("GST:", bill["gst"])
        print("Final amount:", bill["final_amount"])
        break
