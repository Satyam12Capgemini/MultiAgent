# Evaluation Run Report: `baseline-no-critic`

- **Timestamp:** 2026-10-09T16:58:05.978783+00:00
- **Critic Enabled:** No (Baseline Single-Pass)
- **Total Test Cases:** 10
- **Passed Cases:** 3

## Summary Metrics

| Metric | Measured Value | Target Baseline |
|--------|----------------|-----------------|
| **Routing Accuracy** | 90.0% | > 90.0% |
| **Escalation Accuracy** | 30.0% | > 90.0% |
| **Faithfulness Score** | 80.0% | > 85.0% |
| **Hallucination Rate** | 20.0% | < 15.0% |
| **Average Critic Loops** | 0.5 | <= 1.5 |
| **Latency p50 / p95** | 183 ms / 280 ms | < 2500 ms |

## Case-by-Case Breakdown

| Case Code | Expected Cat | Actual Cat | Critic Score | Loops | Latency (ms) | Pass / Fail |
|-----------|--------------|------------|--------------|-------|--------------|-------------|
| `6cb8ea60` | tech | tech | 0.80 | 1 | 223 ms | [FAIL] |
| `1497c9ea` | tech | tech | 0.80 | 1 | 200 ms | [FAIL] |
| `4939dbaf` | billing | billing | 0.80 | 0 | 171 ms | [FAIL] |
| `f3e0e618` | billing | billing | 0.80 | 1 | 280 ms | [FAIL] |
| `8063e5c0` | tech | tech | 0.80 | 1 | 199 ms | [FAIL] |
| `ee6efa81` | general | general | 0.80 | 0 | 152 ms | [FAIL] |
| `a21509c9` | general | general | 0.80 | 0 | 178 ms | [PASS] |
| `ccff5d45` | general | general | 0.80 | 0 | 58 ms | [PASS] |
| `1ffd7be5` | general | general | 0.80 | 0 | 172 ms | [PASS] |
| `84c87640` | general | general | 0.80 | 1 | 198 ms | [FAIL] |
