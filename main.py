
import os
import sys

from services.registration_service import RegistrationService
from services.input_service import InputService
from services.pricing_service import PricingService
from services.billing_service import BillingService


def main():

    try:
        print("========================================")
        print("       CABLE TV PRICING ENGINE")
        print("========================================")

        # Step 1: Initialize services.
        registration_service = RegistrationService()
        input_service = InputService()
        pricing_service = PricingService(registration_service)
        billing_service = BillingService()

        # Step 2: Read commands file.
        commands_file = (
            sys.argv[1]
            if len(sys.argv) > 1
            else "data/commands.txt"
        )

        commands_directory = os.path.dirname(
            os.path.abspath(commands_file)
        )

        loaded_files = {}
        billing_completed = False

        with open(commands_file, "r", encoding="utf-8-sig") as file:

            for line_no, line in enumerate(file, start=1):

                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid command at line {line_no}: {line}"
                    )

                command = parts[0].strip()
                argument = parts[1].strip()

                # Step 3: Process LOAD commands.
                if command in (
                    "LOAD_CHANNELS",
                    "LOAD_BOUQUETS",
                    "LOAD_SUBSCRIBERS"
                ):

                    if billing_completed:
                        raise ValueError(
                            "LOAD commands cannot be executed after BILL_ALL"
                        )

                    if command in loaded_files:
                        raise ValueError(
                            f"Duplicate command: {command}"
                        )

                    file_path = os.path.join(
                        commands_directory,
                        argument
                    )

                    if not os.path.isfile(file_path):
                        raise FileNotFoundError(
                            f"Input file not found: {file_path}"
                        )

                    loaded_files[command] = file_path

                    print(f"Loaded command: {command}")

                # Step 4: Process BILL_ALL command.
                elif command == "BILL_ALL":

                    if billing_completed:
                        raise ValueError(
                            "BILL_ALL command can only be executed once"
                        )

                    required_commands = [
                        "LOAD_CHANNELS",
                        "LOAD_BOUQUETS",
                        "LOAD_SUBSCRIBERS"
                    ]

                    for required in required_commands:
                        if required not in loaded_files:
                            raise ValueError(
                                f"{required} must be executed before BILL_ALL"
                            )

                    billing_month = argument

                    # Validate billing month format.
                    if (
                        len(billing_month) != 7
                        or billing_month[4] != "-"
                        or not billing_month[:4].isdigit()
                        or not billing_month[5:].isdigit()
                        or not 1 <= int(billing_month[5:]) <= 12
                    ):
                        raise ValueError(
                            f"Invalid billing month: {billing_month}"
                        )

                    print("\nRegistering input data...")

                    # Register channels, bouquets and subscribers.
                    input_service.register_all(
                        loaded_files["LOAD_CHANNELS"],
                        loaded_files["LOAD_BOUQUETS"],
                        loaded_files["LOAD_SUBSCRIBERS"],
                        registration_service
                    )

                    print("\nRegistration completed!")

                    print(
                        "Channels registered:",
                        len(registration_service.channels)
                    )

                    print(
                        "Bouquets registered:",
                        len(registration_service.bouquets)
                    )

                    print(
                        "Subscribers registered:",
                        len(registration_service.subscribers)
                    )

                    # Step 5: Determine household tenure.
                    # The primary connection (connection_no = 1)
                    # defines the tenure for the entire household.

                    household_tenure = {}

                    for subscriber in registration_service.subscribers.values():

                        if subscriber.connection_no == 1:

                            if subscriber.address_id in household_tenure:
                                raise ValueError(
                                    f"Multiple primary connections found "
                                    f"for address: {subscriber.address_id}"
                                )

                            household_tenure[subscriber.address_id] = (
                                subscriber.tenure_months
                            )

                    # Step 6: Calculate bills for all subscribers.
                    billing_records = []

                    for subscriber in registration_service.subscribers.values():

                        if subscriber.address_id not in household_tenure:
                            raise ValueError(
                                f"No primary connection found for "
                                f"address: {subscriber.address_id}"
                            )

                        pricing_details = (
                            pricing_service.calculate_subscriber_pricing(
                                subscriber
                            )
                        )

                        # Apply the household's tenure to every connection.
                        pricing_details["tenure_months"] = (
                            household_tenure[subscriber.address_id]
                        )

                        bill = billing_service.calculate_bill(
                            pricing_details
                        )

                        billing_records.append((
                            subscriber,
                            pricing_details,
                            bill
                        ))

                    # Step 7: Generate the three required CSV reports.
                    output_files = billing_service.generate_csv_reports(
                        billing_records,
                        registration_service.errors
                    )

                    billing_completed = True

                    print("\n========== BILLING COMPLETED ==========")
                    print("Billing month:", billing_month)

                    print(
                        "Subscribers billed:",
                        len(billing_records)
                    )

                    print(
                        "Registration errors:",
                        len(registration_service.errors)
                    )

                    print("\nGenerated reports:")

                    for report_name, report_path in output_files.items():
                        print(f"{report_name}: {report_path}")

                    print("\n========================================")
                    print("       EXECUTION SUCCESSFUL")
                    print("========================================")

                else:
                    raise ValueError(
                        f"Unknown command at line {line_no}: {command}"
                    )

    except (
        ValueError,
        KeyError,
        TypeError,
        ArithmeticError,
        OSError
    ) as error:

        print(f"\nError: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
