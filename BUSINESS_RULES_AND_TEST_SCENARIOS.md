# Cable TV / DTH Channel Pack Pricing Engine

**Project:** ECE-010 – Cable TV and DTH Channel Pack Pricing Engine  
**Implementation:** Python CLI Application  
**Input Format:** CSV  
**Output Format:** CSV  
**Testing:** Pytest – 30 test cases passed

---

## 1. What does this application do?

The application calculates monthly cable TV and DTH bills for subscribers based on:

- Channels selected individually (a-la-carte).
- Bouquets selected by the subscriber.
- Number of unique channels selected.
- Number of TV connections.
- Subscription tenure.
- Network Capacity Fee (NCF).
- Discounts and GST.

It reads channel, bouquet and subscriber information from CSV files, validates the input data, calculates bills and generates three CSV reports.

### Example

A subscriber selects:

- Star Sports: ₹20
- Sony Sports: ₹15
- Sports Bouquet: ₹30, containing both channels.

The system should not charge ₹20 + ₹15 + ₹30.

The individual channels are already included in the bouquet, so the channel charge is ₹30.

This is the kind of business logic our application handles.

### Input files

The application reads:

| File | Purpose |
|---|---|
| `channels.csv` | Channel details and individual prices |
| `bouquets.csv` | Bouquet details, prices and included channels |
| `subscribers.csv` | Subscriber, connection and channel selections |
| `commands.txt` | Commands defining input files and billing month |

### Output files

The application generates:

| File | Purpose |
|---|---|
| `bill_lines.csv` | Itemized billing details for every subscriber |
| `bills.csv` | One summarized billing record per connection |
| `errors.csv` | Invalid input references and validation errors |

---

## 2. Business rules and how we implement them

### BR-01: Network Capacity Fee (NCF)

NCF is calculated based on the number of unique channels selected by a connection.

| Unique channels | NCF |
|---|---:|
| 0 | ₹0 |
| 1–200 | ₹130 |
| 201–225 | ₹150 |
| 226 and above | ₹160 |

Important points:

- HD channels count as one channel entry.
- FTA channels also count towards the channel count.
- Duplicate channel selections must not increase the count.
- Channels included in bouquets also count towards the channel count.
- Channels selected individually and through bouquets are counted only once.

Example:

A subscriber selects:
- 100 individual channels.
- 50 channels through a bouquet.
- 10 channels that overlap between the individual selection and bouquet.

Unique channels = 100 + 50 - 10 = 140.

NCF = ₹130.

**Code responsible:**
- `PricingService.calculate_ncf()`
- `PricingService.get_selected_channels()`

### BR-02: Bouquet price validation

A bouquet cannot cost more than the combined individual prices of its channels.

Example:

| Channel | Individual price |
|---|---:|
| Channel A | ₹20 |
| Channel B | ₹15 |
| Channel C | ₹10 |
| Total | ₹45 |

- Bouquet price ₹40 → Valid.
- Bouquet price ₹45 → Valid.
- Bouquet price ₹46 → Invalid.

Why? A bouquet should not be more expensive than purchasing all its channels individually.

Invalid bouquets are rejected during registration and recorded in `errors.csv`.

**Code responsible:** `RegistrationService.register_bouquet()`.

### BR-03: No double billing for bouquet channels

If a subscriber selects a bouquet and also individually selects a channel already included in that bouquet, the individual channel charge is removed.

Example:

Subscriber selects:
- Sports Bouquet: ₹30 (contains A and B).
- Channel A individually: ₹20.
- Channel C individually: ₹10.

| Item | Charge |
|---|---:|
| Sports Bouquet | ₹30 |
| Channel A individually | ₹0 |
| Channel C individually | ₹10 |
| Total channel charges | ₹40 |

The subscriber pays ₹40 in channel charges, not ₹60.

**Code responsible:** `PricingService.get_channel_charge_breakdown()`.

### BR-04: Overlapping bouquets

Two bouquets can contain the same channel.

For NCF, a shared channel must be counted only once.

Example:

- Bouquet A contains channels 1, 2 and 3.
- Bouquet B contains channels 2, 3 and 4.

Unique channels = 4, not 6.

However, the current implementation charges the full price of both selected bouquets. It does not attempt to find the cheapest possible bouquet combination.

This distinction is important: unique channel counting and bouquet billing are separate calculations.

**Code responsible:**
- `PricingService.get_selected_channels()`
- `PricingService.get_channel_charge_breakdown()`

### BR-05: Multiple TV connections

If a household has multiple TV connections at the same address:

- First connection pays 100% of its NCF.
- Second connection pays 40% of its own NCF.
- Channel charges remain 100% for every connection.

Example:

| Details | TV 1 | TV 2 |
|---|---:|---:|
| Unique channels | 2 | 2 |
| Base NCF | ₹130 | ₹130 |
| Applicable NCF | ₹130 | ₹52 |
| Channel charges | ₹30 | ₹15 |

Total NCF = ₹130 + ₹52 = ₹182.

Total channel charges = ₹30 + ₹15 = ₹45.

The application identifies connections using the `connection_no` field, rather than relying on their position in a list.

**Code responsible:** `PricingService.calculate_connection_pricing()`.

### BR-06: Subscription tenure discount

Discount applies only to channel charges, not NCF.

| Subscription tenure | Discount |
|---|---:|
| 1–5 months | 0% |
| 6–11 months | 5% |
| 12 months or more | 10% |

Example:

Channel charges = ₹100.

For a 6-month subscription:

- Discount = ₹100 × 5% = ₹5.
- Discounted channel charges = ₹95.
- NCF remains unchanged.

**Important household rule:**

For multiple connections at the same address, the household tenure is determined using the primary connection (`connection_no = 1`).

The same tenure-based discount is applied to all connections at that address.

For example, if the primary connection has a tenure of 12 months, both the first and second connections receive a 10% discount on their respective channel charges.

**Code responsible:**
- `main.py` – household tenure identification.
- `BillingService.calculate_bill()` – discount calculation.

### BR-07: GST calculation

GST is 18% on the sum of:

- NCF.
- Discounted channel charges.

Formula:

GST = (NCF + Discounted Channel Charges) × 18%

Example:

- NCF = ₹130.
- Channel charges = ₹100.
- Discount = ₹5.
- Discounted charges = ₹95.

Taxable amount = ₹130 + ₹95 = ₹225.

GST = ₹225 × 18% = ₹40.50.

**Code responsible:** `BillingService.calculate_bill()`.

### BR-08: Final amount rounding

The final amount is rounded to the nearest rupee using Python's `ROUND_HALF_UP`.

| Calculated amount | Final amount |
|---|---:|
| ₹154.49 | ₹154 |
| ₹154.50 | ₹155 |
| ₹154.58 | ₹155 |

Other billing amounts are maintained and displayed with two decimal places.

**Code responsible:** `BillingService.calculate_bill()`.

### BR-09: Invalid input handling

The application validates channel, bouquet and subscriber references during registration.

Examples:

- A bouquet referencing an unknown channel is rejected.
- A bouquet whose price exceeds its individual channel total is rejected.
- A subscriber referencing an unknown channel receives an error entry.
- A subscriber referencing a rejected or unknown bouquet receives an error entry.
- Invalid subscriber selections are ignored while the remaining valid selections are processed.
- Duplicate channel selections are deduplicated rather than billed multiple times.

All validation errors are recorded in `errors.csv`.

**Code responsible:**
- `RegistrationService.register_channel()`
- `RegistrationService.register_bouquet()`
- `RegistrationService.register_subscriber()`

---

## 3. Complete billing calculation flow

This is the order in which our application calculates a subscriber's bill.

1. **Read commands and CSV input files**
   - Load channels, bouquets and subscribers.

2. **Register and validate data**
   - Check IDs, channel references, bouquet prices and subscriber selections.

3. **Identify household tenure**
   - Find the primary connection for each address.
   - Use its tenure for all connections belonging to that household.

4. **Calculate unique channels**
   - Combine individual and bouquet channels.
   - Remove duplicates.

5. **Calculate NCF**
   - Apply the NCF slab.
   - Apply the additional-connection rule.

6. **Calculate channel charges**
   - Add selected bouquet prices.
   - Add uncovered individual channel prices.
   - Avoid double billing.

7. **Apply tenure discount**
   - Apply the appropriate discount to channel charges only.

8. **Calculate GST and final amount**
   - Add 18% GST on the taxable amount.
   - Round the final amount to the nearest rupee.

9. **Generate CSV reports**
   - Generate itemized bills.
   - Generate summarized bills.
   - Generate validation error reports.

---

## 4. How to run the application

Run commands from the project root directory.

### Step 1: Activate virtual environment

Windows PowerShell:

```bash
venv\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Execute the application

```bash
python main.py
```

The application reads commands from:

`data/commands.txt`

Example:

```text
LOAD_CHANNELS|channels.csv
LOAD_BOUQUETS|bouquets.csv
LOAD_SUBSCRIBERS|subscribers.csv
BILL_ALL|2026-10
```

### Step 4: Check generated reports

After successful execution, check:

```text
output/
    bill_lines.csv
    bills.csv
    errors.csv
```

---

## 5. Testing and verification

The application is tested using Pytest.

Run all tests:

```bash
pytest -v
```

### Automated test coverage

| Test file | Coverage |
|---|---|
| `test_pricing.py` | NCF slabs, first and second connection NCF, duplicate channels, bouquet overlaps |
| `test_registration.py` | Channel, bouquet and subscriber registration, invalid references and duplicate selections |
| `test_billing.py` | Tenure discounts, GST, rounding, FTA-only bills and CSV report generation |

### NCF boundary test cases

| Channels | Expected NCF | Result |
|---:|---:|---|
| 0 | ₹0 | Passed |
| 1 | ₹130 | Passed |
| 200 | ₹130 | Passed |
| 201 | ₹150 | Passed |
| 225 | ₹150 | Passed |
| 226 | ₹160 | Passed |
| 251 | ₹160 | Passed |

### Other verified scenarios

- First connection pays full NCF.
- Second connection pays 40% NCF.
- Second connection retains full channel charges.
- Duplicate channel selections are counted once.
- Bouquet-covered a-la-carte channels are not charged again.
- Invalid bouquets are rejected.
- Invalid subscriber references are logged.
- Six-month tenure discount is calculated correctly.
- Twelve-month tenure discount is calculated correctly.
- Short-tenure subscribers receive no discount.
- FTA-only connections receive NCF but no channel charges.
- GST is calculated correctly.
- Final amount uses half-up rounding.
- CSV reports are generated with the required columns.

### Latest test execution result

**30 test cases passed.**

```text
============================= 30 passed =============================
```

No test failures were reported in the latest execution.

---

## 6. Latest end-to-end execution result

The application was executed successfully using the supplied ECE-010 input files.

| Metric | Result |
|---|---:|
| Channels registered | 260 |
| Valid bouquets registered | 9 |
| Subscribers registered | 25 |
| Subscribers billed | 25 |
| Registration errors | 3 |
| Reports generated | 3 |

The three registration errors are expected:

1. BQ-07 rejected because its price exceeds the sum of its individual channel prices.
2. SUB-013 references the rejected BQ-07 bouquet.
3. SUB-014 references unknown channel CH-999.

All three reports were generated successfully.

**Final execution status: SUCCESSFUL**

---

## 7. Project structure

```text
cable-tv-pricing-engine/
│
├── main.py
├── requirements.txt
│
├── models/
│   ├── __init__.py
│   ├── channel.py
│   ├── bouquet.py
│   ├── subscriber.py
│   └── connection.py
│
├── services/
│   ├── __init__.py
│   ├── input_service.py
│   ├── registration_service.py
│   ├── pricing_service.py
│   └── billing_service.py
│
├── data/
│   ├── channels.csv
│   ├── bouquets.csv
│   ├── subscribers.csv
│   └── commands.txt
│
├── output/
│   ├── bill_lines.csv
│   ├── bills.csv
│   └── errors.csv
│
└── tests/
    ├── test_pricing.py
    ├── test_registration.py
    └── test_billing.py
```

---

## 8. Conclusion

The Cable TV / DTH Channel Pack Pricing Engine is a Python CLI application that processes subscriber selections, validates channel and bouquet data, calculates connection-level charges and generates monthly billing reports.

It handles important real-world billing scenarios such as overlapping bouquets, duplicate channels, multiple TV connections, household tenure discounts, NCF slabs, GST and invalid input references.

The latest implementation completed end-to-end execution successfully, generated all three required CSV reports and passed all 30 automated test cases.