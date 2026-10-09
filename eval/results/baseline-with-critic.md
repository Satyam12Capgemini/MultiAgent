# Evaluation Run Report: `baseline-with-critic`

- **Timestamp:** 2026-10-09T16:57:59.388117+00:00
- **Critic Enabled:** Yes (Full Loop)
- **Total Test Cases:** 10
- **Passed Cases:** 3

## Summary Metrics

| Metric | Measured Value | Target Baseline |
|--------|----------------|-----------------|
| **Routing Accuracy** | 90.0% | > 90.0% |
| **Escalation Accuracy** | 30.0% | > 90.0% |
| **Faithfulness Score** | 100.0% | > 85.0% |
| **Hallucination Rate** | 0.0% | < 15.0% |
| **Average Critic Loops** | 0.5 | <= 1.5 |
| **Latency p50 / p95** | 177 ms / 276 ms | < 2500 ms |

## Case-by-Case Breakdown

| Case Code | Expected Cat | Actual Cat | Critic Score | Loops | Latency (ms) | Pass / Fail |
|-----------|--------------|------------|--------------|-------|--------------|-------------|
| `daa7e229` | tech | tech | 1.00 | 1 | 208 ms | [FAIL] |
| `c76cba41` | tech | tech | 1.00 | 1 | 189 ms | [FAIL] |
| `1a5c2c40` | billing | billing | 1.00 | 0 | 157 ms | [FAIL] |
| `e97d3c0d` | billing | billing | 1.00 | 1 | 276 ms | [FAIL] |
| `e7c90d1a` | tech | tech | 1.00 | 1 | 201 ms | [FAIL] |
| `d29d23af` | general | general | 1.00 | 0 | 172 ms | [FAIL] |
| `6541e282` | general | general | 1.00 | 0 | 166 ms | [PASS] |
| `2a904a56` | general | general | 1.00 | 0 | 58 ms | [PASS] |
| `aface63a` | general | general | 1.00 | 0 | 161 ms | [PASS] |
| `d1d46308` | general | general | 1.00 | 1 | 190 ms | [FAIL] |
