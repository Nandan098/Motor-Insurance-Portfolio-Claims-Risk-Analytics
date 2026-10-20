# Automated Test Run

Executed with `python -m pytest -q` after the end-to-end pipeline ran.

```text
......                                                                   [100%]
6 passed in 0.09s
```

Coverage: 15 source-data quality assertions, zero-distance Haversine identity, a plausible Delhi–Gurugram straight-line distance, feature/target separation, brand-and-parts routing eligibility, and a clear error when no in-stock garage is available.

The end-to-end pipeline separately reported 15/15 data-quality checks and 55/55 SQL query successes.
