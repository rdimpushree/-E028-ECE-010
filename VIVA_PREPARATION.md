# Cable TV & DTH Channel Pack Pricing Engine
## Viva Preparation — Questions and Simple Answers

Use this as a speaking guide. Understand the reasoning behind each answer rather than memorising every sentence.

---

# 1. Project Overview

### Q1. What is your project?

**Answer:**

It is a Python command-line Cable TV and DTH Channel Pack Pricing Engine.

It reads channel, bouquet and subscriber information from CSV files, calculates monthly bills based on the selected channels and TV connections, and generates three billing reports:

- bill_lines.csv
- bills.csv
- errors.csv

### Q2. What problem does it solve?

**Answer:**

It automates monthly cable TV billing based on selected a-la-carte channels, bouquets, number of TV connections and subscription tenure.

It applies NCF, discounts and GST according to the specified business rules.

### Q3. Why did you choose Python?

**Answer:**

Python 3.10+ is allowed by the problem statement. It provides simple data modelling, CSV handling, Decimal arithmetic and pytest support, which are suitable for this CLI application.

### Q4. Why is there no database or UI?

**Answer:**

The requirement describes a command-file-driven application without a graphical UI.

The input data is loaded from CSV files and stored in memory using dictionaries while the program runs, so a database is not necessary for this scope.

### Q5. Explain the execution flow.

**Answer:**

1. Read commands from commands.txt.
2. Load channel, bouquet and subscriber CSV files.
3. Register channels.
4. Register bouquets and validate their channel references and prices.
5. Register subscribers and validate their selections.
6. Identify household tenure using the primary connection.
7. Calculate unique channels, NCF and channel charges for each connection.
8. Apply tenure discounts.
9. Calculate GST and round the final amount.
10. Generate three CSV reports.

---

# 2. Architecture and Python Concepts

### Q6. What are the main classes or services?

**Answer:**

- Channel, Bouquet, Connection and Subscriber are the domain models.
- InputService reads CSV files and creates model objects.
- RegistrationService stores and validates registered entities.
- PricingService calculates unique channels, NCF and channel charges.
- BillingService applies discounts, calculates GST and generates CSV reports.
- main.py coordinates the application flow and household tenure calculation.

### Q7. Why did you use dictionaries in RegistrationService?

**Answer:**

Channels, bouquets and subscribers are stored in dictionaries using their IDs as keys.

This makes it easy to check whether an ID exists and retrieve an entity by ID.

For example, instead of searching through all channels, we can directly access a channel using its channel ID.

### Q8. Why did you use sets?

**Answer:**

A set stores unique values.

If a channel is selected individually and also appears in a bouquet, it should count only once for NCF.

Sets make duplicate removal straightforward.

### Q9. What is a dataclass and why did you use it?

**Answer:**

A dataclass is a Python feature for defining classes that mainly hold data.

It automatically provides methods such as an initializer, reducing repetitive code in the models.

### Q10. Why use separate services?

**Answer:**

Each service has one main responsibility.

Input loading, registration, pricing and billing are separated, which makes the code easier to understand, test and maintain.

### Q11. Why register channels before bouquets and subscribers?

**Answer:**

A bouquet refers to channel IDs, so those channels must already exist before validating the bouquet.

Subscribers can refer to both channels and bouquets, so they are registered after both.

### Q12. What is the purpose of main.py?

**Answer:**

main.py acts as the entry point of the application.

It reads the command file, initializes the services, coordinates registration, identifies household tenure, calculates bills and generates the reports.

---

# 3. NCF and Channel Counting

### Q13. What is NCF?

**Answer:**

NCF means Network Capacity Fee.

In this project, it is a monthly fee based on the number of unique channels selected by a TV connection.

### Q14. Explain the NCF slabs.

**Answer:**

| Unique channels | NCF |
|---|---:|
| 0 | ₹0 |
| 1–200 | ₹130 |
| 201–225 | ₹150 |
| 226 and above | ₹160 |

The maximum NCF is ₹160.

### Q15. What happens at exactly 200 channels?

**Answer:**

The NCF is ₹130 because 200 is included in the first slab.

### Q16. What happens at 201 channels?

**Answer:**

The NCF becomes ₹150 because one channel has entered the next slab.

### Q17. What happens at 225 and 226 channels?

**Answer:**

At 225 channels, NCF is ₹150.

At 226 channels, it becomes ₹160.

### Q18. Do FTA channels count towards NCF?

**Answer:**

Yes. FTA channels are included in the channel count.

Their individual a-la-carte price is zero, but they still contribute to NCF.

### Q19. How are HD channels counted?

**Answer:**

Each selected channel entry counts as one channel, whether it is SD or HD.

In the current implementation, distinct channel IDs for SD and HD variants count as two distinct channels.

### Q20. How do you avoid counting the same channel twice?

**Answer:**

The pricing service creates a set of selected channel IDs.

It adds individually selected channels and all channels contained in selected bouquets.

Since a set only keeps unique IDs, overlapping coverage is counted once.

**Code:** PricingService.get_selected_channels().

---

# 4. Bouquet and A-la-carte Pricing

### Q21. What is a bouquet?

**Answer:**

A bouquet is a pack containing multiple channels that is sold at one package price.

### Q22. How do you validate a bouquet price?

**Answer:**

During registration, the application adds the a-la-carte prices of all channels in the bouquet.

If the bouquet price is greater than that sum, registration is rejected.

If the prices are equal, it is accepted.

### Q23. What happens if a bouquet costs more than its individual channels combined?

**Answer:**

The application rejects that bouquet during registration and records the validation error in errors.csv.

### Q24. Explain the no-double-billing rule.

**Answer:**

The application collects the channel IDs contained in all selected bouquets.

It then subtracts those IDs from the individually selected channel IDs.

Only the remaining uncovered individual channels are charged separately.

**Code:** PricingService.get_channel_charge_breakdown().

### Q25. Give an example of no double billing.

**Answer:**

Suppose a Sports Pack costs ₹30 and contains Channel A and Channel B.

The subscriber selects the pack and also selects Channel A individually.

The bill charges ₹30 for the pack, not an additional price for Channel A.

### Q26. What if two selected bouquets contain the same channel?

**Answer:**

The channel is counted once for NCF because unique channel IDs are stored in a set.

However, the current implementation still charges the full price of each selected valid bouquet.

### Q27. Does the application automatically find the cheapest combination of bouquets?

**Answer:**

No.

The current implementation charges the selected bouquets and removes separate a-la-carte charges for channels covered by those bouquets.

It does not search all possible bouquet combinations to find the globally cheapest selection.

---

# 5. Multiple TV Connections

### Q28. Explain the multi-TV rule.

**Answer:**

The first TV connection pays 100% of its NCF.

The second connection pays 40% of its respective NCF.

Channel charges for every connection remain 100%.

### Q29. Give a multi-TV calculation example.

**Answer:**

Suppose both connections have two unique channels, so each has a base NCF of ₹130.

- TV 1 NCF = ₹130.
- TV 2 NCF = ₹130 × 40% = ₹52.
- Total NCF = ₹182.

Each TV's selected channel charges are added at their full amount.

### Q30. How does the code identify the first and second connections?

**Answer:**

The application uses the explicit connection_no field.

- connection_no = 1 means the primary connection.
- connection_no = 2 means the second connection.

The pricing service uses this field to decide whether full NCF or 40% NCF should be applied.

### Q31. Does the 40% rule reduce channel charges too?

**Answer:**

No. It applies only to NCF.

Channel charges remain 100% for each connection's own selections.

### Q32. How are household connections identified?

**Answer:**

The application uses address_id to group connections belonging to the same household.

The primary connection is identified using connection_no = 1.

The primary connection's tenure is then used for all connections sharing that address.

---

# 6. Tenure Discount, GST and Rounding

### Q33. Explain the tenure discount.

**Answer:**

| Tenure | Discount |
|---|---:|
| 1–5 months | 0% |
| 6–11 months | 5% |
| 12 months or more | 10% |

The discount is applied only to channel charges, not NCF.

### Q34. How is tenure handled for multiple TV connections?

**Answer:**

The primary connection determines the household tenure.

For example, if the primary connection has a tenure of 12 months, both connections at the same address receive a 10% discount on their respective channel charges.

This logic is implemented in main.py using address_id and connection_no.

### Q35. Why is NCF not discounted?

**Answer:**

Because the business rule explicitly says NCF is never discounted.

The discount is applied only to channel charges.

### Q36. How is GST calculated?

**Answer:**

First, the tenure discount is subtracted from channel charges.

GST is then calculated at 18% on NCF plus discounted channel charges.

**Formula:**

GST = (NCF + discounted channel charges) × 18%

### Q37. Why do you use Decimal instead of float?

**Answer:**

Money calculations need predictable decimal precision.

Binary floating-point values can represent some decimal amounts imprecisely.

Decimal avoids that issue in financial calculations.

### Q38. What is ROUND_HALF_UP?

**Answer:**

It rounds to the nearest integer rupee, with an exact half rounded upwards.

For example, ₹154.50 becomes ₹155.

### Q39. Give a complete billing example.

**Answer:**

Suppose:

- NCF = ₹130
- Channel charges = ₹100
- Tenure = 6 months

Calculation:

- Discount = ₹100 × 5% = ₹5.
- Discounted channel charges = ₹95.
- Taxable amount = ₹130 + ₹95 = ₹225.
- GST = ₹225 × 18% = ₹40.50.
- Total = ₹265.50.
- Final amount = ₹266.

---

# 7. Input, Output and Error Handling

### Q40. What is the input format?

**Answer:**

The application uses three CSV files:

- channels.csv contains channel details.
- bouquets.csv contains bouquet details and channel IDs.
- subscribers.csv contains subscriber, address, connection, channel selection and tenure details.

A separate commands.txt file specifies which files to load and the billing month.

### Q41. How do you run the application?

**Answer:**

From the project root directory:

```bash
python main.py
```

The application reads data/commands.txt by default.

A different command file can also be provided:

```bash
python main.py path/to/commands.txt
```

### Q42. What does commands.txt contain?

**Answer:**

It contains commands that tell the application which input files to load and when to execute billing.

Example:

```text
LOAD_CHANNELS|channels.csv
LOAD_BOUQUETS|bouquets.csv
LOAD_SUBSCRIBERS|subscribers.csv
BILL_ALL|2026-10
```

### Q43. Where are the billing reports generated?

**Answer:**

The application creates an output directory if it does not exist.

It generates three files:

- output/bill_lines.csv
- output/bills.csv
- output/errors.csv

### Q44. What is the difference between bills.csv and bill_lines.csv?

**Answer:**

bills.csv contains one summary record per subscriber connection.

bill_lines.csv contains the itemized charges such as NCF, bouquet charges, a-la-carte charges, discount, GST and final total.

### Q45. What is errors.csv used for?

**Answer:**

It records invalid input references and validation errors.

For example, an invalid bouquet or unknown channel reference is recorded with the source file, line number, item ID and reason.

### Q46. What happens if an input file does not exist?

**Answer:**

The application checks whether each input file exists before registration.

If a file is missing, it raises a clear error and exits with a non-zero status code.

### Q47. What happens if a subscriber references an unknown channel?

**Answer:**

The application records an error in errors.csv and ignores that invalid channel selection.

The remaining valid channel and bouquet selections are still processed.

### Q48. How are errors displayed in the CLI?

**Answer:**

The main() function catches selected expected exceptions, prints an error message to standard error and exits with a non-zero status code.

---

# 8. Testing

### Q49. Which testing framework did you use?

**Answer:**

I used pytest because it is simple to write and run Python tests.

It automatically discovers test functions and reports passed or failed cases.

### Q50. How do you run all tests?

**Answer:**

```bash
python -m pytest -v
```

### Q51. What does a pytest fixture do?

**Answer:**

A fixture prepares reusable test data or objects.

For example, the setup_pricing fixture creates a RegistrationService, registers sample channels and bouquets, and returns a PricingService for tests to use.

### Q52. What does assert do in a test?

**Answer:**

It checks whether an expected condition is true.

If the condition is false, pytest reports the test as failed.

### Q53. How many automated tests have passed?

**Answer:**

The current project has 30 automated test cases, and all 30 passed in the latest test execution.

### Q54. Which important scenarios have you tested?

**Answer:**

- NCF boundaries at 0, 1, 200, 201, 225, 226 and 251 channels.
- FTA channel counting.
- Bouquet channel counting.
- Duplicate channel selection.
- No double billing.
- Second connection NCF.
- Full channel charges on second connections.
- Household tenure discount.
- GST calculation.
- Final amount rounding.
- Invalid bouquet rejection.
- Unknown subscriber channel and bouquet references.
- CSV report generation.

### Q55. Why test boundary values?

**Answer:**

Business rules often change at thresholds.

Testing values immediately before, at and after a threshold helps catch off-by-one errors.

For example, 200 and 201 channels must produce different NCF values.

---

# 9. Important Limitations and Honest Answers

### Q56. Does the current code optimize the cheapest bouquet combination?

**Answer:**

No.

It charges the selected bouquets and removes a-la-carte charges for channels covered by those bouquets.

A global cheapest-combination optimizer is not implemented.

### Q57. Are connections grouped by address?

**Answer:**

Yes.

The application uses address_id to identify household connections.

It finds the primary connection using connection_no = 1 and uses its tenure for all connections sharing that address.

### Q58. Are duplicate channel selections rejected?

**Answer:**

No.

The registration service deduplicates repeated channel IDs in a subscriber's selections.

The channel is counted and billed only once.

### Q59. Are overlapping bouquets allowed?

**Answer:**

Yes.

Their shared channels count once for NCF.

However, the full price of each selected valid bouquet is still charged.

### Q60. What would you improve if you had more time?

**Answer:**

I would clarify the cheapest-coverage interpretation with the client, add automatic bouquet optimization if required, strengthen validation for malformed CSV data and add more end-to-end tests against exact expected bill files.

---

# 10. Five-Minute Demo Checklist

Use this order when recording your demo:

| Time | Demonstration |
|---|---|
| 0:00–0:40 | Introduce the project and architecture |
| 0:40–1:20 | Show channels.csv, bouquets.csv and subscribers.csv |
| 1:20–2:00 | Show commands.txt and explain command execution |
| 2:00–2:40 | Run python main.py |
| 2:40–3:20 | Show bills.csv and explain an NCF / discount calculation |
| 3:20–4:00 | Show bill_lines.csv and errors.csv |
| 4:00–4:30 | Explain multi-TV and household tenure handling |
| 4:30–5:00 | Run python -m pytest -v and show 30 passed |

---

# Final Viva Advice

1. Explain the business rule first, then point to the method that implements it.
2. Use a small numerical example whenever possible.
3. Be clear about the difference between unique channel counting and bouquet billing.
4. Explain why NCF, channel discount and GST are calculated in that order.
5. If a feature is not implemented, say so honestly and explain the current behaviour.
6. Be ready to explain sets, dictionaries, Decimal, dataclasses, fixtures and assertions.
7. Understand how address_id and connection_no work together for household billing.

**Most important concept to understand:**

A channel can be covered by multiple selections, but it should count only once for NCF. An individually selected channel already covered by a selected bouquet must not be charged again.

Also remember that the second connection gets 40% of its own NCF, while its channel charges remain unchanged.