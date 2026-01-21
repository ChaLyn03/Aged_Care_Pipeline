# Tests Overview

## Philosophy

The test suite focuses on behavior and data integrity, not just execution.
Coverage is layered to catch issues early and keep the end-to-end pipeline
trustworthy.

- Unit tests validate parser field extraction, writer output shape, and utility
  behavior with controlled inputs.
- Integration tests exercise scraper/service interactions with real or
  representative responses.
- End-to-end tests run the full CLI pipeline on a small sample to confirm
  orchestration, file outputs, and basic completeness checks.

## What Good Tests Look Like Here

- Assertions explain intent (e.g., specific fields extracted or rows written).
- Edge cases are covered (missing fields, empty responses, schema changes).
- Tests remain deterministic and avoid live external dependencies when possible.

## Running Tests

```bash
pytest -q
```

## Future Improvements

- Add coverage reporting thresholds and surface them in CI.
- Expand schema-drift tests to detect breaking upstream changes.
- Add contract-style fixtures for known API response shapes.
