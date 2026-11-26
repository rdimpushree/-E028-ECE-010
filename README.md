# Cable TV and DTH Channel Pack Pricing Engine

A command-line Python application that calculates a subscriber's monthly cable/DTH bill from selected a-la-carte channels and bouquets.

## Requirements
- Python 3.10+
- pytest

## Setup
```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```
Ensure `pytest` is listed in `requirements.txt`.

## Run
Default input:
```bash
python main.py
```
Specific scenario:
```bash
python main.py data/test_scenarios/multi_tv.json
```

## Run the complete test suite
```bash
python -m pytest -v
```

## Project structure
```text
cable-tv-pricing-engine/
├── main.py
├── models/
├── services/
├── data/
│   └── test_scenarios/
├── tests/
├── output/
├── README.md
├── BUSINESS_RULES_AND_TEST_SCENARIOS.md
├── TESTING_GUIDE.md
└── DECISION_LOG.md
```

## Business rules summary
- NCF is ₹130 for up to 200 unique channels; each additional block of up to 25 adds ₹20; maximum NCF is ₹160.
- FTA channels count towards NCF. Each distinct HD channel counts as one channel.
- Duplicate channel coverage is counted once for NCF.
- A bouquet priced above the sum of its channels' a-la-carte prices is rejected; equality is allowed.
- An individually selected channel already included in a selected bouquet is not charged separately.
- First TV connection pays 100% NCF; second and later connections pay 40% NCF. Channel charges remain 100%.
- 6-month tenure receives 5% discount; 12-month tenure receives 10% discount on channel charges only.
- GST is 18% on NCF plus discounted channel charges.
- Final amount is rounded to the nearest rupee using `ROUND_HALF_UP`.

## Output
Itemized bills are generated under `output/` as `<subscriber_id>_bill.txt`.

## Notes
The application is command-file driven, has no UI, and uses in-memory data during execution.
