# Testing Guide
## Cable TV and DTH Channel Pack Pricing Engine

## 1. Project Testing Overview

The application is tested using:
- Automated unit tests with `pytest`.
- End-to-end execution using the supplied CSV input files.
- Validation of generated billing reports.
- Business rule and edge-case verification.

The automated test suite currently contains **30 test cases**.

---

## 2. Run Automated Tests

Run all test cases:

```bash
python -m pytest -v
```

Run pricing tests:

```bash
python -m pytest tests/test_pricing.py -v
```

Run registration tests:

```bash
python -m pytest tests/test_registration.py -v
```

Run billing tests:

```bash
python -m pytest tests/test_billing.py -v
```

### Test coverage

| Test module | What it verifies |
|---|---|
| `test_pricing.py` | NCF slabs, unique channel counting, second connection NCF, bouquet coverage and a-la-carte charges |
| `test_registration.py` | Channel, bouquet and subscriber registration, invalid references, duplicate selections and multi-TV identification |
| `test_billing.py` | Tenure discounts, GST, final amount rounding, FTA-only billing and CSV report generation |

**Latest test result:**

```text
30 passed
```

---

## 3. Run the Application Manually

Run the application from the project root directory:

```bash
python main.py
```

The application reads:

```text
data/commands.txt
```

The command file contains:

```text
LOAD_CHANNELS|channels.csv
LOAD_BOUQUETS|bouquets.csv
LOAD_SUBSCRIBERS|subscribers.csv
BILL_ALL|2026-10
```

The application resolves the input CSV files relative to the command file's directory.

You can also provide a different command file:

```bash
python main.py path/to/commands.txt
```

---

## 4. Expected Registration Results

When running with the supplied dataset, the expected registration results are:

| Item | Expected result |
|---|---:|
| Channels registered | 260 |
| Valid bouquets registered | 9 |
| Subscribers registered | 25 |
| Rejected bouquets | 1 |
| Registration errors | 3 |

**Important validation scenarios:**

- `BQ-07` is rejected because its price exceeds the combined a-la-carte price of its channels.
- The rejected bouquet reference in `SUB-013` is logged and ignored.
- The unknown channel `CH-999` in `SUB-014` is logged and ignored.
- Remaining valid selections are still processed and billed.

---

## 5. Business Rule Test Scenarios

### A. NCF boundary scenarios

| Scenario | Unique channels | Expected NCF |
|---|---:|---:|
| Empty selection | 0 | ₹0 |
| Minimum selection | 1 | ₹130 |
| Boundary | 200 | ₹130 |
| First channel above 200 | 201 | ₹150 |
| Upper boundary | 225 | ₹150 |
| First channel above 225 | 226 | ₹160 |
| Maximum sample scenario | 251 | ₹160 |

### B. Channel and bouquet scenarios

| Scenario | Expected behaviour |
|---|---|
| FTA-only selection | FTA channels count towards NCF; channel charge is ₹0 |
| Duplicate channel selection | Duplicate IDs are removed and counted once |
| Overlapping bouquets | Shared channels count once for NCF |
| Bouquet and individual channel overlap | Separate a-la-carte charge is removed |
| Bouquet price equals member channel total | Bouquet registration succeeds |
| Bouquet price exceeds member channel total | Bouquet registration is rejected |
| Unknown channel reference | Error is recorded and invalid channel is ignored |
| Rejected bouquet reference | Error is recorded and invalid bouquet is ignored |

### C. Multi-TV scenarios

| Scenario | Expected behaviour |
|---|---|
| First connection | Pays 100% of its NCF |
| Second connection | Pays 40% of its own NCF |
| Second connection channel charges | Remain 100% |
| Same household tenure | Primary connection tenure is applied to the household's connections |

### D. Discount and tax scenarios

| Scenario | Expected behaviour |
|---|---|
| 1–5 months | No discount |
| 6–11 months | 5% discount on channel charges |
| 12 months or more | 10% discount on channel charges |
| GST | 18% on NCF plus discounted channel charges |
| Final amount | Rounded to nearest rupee using `ROUND_HALF_UP` |

---

## 6. Verify Generated Reports

After successful execution, the application generates three CSV files inside the `output/` directory.

```text
output/
├── bill_lines.csv
├── bills.csv
└── errors.csv
```

### A. bill_lines.csv

Contains itemized billing information.

Expected line types:

- `NCF`
- `BOUQUET`
- `ALACARTE`
- `DISCOUNT`
- `GST`
- `TOTAL`

### B. bills.csv

Contains one summary row per subscriber connection.

It includes:

- Subscriber and address details.
- Connection number.
- Unique channel count.
- NCF and channel charges.
- Dropped a-la-carte count.
- Discount percentage and amount.
- Taxable amount.
- GST.
- Final bill amount.

Expected record count with the supplied dataset: **25 billing rows**.

### C. errors.csv

Contains validation errors with:

- Source file.
- Input line number.
- Item ID.
- Error reason.

Expected error count with the supplied dataset: **3 errors**.

---

## 7. Important Sample Results to Verify

| Subscriber | Scenario | Expected result |
|---|---|---|
| SUB-005 | Exactly 200 channels | NCF ₹130 |
| SUB-006 | 201 channels | NCF ₹150 |
| SUB-007 | 251 channels | NCF ₹160 |
| SUB-008 | FTA-only selection | NCF ₹130; channel charges ₹0 |
| SUB-009 | Bouquet and individual overlap | Duplicate a-la-carte charge removed |
| SUB-010 | First household connection | 100% NCF |
| SUB-011 | Second household connection | 40% NCF |
| SUB-013 | Rejected bouquet reference | Invalid bouquet ignored |
| SUB-014 | Unknown channel reference | Invalid channel ignored |
| SUB-015 | Duplicate channel selection | Channel counted once |
| SUB-016 | A-la-carte channels covered by bouquet | Separate charges removed |

---

## 8. Final Verification Checklist

Before submission, verify the following:

- [ ] All 30 automated tests pass.
- [ ] All 260 channels are registered.
- [ ] 9 valid bouquets are registered.
- [ ] All 25 subscribers are registered and billed.
- [ ] Invalid bouquet and channel references are logged.
- [ ] NCF boundaries are correct.
- [ ] Multi-TV NCF calculation is correct.
- [ ] Household tenure discount is applied correctly.
- [ ] GST is calculated at 18%.
- [ ] Final amounts use `ROUND_HALF_UP`.
- [ ] `bill_lines.csv` is generated correctly.
- [ ] `bills.csv` contains 25 billing rows.
- [ ] `errors.csv` contains the expected validation errors.

**Final commands:**

```bash
python -m pytest -v
python main.py
```

Both commands should complete successfully.