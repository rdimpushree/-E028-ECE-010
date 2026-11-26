
from services.input_service import InputService
from services.registration_service import RegistrationService

registration = RegistrationService()
input_service = InputService()

input_service.register_all(
    "data/channels.csv",
    "data/bouquets.csv",
    "data/subscribers.csv",
    registration
)

print("Registered channels:", len(registration.channels))
print("Registered bouquets:", len(registration.bouquets))
print("Registered subscribers:", len(registration.subscribers))
print("Errors:", len(registration.errors))

print("\nFirst subscriber:")
print(registration.get_subscriber("SUB-001"))

print("\nRegistration errors:")
for error in registration.errors:
    print(error)
