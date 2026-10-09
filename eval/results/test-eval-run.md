# Evaluation Run Report: `test-eval-run`

- **Timestamp:** 2026-10-09T17:49:24.151840+00:00
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
| **Latency p50 / p95** | 165 ms / 272 ms | < 2500 ms |

## Case-by-Case Breakdown

| Case Code | Expected Cat | Actual Cat | Critic Score | Loops | Latency (ms) | Pass / Fail |
|-----------|--------------|------------|--------------|-------|--------------|-------------|
| `e996b2f0` | tech | tech | 1.00 | 1 | 219 ms | [FAIL] |
| `220607fc` | tech | tech | 1.00 | 1 | 156 ms | [FAIL] |
| `37cb47b2` | billing | billing | 1.00 | 0 | 166 ms | [FAIL] |
| `0983dce2` | billing | billing | 1.00 | 1 | 272 ms | [FAIL] |
| `3534419a` | tech | tech | 1.00 | 1 | 172 ms | [FAIL] |
| `3107b8df` | general | general | 1.00 | 0 | 142 ms | [FAIL] |
| `e9d61727` | general | general | 1.00 | 0 | 147 ms | [PASS] |
| `8548c182` | general | general | 1.00 | 0 | 54 ms | [PASS] |
| `ac7fd592` | general | general | 1.00 | 0 | 146 ms | [PASS] |
| `a51569f0` | general | general | 1.00 | 1 | 183 ms | [FAIL] |
