# Phoenix Trace Export

12 trace(s) captured. Showing the most recent 10.

| # | Trace ID | Question | Model | Latency (ms) | Prompt tok | Compl. tok | Slowest child | Slowest (ms) |
|---|---|---|---|---|---|---|---|---|
| 1 | `57094cde1e578c1897ddd226c8db5ca1` | What is the weight of the baseline control paddle? | gpt-4o-mini | 5405.9 | 1060 | 12 | generation | 1515.6 |
| 2 | `ff432f1f21fd46d4e4a8b373df072dd4` | What is the weight of the baseline control paddle? | gpt-4o-mini | 6055.6 | 1060 | 12 | output_validation | 2481.6 |
| 3 | `a40f3d5461b80cde0089936fda3a6768` | What are the dimensions of baseline rally towel 1? | gpt-4o-mini | 5473.6 | 816 | 19 | classification | 1853.7 |
| 4 | `a8af35ce407ceafcc7b7c844a24575e6` | What is the weight of the baseline control paddle? | gpt-4o-mini | 67830.0 | 1060 | 15 | classification | 62662.7 |
| 5 | `f09aca86ef4eaf1ce4b519b58fb7cd93` | What is the weight of the baseline control paddle? | gpt-4o-mini | 127508.0 | 1060 | 12 | classification | 122955.2 |
| 6 | `aebaeeb86230aff87040df6addb8c3d4` | What is the weight of the baseline control paddle? | gpt-4o-mini | 4434.7 | 1060 | 15 | classification | 1379.4 |
| 7 | `0eacd8df86eb4f7cdfbd689636cd23fe` | What is the weight of the baseline control paddle? | gpt-4o-mini | 4465.7 | 1060 | 12 | classification | 1391.2 |
| 8 | `860827d0f42e5943172a57ac77f816c3` | What is the weight of the baseline control paddle? | gpt-4o-mini | 4513.3 | 1060 | 12 | classification | 1282.1 |
| 9 | `047bd919119f838fd7125167b5993792` | What is the weight of the baseline control paddle? | gpt-4o-mini | 4627.8 | 1060 | 15 | output_validation | 1283.6 |
| 10 | `55055cb877df09ce8f8fd48eb760168b` | What is the weight of the baseline control paddle? | gpt-4o-mini | 5437.4 | 1060 | 12 | classification | 1847.5 |

## Trace 57094cde1e578c1897ddd226c8db5ca1

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1107.58 |
| output_validation | 1112.17 |
| response_summary | 0.04 |
| ChatCompletion | 1511.64 |
| generation | 1515.57 |
| CreateEmbeddings | 1165.49 |
| retrieval | 1174.22 |
| rag_query | 2696.13 |
| ChatCompletion | 1372.14 |
| classification | 1377.76 |
| faq_request | 5405.86 |
Slowest step consumes 28.0% of total request latency.

## Trace ff432f1f21fd46d4e4a8b373df072dd4

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 2477.62 |
| output_validation | 2481.55 |
| response_summary | 0.04 |
| ChatCompletion | 1171.91 |
| generation | 1175.63 |
| CreateEmbeddings | 853.84 |
| retrieval | 866.35 |
| rag_query | 2049.07 |
| ChatCompletion | 1326.7 |
| classification | 1331.97 |
| faq_request | 6055.56 |
Slowest step consumes 41.0% of total request latency.

## Trace a40f3d5461b80cde0089936fda3a6768

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1177.01 |
| output_validation | 1182.33 |
| response_summary | 0.05 |
| ChatCompletion | 1117.79 |
| generation | 1124.23 |
| CreateEmbeddings | 1085.97 |
| retrieval | 1100.37 |
| rag_query | 2232.98 |
| ChatCompletion | 1848.39 |
| classification | 1853.71 |
| faq_request | 5473.56 |
Slowest step consumes 33.9% of total request latency.

## Trace a8af35ce407ceafcc7b7c844a24575e6

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1705.46 |
| output_validation | 1712.81 |
| response_summary | 0.05 |
| ChatCompletion | 1584.44 |
| generation | 1591.57 |
| CreateEmbeddings | 1590.19 |
| retrieval | 1605.83 |
| rag_query | 3206.01 |
| ChatCompletion | 62655.99 |
| classification | 62662.71 |
| faq_request | 67830.03 |
Slowest step consumes 92.4% of total request latency.

## Trace f09aca86ef4eaf1ce4b519b58fb7cd93

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1536.71 |
| output_validation | 1540.99 |
| response_summary | 0.06 |
| ChatCompletion | 1699.91 |
| generation | 1704.31 |
| CreateEmbeddings | 1113.83 |
| retrieval | 1129.13 |
| rag_query | 2842.98 |
| ChatCompletion | 122950.42 |
| classification | 122955.18 |
| faq_request | 127508.05 |
Slowest step consumes 96.4% of total request latency.

## Trace aebaeeb86230aff87040df6addb8c3d4

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1085.96 |
| output_validation | 1091.16 |
| response_summary | 0.06 |
| ChatCompletion | 1142.01 |
| generation | 1148.46 |
| CreateEmbeddings | 605.89 |
| retrieval | 615.36 |
| rag_query | 1772.21 |
| ChatCompletion | 1375.88 |
| classification | 1379.4 |
| faq_request | 4434.73 |
Slowest step consumes 31.1% of total request latency.

## Trace 0eacd8df86eb4f7cdfbd689636cd23fe

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1003.76 |
| output_validation | 1010.45 |
| response_summary | 0.03 |
| ChatCompletion | 1155.24 |
| generation | 1159.77 |
| CreateEmbeddings | 689.04 |
| retrieval | 697.95 |
| rag_query | 1863.13 |
| ChatCompletion | 1383.92 |
| classification | 1391.21 |
| faq_request | 4465.66 |
Slowest step consumes 31.2% of total request latency.

## Trace 860827d0f42e5943172a57ac77f816c3

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1142.0 |
| output_validation | 1148.09 |
| response_summary | 0.05 |
| ChatCompletion | 1058.07 |
| generation | 1063.46 |
| CreateEmbeddings | 789.87 |
| retrieval | 795.61 |
| rag_query | 1865.72 |
| ChatCompletion | 1274.78 |
| classification | 1282.11 |
| faq_request | 4513.34 |
Slowest step consumes 28.4% of total request latency.

## Trace 047bd919119f838fd7125167b5993792

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1277.59 |
| output_validation | 1283.61 |
| response_summary | 0.05 |
| ChatCompletion | 1178.98 |
| generation | 1185.72 |
| CreateEmbeddings | 642.82 |
| retrieval | 653.89 |
| rag_query | 1847.04 |
| ChatCompletion | 1261.83 |
| classification | 1268.57 |
| faq_request | 4627.84 |
Slowest step consumes 27.7% of total request latency.

## Trace 55055cb877df09ce8f8fd48eb760168b

| Span | Duration ms |
| --- | ---: |
| ChatCompletion | 1170.41 |
| output_validation | 1175.58 |
| response_summary | 0.04 |
| ChatCompletion | 1063.24 |
| generation | 1067.09 |
| CreateEmbeddings | 1121.67 |
| retrieval | 1131.03 |
| rag_query | 2204.19 |
| ChatCompletion | 1843.83 |
| classification | 1847.5 |
| faq_request | 5437.43 |
Slowest step consumes 34.0% of total request latency.
