
from decimal import Decimal

from models.channel import Channel
from models.bouquet import Bouquet
from models.subscriber import Subscriber


class RegistrationService:

    def __init__(self):
        self.channels = {}
        self.bouquets = {}
        self.subscribers = {}
        self.errors = []

    def add_error(self, source, line_no, item_id, reason):
        self.errors.append({
            "source": source,
            "line_no": line_no,
            "item_id": item_id,
            "reason": reason
        })

    # ---------------------------
    # CHANNEL REGISTRATION
    # ---------------------------
    def register_channel(self, channel: Channel):

        if not channel.channel_id:
            raise ValueError("Channel ID cannot be empty")

        if channel.channel_id in self.channels:
            raise ValueError(
                f"Channel {channel.channel_id} already exists"
            )

        self.channels[channel.channel_id] = channel

    # ---------------------------
    # BOUQUET REGISTRATION
    # ---------------------------
    def register_bouquet(self, bouquet: Bouquet, line_no=None):

        try:
            if not bouquet.bouquet_id:
                raise ValueError("Bouquet ID cannot be empty")

            if bouquet.bouquet_id in self.bouquets:
                raise ValueError(
                    f"Bouquet {bouquet.bouquet_id} already exists"
                )

            if not bouquet.channel_ids:
                raise ValueError("Bouquet must contain at least one channel")

            if len(bouquet.channel_ids) != len(set(bouquet.channel_ids)):
                raise ValueError("Bouquet contains duplicate channels")

            for channel_id in bouquet.channel_ids:
                if channel_id not in self.channels:
                    raise ValueError(
                        f"Channel {channel_id} does not exist"
                    )

            individual_total = sum(
                (
                    self.channels[channel_id].price
                    for channel_id in bouquet.channel_ids
                ),
                start=Decimal("0")
            )

            if bouquet.price > individual_total:
                raise ValueError(
                    f"Bouquet price {bouquet.price} exceeds "
                    f"individual channel total {individual_total}"
                )

            self.bouquets[bouquet.bouquet_id] = bouquet
            return True

        except ValueError as error:
            self.add_error(
                source="bouquets.csv",
                line_no=line_no,
                item_id=bouquet.bouquet_id,
                reason=str(error)
            )
            return False

    # ---------------------------
    # SUBSCRIBER REGISTRATION
    # ---------------------------
    def register_subscriber(self, subscriber: Subscriber, line_no=None):

        if not subscriber.subscriber_id:
            raise ValueError("Subscriber ID cannot be empty")

        if subscriber.subscriber_id in self.subscribers:
            raise ValueError(
                f"Subscriber {subscriber.subscriber_id} already exists"
            )

        if not subscriber.connections:
            raise ValueError(
                "Subscriber must have at least one TV connection"
            )

        connection_ids = set()

        for connection in subscriber.connections:

            if not connection.connection_id:
                raise ValueError("Connection ID cannot be empty")

            if connection.connection_id in connection_ids:
                raise ValueError(
                    f"Duplicate connection ID: {connection.connection_id}"
                )

            connection_ids.add(connection.connection_id)

            # De-duplicate channel selections.
            connection.channel_ids = list(
                dict.fromkeys(connection.channel_ids)
            )

            # De-duplicate bouquet selections.
            connection.bouquet_ids = list(
                dict.fromkeys(connection.bouquet_ids)
            )

            # Keep only valid channel IDs.
            valid_channels = []

            for channel_id in connection.channel_ids:
                if channel_id in self.channels:
                    valid_channels.append(channel_id)
                else:
                    self.add_error(
                        source="subscribers.csv",
                        line_no=line_no,
                        item_id=channel_id,
                        reason="Unknown channel ID"
                    )

            connection.channel_ids = valid_channels

            # Keep only registered bouquet IDs.
            valid_bouquets = []

            for bouquet_id in connection.bouquet_ids:
                if bouquet_id in self.bouquets:
                    valid_bouquets.append(bouquet_id)
                else:
                    self.add_error(
                        source="subscribers.csv",
                        line_no=line_no,
                        item_id=bouquet_id,
                        reason="Unknown or rejected bouquet ID"
                    )

            connection.bouquet_ids = valid_bouquets

        self.subscribers[subscriber.subscriber_id] = subscriber

    # ---------------------------
    # GET METHODS
    # ---------------------------
    def get_channel(self, channel_id):
        return self.channels.get(channel_id)

    def get_bouquet(self, bouquet_id):
        return self.bouquets.get(bouquet_id)

    def get_subscriber(self, subscriber_id):
        return self.subscribers.get(subscriber_id)
