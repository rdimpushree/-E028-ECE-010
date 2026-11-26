
import csv
import os

from decimal import Decimal, ROUND_HALF_UP


class BillingService:

    # --------------------------------
    # 1. FORMAT MONEY
    # --------------------------------
    def _money(self, amount):
        return format(
            amount.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            ),
            ".2f"
        )

    # --------------------------------
    # 2. CALCULATE FINAL BILL
    # --------------------------------
    def calculate_bill(self, pricing_details):

        total_ncf = pricing_details["total_ncf"]
        channel_charges = pricing_details["total_channel_charges"]
        tenure = pricing_details["tenure_months"]

        # Apply discount only on channel charges.
        discount_rate = Decimal("0")

        if tenure >= 12:
            discount_rate = Decimal("0.10")
        elif tenure >= 6:
            discount_rate = Decimal("0.05")

        discount = channel_charges * discount_rate
        discounted_channel_charges = channel_charges - discount

        # GST applies to NCF + discounted channel charges.
        taxable_amount = total_ncf + discounted_channel_charges
        gst = taxable_amount * Decimal("0.18")

        # Round final amount to nearest rupee.
        final_amount = (taxable_amount + gst).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )

        return {
            "ncf": total_ncf,
            "channel_charges": channel_charges,
            "discount_pct": int(discount_rate * 100),
            "discount": discount,
            "discounted_channel_charges": discounted_channel_charges,
            "taxable_amount": taxable_amount,
            "gst": gst,
            "final_amount": final_amount
        }

    # --------------------------------
    # 3. GENERATE BILL LINE ROWS
    # --------------------------------
    def _build_bill_lines(self, subscriber, pricing_details, bill):

        rows = []
        line_no = 1

        def add_line(line_type, item_id, description, amount):
            nonlocal line_no

            rows.append({
                "subscriber_id": subscriber.subscriber_id,
                "line_no": line_no,
                "line_type": line_type,
                "item_id": item_id,
                "description": description,
                "amount_rs": self._money(amount)
            })

            line_no += 1

        # NCF line.
        add_line(
            "NCF",
            "NCF",
            "Network Capacity Fee",
            bill["ncf"]
        )

        # Bouquet and a-la-carte lines.
        for connection in pricing_details["connections"]:

            for charge in connection["charge_lines"]:

                if charge["type"] == "bouquet":
                    add_line(
                        "BOUQUET",
                        charge["id"],
                        charge["name"],
                        charge["amount"]
                    )

                elif charge["type"] == "channel":
                    add_line(
                        "ALACARTE",
                        charge["id"],
                        charge["name"],
                        charge["amount"]
                    )

        # Discount line.
        add_line(
            "DISCOUNT",
            "DISCOUNT",
            f"Tenure discount ({bill['discount_pct']}%)",
            -bill["discount"]
        )

        # GST line.
        add_line(
            "GST",
            "GST",
            "GST (18%)",
            bill["gst"]
        )

        # Final total line.
        add_line(
            "TOTAL",
            "TOTAL",
            "Final bill amount",
            bill["final_amount"]
        )

        return rows

    # --------------------------------
    # 4. BUILD BILL SUMMARY ROW
    # --------------------------------
    def _build_bill_summary(self, subscriber, pricing_details, bill):

        dropped_count = sum(
            connection["dropped_alacarte_count"]
            for connection in pricing_details["connections"]
        )

        bouquet_total = sum(
            (
                line["amount"]
                for connection in pricing_details["connections"]
                for line in connection["charge_lines"]
                if line["type"] == "bouquet"
            ),
            start=Decimal("0")
        )

        alacarte_total = sum(
            (
                line["amount"]
                for connection in pricing_details["connections"]
                for line in connection["charge_lines"]
                if line["type"] == "channel"
            ),
            start=Decimal("0")
        )

        return {
            "subscriber_id": subscriber.subscriber_id,
            "address_id": subscriber.address_id,
            "connection_no": subscriber.connection_no,

            "channel_count": sum(
                connection["unique_channel_count"]
                for connection in pricing_details["connections"]
            ),

            "ncf_rs": self._money(bill["ncf"]),
            "bouquet_charge_rs": self._money(bouquet_total),
            "alacarte_charge_rs": self._money(alacarte_total),
            "dropped_alacarte_count": dropped_count,
            "discount_pct": bill["discount_pct"],
            "discount_rs": self._money(bill["discount"]),
            "taxable_rs": self._money(bill["taxable_amount"]),
            "gst_rs": self._money(bill["gst"]),
            "total_rs": self._money(bill["final_amount"])
        }

    # --------------------------------
    # 5. GENERATE ALL CSV REPORTS
    # --------------------------------
    def generate_csv_reports(self, billing_records, errors):

        os.makedirs("output", exist_ok=True)

        bill_line_fields = [
            "subscriber_id",
            "line_no",
            "line_type",
            "item_id",
            "description",
            "amount_rs"
        ]

        bill_fields = [
            "subscriber_id",
            "address_id",
            "connection_no",
            "channel_count",
            "ncf_rs",
            "bouquet_charge_rs",
            "alacarte_charge_rs",
            "dropped_alacarte_count",
            "discount_pct",
            "discount_rs",
            "taxable_rs",
            "gst_rs",
            "total_rs"
        ]

        error_fields = [
            "source",
            "line_no",
            "item_id",
            "reason"
        ]

        all_bill_lines = []
        all_bills = []

        for subscriber, pricing_details, bill in billing_records:

            # Build itemized bill lines.
            all_bill_lines.extend(
                self._build_bill_lines(
                    subscriber,
                    pricing_details,
                    bill
                )
            )

            # Build subscriber bill summary.
            all_bills.append(
                self._build_bill_summary(
                    subscriber,
                    pricing_details,
                    bill
                )
            )

        # Sort bill summaries by subscriber ID.
        all_bills.sort(
            key=lambda row: row["subscriber_id"]
        )

        # Generate bill_lines.csv.
        with open(
            "output/bill_lines.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=bill_line_fields
            )

            writer.writeheader()
            writer.writerows(all_bill_lines)

        # Generate bills.csv.
        with open(
            "output/bills.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=bill_fields
            )

            writer.writeheader()
            writer.writerows(all_bills)

        # Generate errors.csv.
        with open(
            "output/errors.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=error_fields
            )

            writer.writeheader()
            writer.writerows(errors)

        return {
            "bill_lines": "output/bill_lines.csv",
            "bills": "output/bills.csv",
            "errors": "output/errors.csv"
        }
