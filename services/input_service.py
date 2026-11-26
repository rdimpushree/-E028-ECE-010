
import csv
from decimal import Decimal

from models.channel import Channel
from models.bouquet import Bouquet
from models.connection import Connection
from models.subscriber import Subscriber


class InputService:

    def _read_csv(self, file_path):
        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))

    def _parse_bool(self, value):
        value = value.strip().lower()

        if value == "true":
            return True
        if value == "false":
            return False

        raise ValueError(f"Invalid boolean value: {value}")

    def _parse_ids(self, value):
        value = value.strip()

        if not value or value.upper() == "NONE":
            return []

        return list(dict.fromkeys(
            item.strip() for item in value.split(";") if item.strip()
        ))

    def register_all(self, channels_file, bouquets_file,
                     subscribers_file, registration_service):

        # 1. Register channels first.
        channel_rows = self._read_csv(channels_file)

        for row in channel_rows:
            channel = Channel(
                channel_id=row["channel_id"].strip(),
                name=row["channel_name"].strip(),
                genre=row["genre"].strip(),
                is_hd=self._parse_bool(row["hd"]),
                is_fta=self._parse_bool(row["fta"]),
                price=Decimal(row["alacarte_price_rs"])
            )

            registration_service.register_channel(channel)

        # 2. Register bouquets after channels.
        bouquet_rows = self._read_csv(bouquets_file)

        for line_no, row in enumerate(bouquet_rows, start=2):
            bouquet = Bouquet(
                bouquet_id=row["bouquet_id"].strip(),
                name=row["bouquet_name"].strip(),
                channel_ids=self._parse_ids(row["channel_ids"]),
                price=Decimal(row["price_rs"])
            )

            registration_service.register_bouquet(
                bouquet,
                line_no=line_no
            )

        # 3. Register subscribers after bouquets.
        subscriber_rows = self._read_csv(subscribers_file)

        for line_no, row in enumerate(subscriber_rows, start=2):
            subscriber_id = row["subscriber_id"].strip()

            connection = Connection(
                connection_id=subscriber_id,
                channel_ids=self._parse_ids(row["channel_ids"]),
                bouquet_ids=self._parse_ids(row["bouquet_ids"])
            )

            subscriber = Subscriber(
                subscriber_id=subscriber_id,
                name=row["name"].strip(),
                tenure_months=int(row["tenure_months"]),
                connections=[connection],
                address_id=row["address_id"].strip(),
                connection_no=int(row["connection_no"])
            )

            registration_service.register_subscriber(
                subscriber,
                line_no=line_no
            )
    