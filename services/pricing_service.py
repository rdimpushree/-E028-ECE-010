
from decimal import Decimal


class PricingService:

    def __init__(self, registration_service):
        self.registration = registration_service

    # 1. GET ALL SELECTED CHANNELS
    def get_selected_channels(self, connection):

        selected_channel_ids = set(connection.channel_ids)

        for bouquet_id in connection.bouquet_ids:
            bouquet = self.registration.get_bouquet(bouquet_id)

            if bouquet:
                selected_channel_ids.update(bouquet.channel_ids)

        return selected_channel_ids

    # 2. CALCULATE NCF
    def calculate_ncf(self, channel_count):

        if channel_count <= 0:
            return Decimal("0")

        if channel_count <= 200:
            return Decimal("130")
        elif channel_count <= 225:
            return Decimal("150")
        else:
            return Decimal("160")

    # 3. GET CHANNEL CHARGE BREAKDOWN
    def get_channel_charge_breakdown(self, connection):

        bouquet_channel_ids = set()
        charge_lines = []

        for bouquet_id in set(connection.bouquet_ids):

            bouquet = self.registration.get_bouquet(bouquet_id)

            if not bouquet:
                continue

            bouquet_channel_ids.update(bouquet.channel_ids)

            charge_lines.append({
                "type": "bouquet",
                "id": bouquet.bouquet_id,
                "name": bouquet.name,
                "amount": bouquet.price
            })

        individual_channel_ids = set(connection.channel_ids)
        uncovered_channels = individual_channel_ids - bouquet_channel_ids

        for channel_id in sorted(uncovered_channels):

            channel = self.registration.get_channel(channel_id)

            if not channel:
                continue

            charge_lines.append({
                "type": "channel",
                "id": channel.channel_id,
                "name": channel.name,
                "amount": channel.price
            })

        return charge_lines

    # 4. CALCULATE CHANNEL CHARGES
    def calculate_channel_charges(self, connection):

        charge_lines = self.get_channel_charge_breakdown(connection)

        return sum(
            (line["amount"] for line in charge_lines),
            start=Decimal("0")
        )

    # 5. CALCULATE CONNECTION PRICING
    def calculate_connection_pricing(self, connection, connection_no):

        selected_channels = self.get_selected_channels(connection)
        channel_count = len(selected_channels)

        ncf = self.calculate_ncf(channel_count)

        if connection_no == 1:
            applicable_ncf = ncf
        else:
            applicable_ncf = ncf * Decimal("0.40")

        charge_lines = self.get_channel_charge_breakdown(connection)

        channel_charges = sum(
            (line["amount"] for line in charge_lines),
            start=Decimal("0")
        )

        bouquet_channel_ids = set()

        for bouquet_id in connection.bouquet_ids:
            bouquet = self.registration.get_bouquet(bouquet_id)

            if bouquet:
                bouquet_channel_ids.update(bouquet.channel_ids)

        dropped_alacarte_count = len(
            set(connection.channel_ids) & bouquet_channel_ids
        )

        return {
            "connection_id": connection.connection_id,
            "unique_channel_count": channel_count,
            "selected_channel_ids": sorted(selected_channels),
            "ncf": applicable_ncf,
            "channel_charges": channel_charges,
            "charge_lines": charge_lines,
            "connection_bouquet_ids": connection.bouquet_ids,
            "dropped_alacarte_count": dropped_alacarte_count
        }

    # 6. CALCULATE SUBSCRIBER PRICING
    def calculate_subscriber_pricing(self, subscriber):

        connection_details = []

        total_ncf = Decimal("0")
        total_channel_charges = Decimal("0")

        for connection in subscriber.connections:

            result = self.calculate_connection_pricing(
                connection,
                subscriber.connection_no
            )

            connection_details.append(result)

            total_ncf += result["ncf"]
            total_channel_charges += result["channel_charges"]

        return {
            "subscriber_id": subscriber.subscriber_id,
            "subscriber_name": subscriber.name,
            "address_id": subscriber.address_id,
            "connection_no": subscriber.connection_no,
            "tenure_months": subscriber.tenure_months,
            "connections": connection_details,
            "total_ncf": total_ncf,
            "total_channel_charges": total_channel_charges
        }
