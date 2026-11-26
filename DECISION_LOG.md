# Decision Log

1. **Python 3.10+** — selected because it is compatible with the project requirements and supports the language features used in the application.

2. **Command-line interface** — followed the requirement for a command-file-driven application without a graphical user interface.

3. **CSV input files** — selected CSV files for channels, bouquets and subscribers to provide a structured and easy-to-maintain input format.

4. **Command-file-driven execution** — used `commands.txt` to specify input files and the billing month, allowing the application to execute the required operations in sequence.

5. **In-memory dictionaries** — used dictionaries for channel, bouquet and subscriber registration to enable efficient ID-based lookup without introducing a database.

6. **Dataclasses for models** — represented Channel, Bouquet, Connection and Subscriber as data-focused objects.

7. **Decimal for money** — avoided binary floating-point precision problems in billing calculations.

8. **Channels registered first** — bouquets refer to channel IDs, so channels must exist before bouquet validation.

9. **Bouquets registered before subscribers** — subscriber selections refer to bouquet IDs, so bouquets must be validated before subscriber registration.

10. **Sets for unique channel counting** — prevented duplicate channel coverage from increasing the NCF channel count.

11. **Duplicate subscriber channel handling** — deduplicated repeated channel selections instead of rejecting the subscriber.

12. **FTA channels included in NCF count** — followed the explicit NCF rule that free-to-air channels also contribute to the unique channel count.

13. **Bouquet price validation** — rejected a bouquet priced above the sum of its member channels' a-la-carte prices. Exact price equality is accepted.

14. **No double billing** — removed an individual channel charge when that channel was already covered by a selected bouquet.

15. **Overlapping bouquet handling** — counted shared channels only once for NCF calculation while charging the full price of each selected valid bouquet.

16. **NCF slabs and cap** — implemented ₹130 for 1–200 channels, ₹150 for 201–225 channels and ₹160 for 226 or more channels. Zero selected channels results in zero NCF.

17. **Multi-TV NCF** — applied full NCF to the first connection and 40% of the respective NCF to the second connection. Channel charges remain 100% for every connection.

18. **Explicit connection identification** — used `connection_no` to distinguish primary and second connections rather than relying on the position of a connection in a list.

19. **Household-level tenure** — used the tenure of the primary connection (`connection_no = 1`) for all connections sharing the same address. This ensures consistent tenure discounts across a household.

20. **Tenure discount scope** — applied 5% for 6–11 months and 10% for 12 or more months to channel charges only, never to NCF.

21. **GST base** — calculated 18% GST on NCF plus discounted channel charges.

22. **Final rounding** — used Decimal with `ROUND_HALF_UP` to round the final bill amount to the nearest rupee while retaining two decimal places for other monetary values.

23. **Invalid input handling** — rejected invalid bouquets and logged invalid subscriber channel or bouquet references in `errors.csv`. Remaining valid subscriber selections are still processed.

24. **CSV billing reports** — generated three separate output files:
    - `bill_lines.csv` for itemized billing details.
    - `bills.csv` for summarized billing details.
    - `errors.csv` for registration and validation errors.

25. **Pytest** — selected pytest to provide automated testing through a single command. The current test suite contains 30 passing test cases.

26. **No global bouquet optimizer** — the current logic charges every selected valid bouquet and removes covered a-la-carte channel charges. It does not search all possible bouquet combinations to find the cheapest total. Automatic bouquet optimization is outside the current implementation scope.