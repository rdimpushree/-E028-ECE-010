
from services.input_service import InputService
from services.registration_service import RegistrationService
from services.pricing_service import PricingService

registration = RegistrationService()
input_service = InputService()

input_service.register_all(
    "data/channels.csv",
    "data/bouquets.csv",
    "data/subscribers.csv",
    registration
)

pricing = PricingService(registration)

# Test a normal first connection.
subscriber_1 = registration.get_subscriber("SUB-001")
result_1 = pricing.calculate_subscriber_pricing(subscriber_1)

print("SUB-001")
print("Connection:", subscriber_1.connection_no)
print("Channel count:", result_1["connections"][0]["unique_channel_count"])
print("NCF:", result_1["total_ncf"])
print("Channel charges:", result_1["total_channel_charges"])

# Test a second TV connection.
subscriber_2 = registration.get_subscriber("SUB-011")
result_2 = pricing.calculate_subscriber_pricing(subscriber_2)

print("\nSUB-011")
print("Connection:", subscriber_2.connection_no)
print("Channel count:", result_2["connections"][0]["unique_channel_count"])
print("NCF:", result_2["total_ncf"])
print("Channel charges:", result_2["total_channel_charges"])
