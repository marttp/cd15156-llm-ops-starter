# Rubric evidence audit

All nine required rows have implementation and retained real-provider evidence. The automated audit checks completeness; external course grading remains the reviewer’s decision. See the ordered analysis in [WRITEUP.md](WRITEUP.md) and the [audit transcript](evidence/rubric-audit.txt).

| Row | Implementation and observed proof |
| --- | --- |
| 1 | Five validated catalog additions; literal curl cites `demo_control_paddle` |
| 2 | Complete QueryResponse and source fields; 35 scored questions at k=3/5/10; twelve finite means and recommendation with two measured deltas |
| 3 | Three uncached outputs with simple/complex classifications and two configured generation models |
| 4 | Three inbox products ingested by running observer; query sources and actual malformed quarantine/error retained |
| 5 | Independent four-metric evaluation, weakest-metric diagnosis, faithfulness floor 0.90 and demonstrated passing/failing exits |
| 6 | Three new injection patterns with blocked/legitimate pairs; real PII, off-topic and output-judge probes |
| 7 | Ten dedicated HTTP requests; matching Phoenix spans and slowest-step fraction 96.4% |
| 8 | Same 112-operation log, five-line excerpt, rendered dashboard, generation-tier counts/means and named baseline savings |
| 9 | Nine-section writeup, Python 3.12 lock, 264 tests, zero automated verification failures, clean-clone checks and secret scan |

Optional measurements cover the cache threshold tradeoff, three raw TTFT comparisons, and a 10,000-query/day cost projection. They are distinguished from guarded display latency and real production traffic. Diagnostic before-retry and before-safety-fix artifacts document failures rather than replacing accepted evidence.
