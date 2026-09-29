# Input data

The Vireo Audio take-home supplied customer-level operational files (tickets, agents, orders, customers, products and policy/email documents).

Those source files are **intentionally not committed to this public repository** because they contain customer/operational data supplied for the exercise.

To regenerate the checked-in reports locally, place the supplied `tickets.csv` and `agents.csv` files in this directory and run:

```bash
python analyze.py
```

The analysis also accepts the other supplied files remaining in the input pack, but the deterministic SLA calculation requires `tickets.csv` and `agents.csv`.

The checked-in `output/` directory contains the submission snapshot generated from the supplied dataset.
