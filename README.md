# Cable TV and DTH Channel Pack Pricing Engine

A command-line Python application that calculates monthly Cable TV/DTH bills based on subscribers' selected a-la-carte channels and bouquets.

The application validates input data, applies business rules, calculates NCF, channel charges, tenure discounts and GST, and generates itemized billing reports in CSV format.

## Team
- R DIMPUSHREE 
- SAFIYA FATIMA
- Section ECM B


## Requirements

- Python 3.10+
- pytest

## Project Setup

Clone the repository:

```bash
git clone https://github.com/rdimpushree/-E028-ECE-010.git
cd -E028-ECE-010
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Input Files

The application reads input data from CSV files stored in the `data/` directory.

| File | Description |
|---|---|
| `channels.csv` | Channel master data, including prices, genres, HD and FTA details |
| `bouquets.csv` | Bouquet definitions and their channel memberships |
| `subscribers.csv` | Subscriber details, connection information, selected channels, bouquets and tenure |
| `commands.txt` | Defines the input loading and billing execution sequence |

## Run the Application

Execute the application using:

```bash
python main.py
```

The application reads commands from `data/commands.txt` by default.

The command file specifies the input loading sequence and billing month:

```text
LOAD_CHANNELS|channels.csv
LOAD_BOUQUETS|bouquets.csv
LOAD_SUBSCRIBERS|subscribers.csv
BILL_ALL|2026-10
```

Alternatively, provide a custom command file:

```bash
python main.py path/to/commands.txt
```

## Business Rules Summary

- NCF is ₹130 for 1–200 unique channels.
- NCF is ₹150 for 201–225 unique channels.
- NCF is ₹160 for 226 or more unique channels.
- FTA channels count towards NCF but have zero channel charges.
- Each distinct HD channel counts as one channel.
- Duplicate channel selections are deduplicated and counted only once.
- A bouquet priced above the sum of its member channels' a-la-carte prices is rejected. Equality is allowed.
- An individually selected channel already included in a selected bouquet is not charged separately.
- The second TV connection pays 40% of its own NCF. Channel charges remain unchanged.
- A 6-month tenure receives a 5% discount, while a 12-month or longer tenure receives a 10% discount.
- Tenure discounts apply only to channel charges, not NCF.
- GST is 18% on NCF plus discounted channel charges.
- Final bill amounts are rounded to the nearest rupee using `ROUND_HALF_UP`.

## Generated Output

The application generates three CSV reports inside the `output/` directory.

| File | Description |
|---|---|
| `bills.csv` | One summary billing record per subscriber connection |
| `bill_lines.csv` | Itemized billing details, including NCF, bouquets, a-la-carte charges, discounts, GST and total |
| `errors.csv` | Invalid input references and rejected records with their reasons |

## Run Tests

Execute the complete test suite:

```bash
python -m pytest -v
```

The test suite covers pricing calculations, NCF slabs, bouquet validation, duplicate selections, multi-TV billing, discounts, GST, rounding and CSV report generation.

## Project Structure

```text
cable-tv-pricing-engine/
├── main.py
├── models/
│   ├── channel.py
│   ├── bouquet.py
│   ├── subscriber.py
│   └── connection.py
├── services/
│   ├── input_service.py
│   ├── registration_service.py
│   ├── pricing_service.py
│   └── billing_service.py
├── data/
│   ├── channels.csv
│   ├── bouquets.csv
│   ├── subscribers.csv
│   └── commands.txt
├── tests/
│   ├── test_pricing.py
│   ├── test_registration.py
│   └── test_billing.py
├── output/
├── requirements.txt
├── README.md
├── BUSINESS_RULES_AND_TEST_SCENARIOS.md
├── TESTING_GUIDE.md
└── DECISION_LOG.md
```

## Implementation Notes

- Command-file-driven CLI application with no graphical user interface.
- Uses Python dataclasses to represent application entities.
- Uses in-memory dictionaries for data storage during execution.
- Uses Python `Decimal` for accurate financial calculations.
- Separates input handling, registration, pricing and billing into service modules.
- Uses pytest for automated testing.
