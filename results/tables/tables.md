### Table A-F1: F1 (%) on held-out entities, no injected drift, K = 5, point-wise, threshold set by each method

| Method | SKAB | SMD | HAI |
|---|---|---|---|
| IF | 16.0 ± 4.7 | 20.3 ± 9.4 | 1.9 ± 2.7 |
| VAE-S | 64.1 ± 5.9 | 35.5 ± 14.5 | 62.2 ± 0.0 |
| VAE-FT | **65.6 ± 6.0** | 35.1 ± 14.4 | 61.4 ± 1.1 |
| VAE-INC | 53.7 ± 2.4 | **39.0 ± 16.2** | 62.2 ± 0.0 |
| VAE-DFT | 42.7 ± 6.4 | 36.0 ± 16.6 | **62.2 ± 0.0** |
| MAML-1 | 64.1 ± 4.9 | 28.6 ± 6.5 | 52.1 ± 0.0 |
| MSGD-1 | 64.0 ± 5.1 | 28.8 ± 6.1 | 58.2 ± 0.0 |
| OML-A | 62.8 ± 4.5 | 32.1 ± 12.0 | 52.1 ± 0.0 |
| DAMAD | 54.9 ± 4.8 | 29.1 ± 4.1 | 52.1 ± 0.0 |

### Table A-AUROC: AUROC (%) on held-out entities, no injected drift, K = 5, point-wise, threshold set by each method

| Method | SKAB | SMD | HAI |
|---|---|---|---|
| IF | **86.8 ± 4.6** | 81.4 ± 2.5 | 47.1 ± 1.2 |
| VAE-S | 85.3 ± 3.0 | 87.5 ± 5.5 | 96.8 ± 0.0 |
| VAE-FT | 86.7 ± 3.5 | 88.1 ± 4.9 | 94.9 ± 0.9 |
| VAE-INC | 80.2 ± 3.0 | **88.8 ± 3.2** | **97.4 ± 0.0** |
| VAE-DFT | 75.2 ± 3.1 | 85.2 ± 7.5 | 94.9 ± 0.0 |
| MAML-1 | 85.8 ± 3.1 | 87.8 ± 4.8 | 94.7 ± 0.0 |
| MSGD-1 | 85.8 ± 3.0 | 87.8 ± 4.4 | 94.3 ± 0.0 |
| OML-A | 85.4 ± 3.0 | 87.7 ± 5.2 | 95.1 ± 0.0 |
| DAMAD | 85.8 ± 3.1 | 85.7 ± 6.5 | 94.7 ± 0.0 |

### Table A-AUPRC: AUPRC (%) on held-out entities, no injected drift, K = 5, point-wise, threshold set by each method

| Method | SKAB | SMD | HAI |
|---|---|---|---|
| IF | 79.5 ± 6.5 | 37.8 ± 4.1 | 1.1 ± 0.1 |
| VAE-S | 81.5 ± 4.0 | 54.1 ± 13.4 | 67.3 ± 0.0 |
| VAE-FT | **83.2 ± 4.4** | 51.4 ± 8.9 | 64.9 ± 1.0 |
| VAE-INC | 76.0 ± 3.1 | **55.3 ± 13.1** | 68.0 ± 0.0 |
| VAE-DFT | 69.8 ± 4.9 | 49.1 ± 15.5 | 66.0 ± 0.0 |
| MAML-1 | 82.3 ± 4.3 | 52.1 ± 9.6 | 69.8 ± 0.0 |
| MSGD-1 | 82.3 ± 4.1 | 51.9 ± 6.7 | 68.8 ± 0.0 |
| OML-A | 81.8 ± 4.0 | 52.7 ± 9.0 | **69.9 ± 0.0** |
| DAMAD | 82.1 ± 4.4 | 50.4 ± 8.8 | 69.8 ± 0.0 |

### Table A-bestF1: oracle-threshold F1 (%) for context only

| Method | SKAB | SMD | HAI |
|---|---|---|---|
| IF | 77.9 ± 4.5 | 41.4 ± 4.1 | 3.3 ± 1.4 |
| VAE-S | 81.3 ± 3.0 | 55.4 ± 10.7 | 73.6 ± 0.4 |
| VAE-FT | **82.1 ± 3.4** | 54.0 ± 9.2 | 73.3 ± 0.0 |
| VAE-INC | 75.2 ± 3.1 | **57.4 ± 9.9** | 73.9 ± 0.0 |
| VAE-DFT | 66.1 ± 3.1 | 51.0 ± 13.2 | 73.3 ± 0.0 |
| MAML-1 | 81.8 ± 3.2 | 54.3 ± 8.3 | 73.9 ± 0.0 |
| MSGD-1 | 81.7 ± 3.1 | 54.4 ± 6.8 | **75.2 ± 0.0** |
| OML-A | 81.3 ± 3.0 | 55.6 ± 9.3 | 73.9 ± 0.0 |
| DAMAD | 81.8 ± 3.2 | 54.4 ± 9.8 | 73.9 ± 0.0 |

### Table B-F1-SKAB: F1 on SKAB by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 16.0 ± 4.7 | – | – | – | – |
| VAE-S | 64.1 ± 5.9 | – | – | – | – |
| VAE-FT | **65.6 ± 6.0** | – | – | – | – |
| VAE-INC | 53.7 ± 2.4 | – | – | – | – |
| VAE-DFT | 42.7 ± 6.4 | – | – | – | – |
| MAML-1 | 64.1 ± 4.9 | – | – | – | – |
| MSGD-1 | 64.0 ± 5.1 | – | – | – | – |
| OML-A | 62.8 ± 4.5 | – | – | – | – |
| DAMAD | 54.9 ± 4.8 | – | – | – | – |

### Table B-F1-SMD: F1 on SMD by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 20.3 ± 9.4 | 14.5 ± 10.1 | 14.2 ± 10.1 | 10.4 ± 4.2 | 10.8 ± 4.6 |
| VAE-S | 35.5 ± 14.5 | 11.6 ± 8.0 | 11.8 ± 8.1 | 9.3 ± 3.6 | 9.8 ± 3.6 |
| VAE-FT | 35.1 ± 14.4 | 12.2 ± 8.0 | 12.1 ± 8.0 | 9.8 ± 3.9 | 10.5 ± 4.1 |
| VAE-INC | **39.0 ± 16.2** | 12.9 ± 7.4 | 20.1 ± 8.1 | **23.1 ± 4.2** | 13.1 ± 6.6 |
| VAE-DFT | 36.0 ± 16.6 | **27.8 ± 15.9** | **23.6 ± 11.7** | 16.2 ± 4.4 | 21.3 ± 8.1 |
| MAML-1 | 28.6 ± 6.5 | 12.1 ± 7.7 | 12.4 ± 7.9 | 9.9 ± 3.7 | 10.3 ± 3.9 |
| MSGD-1 | 28.8 ± 6.1 | 12.7 ± 8.1 | 12.8 ± 8.2 | 9.9 ± 3.8 | 10.8 ± 4.7 |
| OML-A | 32.1 ± 12.0 | 12.5 ± 7.6 | 12.7 ± 8.4 | 10.1 ± 4.1 | 10.9 ± 4.1 |
| DAMAD | 29.1 ± 4.1 | 25.2 ± 5.3 | 23.1 ± 6.6 | 21.3 ± 1.9 | **24.2 ± 5.0** |

### Table B-F1-HAI: F1 on HAI by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 1.9 ± 2.7 | 0.4 ± 0.0 | 0.4 ± 0.0 | – | – |
| VAE-S | 62.2 ± 0.0 | 2.3 ± 0.0 | 2.6 ± 0.0 | – | – |
| VAE-FT | 61.4 ± 1.1 | 2.3 ± 0.0 | 2.5 ± 0.0 | – | – |
| VAE-INC | 62.2 ± 0.0 | 8.3 ± 0.0 | 63.8 ± 0.0 | – | – |
| VAE-DFT | **62.2 ± 0.0** | 6.2 ± 0.0 | 28.7 ± 0.0 | – | – |
| MAML-1 | 52.1 ± 0.0 | **64.6 ± 0.0** | **64.6 ± 0.0** | – | – |
| MSGD-1 | 58.2 ± 0.0 | 6.7 ± 0.0 | 5.5 ± 0.0 | – | – |
| OML-A | 52.1 ± 0.0 | 61.7 ± 0.0 | – | – | – |
| DAMAD | 52.1 ± 0.0 | 55.7 ± 0.0 | – | – | – |

### Table B-F1-ALL: F1, pooled over datasets, by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 16.5 ± 4.0 | 14.3 ± 10.2 | 14.1 ± 10.2 | 10.4 ± 4.2 | 10.8 ± 4.6 |
| VAE-S | 51.9 ± 8.7 | 11.5 ± 8.1 | 11.7 ± 8.1 | 9.3 ± 3.6 | 9.8 ± 3.6 |
| VAE-FT | **53.2 ± 11.0** | 12.0 ± 8.0 | 12.0 ± 8.1 | 9.8 ± 3.9 | 10.5 ± 4.1 |
| VAE-INC | 46.6 ± 6.7 | 12.8 ± 7.4 | 21.3 ± 6.9 | **23.1 ± 4.2** | 13.1 ± 6.6 |
| VAE-DFT | 39.0 ± 7.6 | **27.3 ± 16.0** | **23.8 ± 11.6** | 16.2 ± 4.4 | 21.3 ± 8.1 |
| MAML-1 | 50.4 ± 8.1 | 13.3 ± 7.6 | 13.6 ± 7.7 | 9.9 ± 3.7 | 10.3 ± 3.9 |
| MSGD-1 | 50.3 ± 7.5 | 12.7 ± 8.1 | 12.7 ± 8.3 | 9.9 ± 3.8 | 10.8 ± 4.7 |
| OML-A | 49.9 ± 7.5 | 13.7 ± 7.3 | 12.7 ± 8.4 | 10.1 ± 4.1 | 10.9 ± 4.1 |
| DAMAD | 45.9 ± 5.5 | 25.9 ± 5.4 | 23.1 ± 6.6 | 21.3 ± 1.9 | **24.2 ± 5.0** |

### Table B-FPR under drift-SKAB: FPR under drift on SKAB by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | – | – | – | – |
| VAE-S | – | – | – | – | – |
| VAE-FT | – | – | – | – | – |
| VAE-INC | – | – | – | – | – |
| VAE-DFT | – | – | – | – | – |
| MAML-1 | – | – | – | – | – |
| MSGD-1 | – | – | – | – | – |
| OML-A | – | – | – | – | – |
| DAMAD | – | – | – | – | – |

### Table B-FPR under drift-SMD: FPR under drift on SMD by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | 67.1 ± 23.6 | 65.3 ± 24.7 | 73.8 ± 3.5 | 64.8 ± 5.6 |
| VAE-S | – | 96.6 ± 5.2 | 93.8 ± 5.2 | 82.8 ± 5.3 | 74.0 ± 3.9 |
| VAE-FT | – | 97.2 ± 5.2 | 94.1 ± 4.5 | 84.1 ± 5.0 | 75.2 ± 3.6 |
| VAE-INC | – | 83.9 ± 13.1 | 51.1 ± 18.3 | 23.1 ± 0.7 | 56.5 ± 11.4 |
| VAE-DFT | – | 25.3 ± 14.4 | 26.1 ± 9.2 | 34.6 ± 5.2 | 23.6 ± 8.8 |
| MAML-1 | – | 95.7 ± 5.0 | 93.1 ± 5.1 | 83.0 ± 4.6 | 77.7 ± 3.8 |
| MSGD-1 | – | 93.9 ± 9.6 | 91.3 ± 8.6 | 82.5 ± 6.6 | 76.2 ± 7.3 |
| OML-A | – | 89.8 ± 10.1 | 88.1 ± 6.1 | 80.7 ± 4.2 | 71.5 ± 4.6 |
| DAMAD | – | **15.0 ± 8.1** | **19.6 ± 8.8** | **19.5 ± 5.2** | **12.0 ± 4.4** |

### Table B-FPR under drift-HAI: FPR under drift on HAI by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | 56.3 ± 0.0 | 58.8 ± 0.0 | – | – |
| VAE-S | – | 98.9 ± 0.0 | 88.3 ± 0.0 | – | – |
| VAE-FT | – | 99.9 ± 0.0 | 90.0 ± 0.0 | – | – |
| VAE-INC | – | 23.0 ± 0.0 | **0.4 ± 0.0** | – | – |
| VAE-DFT | – | 35.0 ± 0.0 | 3.5 ± 0.0 | – | – |
| MAML-1 | – | 0.5 ± 0.0 | 0.5 ± 0.0 | – | – |
| MSGD-1 | – | 31.3 ± 0.0 | 40.1 ± 0.0 | – | – |
| OML-A | – | 0.5 ± 0.0 | – | – | – |
| DAMAD | – | **0.2 ± 0.0** | – | – | – |

### Table B-FPR under drift-ALL: FPR under drift, pooled over datasets, by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | 66.6 ± 23.4 | 65.0 ± 24.5 | 73.8 ± 3.5 | 64.8 ± 5.6 |
| VAE-S | – | 96.6 ± 5.2 | 93.6 ± 5.0 | 82.8 ± 5.3 | 74.0 ± 3.9 |
| VAE-FT | – | 97.2 ± 5.2 | 93.9 ± 4.3 | 84.1 ± 5.0 | 75.2 ± 3.6 |
| VAE-INC | – | 82.3 ± 11.7 | 49.4 ± 15.6 | 23.1 ± 0.7 | 56.5 ± 11.4 |
| VAE-DFT | – | 25.7 ± 14.1 | 25.6 ± 9.4 | 34.6 ± 5.2 | 23.6 ± 8.8 |
| MAML-1 | – | 93.5 ± 5.1 | 91.0 ± 5.3 | 83.0 ± 4.6 | 77.7 ± 3.8 |
| MSGD-1 | – | 92.3 ± 8.9 | 90.0 ± 7.9 | 82.5 ± 6.6 | 76.2 ± 7.3 |
| OML-A | – | 87.5 ± 8.3 | 88.1 ± 6.1 | 80.7 ± 4.2 | 71.5 ± 4.6 |
| DAMAD | – | **14.4 ± 7.1** | **19.6 ± 8.8** | **19.5 ± 5.2** | **12.0 ± 4.4** |

### Table B-adaptation steps-SKAB: adaptation steps on SKAB by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | – | – | – | – |
| VAE-S | – | – | – | – | – |
| VAE-FT | – | – | – | – | – |
| VAE-INC | – | – | – | – | – |
| VAE-DFT | – | – | – | – | – |
| MAML-1 | – | – | – | – | – |
| MSGD-1 | – | – | – | – | – |
| OML-A | – | – | – | – | – |
| DAMAD | – | – | – | – | – |

### Table B-adaptation steps-SMD: adaptation steps on SMD by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | 3114 ± 1744 | 782 ± 510 | 642 ± 604 | 2605 ± 193 |
| VAE-S | – | 4609 ± 1104 | 1693 ± 1250 | 422 ± 444 | 3033 ± 324 |
| VAE-FT | – | 4637 ± 1132 | 1731 ± 1079 | 629 ± 509 | 3033 ± 324 |
| VAE-INC | – | 4043 ± 993 | 951 ± 827 | 150 ± 37 | 2394 ± 412 |
| VAE-DFT | – | **441 ± 354** | 287 ± 185 | 137 ± 5 | 610 ± 320 |
| MAML-1 | – | 4367 ± 1152 | 2024 ± 1190 | 1584 ± 1014 | 3097 ± 360 |
| MSGD-1 | – | 4305 ± 1221 | 1889 ± 1182 | 1266 ± 892 | 3069 ± 495 |
| OML-A | – | 4172 ± 1227 | 1924 ± 1142 | 1069 ± 1016 | 2784 ± 389 |
| DAMAD | – | 517 ± 352 | **268 ± 218** | **135 ± 10** | **246 ± 47** |

### Table B-adaptation steps-HAI: adaptation steps on HAI by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | 914 ± 0 | 914 ± 0 | – | – |
| VAE-S | – | 1404 ± 0 | 99 ± 0 | – | – |
| VAE-FT | – | 1404 ± 0 | 914 ± 0 | – | – |
| VAE-INC | – | 418 ± 0 | 99 ± 0 | – | – |
| VAE-DFT | – | 280 ± 0 | 99 ± 0 | – | – |
| MAML-1 | – | 99 ± 0 | **99 ± 0** | – | – |
| MSGD-1 | – | 590 ± 0 | 99 ± 0 | – | – |
| OML-A | – | 99 ± 0 | – | – | – |
| DAMAD | – | **99 ± 0** | – | – | – |

### Table B-adaptation steps-ALL: adaptation steps, pooled over datasets, by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | – | 3034 ± 1671 | 777 ± 505 | 642 ± 604 | 2605 ± 193 |
| VAE-S | – | 4511 ± 983 | 1624 ± 1151 | 422 ± 444 | 3033 ± 324 |
| VAE-FT | – | 4538 ± 1017 | 1687 ± 1020 | 629 ± 509 | 3033 ± 324 |
| VAE-INC | – | 3930 ± 791 | 903 ± 736 | 150 ± 37 | 2394 ± 412 |
| VAE-DFT | – | **441 ± 354** | 280 ± 180 | 137 ± 5 | 610 ± 320 |
| MAML-1 | – | 4239 ± 970 | 1955 ± 1111 | 1584 ± 1014 | 3097 ± 360 |
| MSGD-1 | – | 4188 ± 1055 | 1816 ± 1072 | 1266 ± 892 | 3069 ± 495 |
| OML-A | – | 4045 ± 1028 | 1924 ± 1142 | 1069 ± 1016 | 2784 ± 389 |
| DAMAD | – | 495 ± 311 | **268 ± 218** | **135 ± 10** | **246 ± 47** |

### Table B-detection latency (steps)-SKAB: detection latency (steps) on SKAB by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 137 ± 24 | – | – | – | – |
| VAE-S | 34 ± 5 | – | – | – | – |
| VAE-FT | **29 ± 10** | – | – | – | – |
| VAE-INC | 35 ± 10 | – | – | – | – |
| VAE-DFT | 31 ± 10 | – | – | – | – |
| MAML-1 | 36 ± 5 | – | – | – | – |
| MSGD-1 | 34 ± 7 | – | – | – | – |
| OML-A | 38 ± 7 | – | – | – | – |
| DAMAD | 37 ± 6 | – | – | – | – |

### Table B-detection latency (steps)-SMD: detection latency (steps) on SMD by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 73 ± 137 | 14 ± 20 | 29 ± 50 | 7 ± 9 | 7 ± 8 |
| VAE-S | 3 ± 2 | 1 ± 1 | 1 ± 1 | 1 ± 0 | 3 ± 1 |
| VAE-FT | **2 ± 1** | 1 ± 1 | **1 ± 1** | **1 ± 0** | **2 ± 1** |
| VAE-INC | 11 ± 9 | 5 ± 5 | 6 ± 5 | 9 ± 5 | 9 ± 5 |
| VAE-DFT | 5 ± 3 | 4 ± 3 | 4 ± 3 | 6 ± 1 | 5 ± 3 |
| MAML-1 | 3 ± 2 | 1 ± 1 | 1 ± 1 | 1 ± 0 | 3 ± 1 |
| MSGD-1 | 3 ± 2 | **1 ± 1** | 1 ± 1 | 1 ± 0 | 2 ± 1 |
| OML-A | 3 ± 2 | 1 ± 1 | 1 ± 1 | 1 ± 0 | 3 ± 1 |
| DAMAD | 62 ± 116 | 7 ± 6 | 9 ± 6 | 10 ± 5 | 10 ± 6 |

### Table B-detection latency (steps)-HAI: detection latency (steps) on HAI by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 16 ± 0 | 16 ± 0 | 16 ± 0 | – | – |
| VAE-S | 3 ± 0 | 1 ± 0 | 1 ± 0 | – | – |
| VAE-FT | 3 ± 0 | 1 ± 0 | 1 ± 0 | – | – |
| VAE-INC | 3 ± 0 | 2 ± 0 | 2 ± 0 | – | – |
| VAE-DFT | **3 ± 0** | **1 ± 0** | 4 ± 0 | – | – |
| MAML-1 | 4 ± 0 | 2 ± 0 | 2 ± 0 | – | – |
| MSGD-1 | 4 ± 0 | 1 ± 0 | **1 ± 0** | – | – |
| OML-A | 4 ± 0 | 2 ± 0 | – | – | – |
| DAMAD | 4 ± 0 | 2 ± 0 | – | – | – |

### Table B-detection latency (steps)-ALL: detection latency (steps), pooled over datasets, by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 84 ± 52 | 14 ± 20 | 29 ± 50 | 7 ± 9 | 7 ± 8 |
| VAE-S | 22 ± 8 | 1 ± 1 | 1 ± 1 | 1 ± 0 | 3 ± 1 |
| VAE-FT | **19 ± 10** | **1 ± 1** | **1 ± 1** | **1 ± 0** | **2 ± 1** |
| VAE-INC | 27 ± 8 | 5 ± 5 | 6 ± 5 | 9 ± 5 | 9 ± 5 |
| VAE-DFT | 21 ± 8 | 4 ± 3 | 4 ± 3 | 6 ± 1 | 5 ± 3 |
| MAML-1 | 24 ± 6 | 1 ± 1 | 1 ± 1 | 1 ± 0 | 3 ± 1 |
| MSGD-1 | 22 ± 8 | 1 ± 1 | 1 ± 1 | 1 ± 0 | 2 ± 1 |
| OML-A | 24 ± 6 | 1 ± 1 | 1 ± 1 | 1 ± 0 | 3 ± 1 |
| DAMAD | 31 ± 16 | 6 ± 6 | 9 ± 6 | 10 ± 5 | 10 ± 6 |

### Table B-segment detection rate-SKAB: segment detection rate on SKAB by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 58.0 ± 4.5 | – | – | – | – |
| VAE-S | 96.0 ± 8.9 | – | – | – | – |
| VAE-FT | 98.0 ± 4.5 | – | – | – | – |
| VAE-INC | 94.0 ± 8.9 | – | – | – | – |
| VAE-DFT | 98.0 ± 4.5 | – | – | – | – |
| MAML-1 | 98.0 ± 4.5 | – | – | – | – |
| MSGD-1 | 98.0 ± 4.5 | – | – | – | – |
| OML-A | 98.0 ± 4.5 | – | – | – | – |
| DAMAD | **98.0 ± 4.5** | – | – | – | – |

### Table B-segment detection rate-SMD: segment detection rate on SMD by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 68.0 ± 5.7 | 78.8 ± 9.6 | 79.4 ± 9.7 | 82.6 ± 5.1 | 77.8 ± 3.3 |
| VAE-S | 95.2 ± 2.8 | 96.1 ± 2.4 | 96.7 ± 1.9 | 95.8 ± 0.6 | 94.8 ± 1.0 |
| VAE-FT | **97.6 ± 2.0** | **97.9 ± 1.6** | **98.5 ± 1.4** | **98.3 ± 0.8** | **97.3 ± 1.3** |
| VAE-INC | 88.3 ± 7.4 | 93.3 ± 3.9 | 93.3 ± 4.1 | 89.0 ± 1.9 | 91.2 ± 1.2 |
| VAE-DFT | 88.6 ± 8.6 | 89.4 ± 7.6 | 89.3 ± 7.0 | 90.7 ± 2.0 | 87.1 ± 8.3 |
| MAML-1 | 96.5 ± 2.1 | 97.0 ± 1.8 | 97.3 ± 1.7 | 96.9 ± 0.6 | 95.9 ± 0.3 |
| MSGD-1 | 96.8 ± 2.9 | 97.8 ± 1.6 | 97.8 ± 1.6 | 97.8 ± 0.9 | 96.3 ± 2.1 |
| OML-A | 96.5 ± 2.1 | 96.7 ± 1.9 | 96.7 ± 1.9 | 96.9 ± 0.6 | 95.9 ± 0.3 |
| DAMAD | 72.0 ± 19.6 | 73.2 ± 27.2 | 78.0 ± 9.4 | 83.0 ± 5.7 | 82.0 ± 3.8 |

### Table B-segment detection rate-HAI: segment detection rate on HAI by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 12.5 ± 17.7 | 25.0 ± 0.0 | 25.0 ± 0.0 | – | – |
| VAE-S | 75.0 ± 0.0 | 75.0 ± 0.0 | 75.0 ± 0.0 | – | – |
| VAE-FT | 75.0 ± 0.0 | 75.0 ± 0.0 | 75.0 ± 0.0 | – | – |
| VAE-INC | 75.0 ± 0.0 | 75.0 ± 0.0 | 75.0 ± 0.0 | – | – |
| VAE-DFT | 75.0 ± 0.0 | 75.0 ± 0.0 | 75.0 ± 0.0 | – | – |
| MAML-1 | 50.0 ± 0.0 | **75.0 ± 0.0** | **75.0 ± 0.0** | – | – |
| MSGD-1 | **75.0 ± 0.0** | 75.0 ± 0.0 | 75.0 ± 0.0 | – | – |
| OML-A | 50.0 ± 0.0 | 75.0 ± 0.0 | – | – | – |
| DAMAD | 50.0 ± 0.0 | 50.0 ± 0.0 | – | – | – |

### Table B-segment detection rate-ALL: segment detection rate, pooled over datasets, by drift condition (K = 5)

| Method | none | sudden | gradual | incremental | recurring |
|---|---|---|---|---|---|
| IF | 61.3 ± 5.1 | 77.7 ± 10.0 | 78.2 ± 10.0 | 82.6 ± 5.1 | 77.8 ± 3.3 |
| VAE-S | 95.3 ± 5.6 | 95.7 ± 2.6 | 96.2 ± 2.3 | 95.8 ± 0.6 | 94.8 ± 1.0 |
| VAE-FT | **97.4 ± 2.7** | **97.4 ± 1.9** | **97.9 ± 1.6** | **98.3 ± 0.8** | **97.3 ± 1.3** |
| VAE-INC | 91.4 ± 5.9 | 92.9 ± 4.0 | 92.9 ± 4.1 | 89.0 ± 1.9 | 91.2 ± 1.2 |
| VAE-DFT | 93.7 ± 4.6 | 89.2 ± 7.8 | 89.0 ± 7.1 | 90.7 ± 2.0 | 87.1 ± 8.3 |
| MAML-1 | 96.9 ± 3.7 | 96.5 ± 2.3 | 96.8 ± 2.3 | 96.9 ± 0.6 | 95.9 ± 0.3 |
| MSGD-1 | 97.3 ± 2.9 | 97.2 ± 1.8 | 97.2 ± 1.8 | 97.8 ± 0.9 | 96.3 ± 2.1 |
| OML-A | 96.9 ± 3.7 | 96.2 ± 2.3 | 96.7 ± 1.9 | 96.9 ± 0.6 | 95.9 ± 0.3 |
| DAMAD | 90.5 ± 4.8 | 72.4 ± 26.9 | 78.0 ± 9.4 | 83.0 ± 5.7 | 82.0 ± 3.8 |

### Table C-SKAB: F1 (%) versus number of shots on SKAB (no injected drift)

| Method | 1-shot | 5-shot | 10-shot |
|---|---|---|---|
| VAE-S | 64.2 ± 5.9 | 64.1 ± 5.9 | 63.6 ± 6.5 |
| VAE-FT | **66.7 ± 6.0** | **65.6 ± 6.0** | **64.3 ± 7.4** |
| MAML-1 | 64.1 ± 5.1 | 64.1 ± 4.9 | 63.2 ± 6.1 |
| MSGD-1 | 64.2 ± 4.9 | 64.0 ± 5.1 | 63.2 ± 5.8 |
| OML-A | 63.2 ± 5.0 | 62.8 ± 4.5 | 62.3 ± 5.7 |
| DAMAD | 54.7 ± 5.0 | 54.9 ± 4.8 | 55.2 ± 5.7 |

### Table C-SMD: F1 (%) versus number of shots on SMD (no injected drift)

| Method | 1-shot | 5-shot | 10-shot |
|---|---|---|---|
| VAE-S | **35.5 ± 14.5** | **35.5 ± 14.5** | **35.5 ± 14.5** |
| VAE-FT | 34.8 ± 15.0 | 35.1 ± 14.4 | 34.2 ± 13.4 |
| MAML-1 | 28.7 ± 6.4 | 28.6 ± 6.5 | 28.7 ± 6.4 |
| MSGD-1 | 29.0 ± 6.1 | 28.8 ± 6.1 | 28.8 ± 6.1 |
| OML-A | 29.2 ± 6.6 | 32.1 ± 12.0 | 30.1 ± 7.8 |
| DAMAD | 32.9 ± 6.0 | 29.1 ± 4.1 | 31.2 ± 3.7 |

### Table C-HAI: F1 (%) versus number of shots on HAI (no injected drift)

| Method | 1-shot | 5-shot | 10-shot |
|---|---|---|---|
| VAE-S | 62.2 ± 0.0 | **62.2 ± 0.0** | 62.2 ± 0.0 |
| VAE-FT | **62.2 ± 0.0** | 61.4 ± 1.1 | **62.2 ± 0.0** |
| MAML-1 | 52.1 ± 0.0 | 52.1 ± 0.0 | 52.1 ± 0.0 |
| MSGD-1 | 57.5 ± 0.0 | 58.2 ± 0.0 | 57.5 ± 0.0 |
| OML-A | 52.1 ± 0.0 | 52.1 ± 0.0 | 52.1 ± 0.0 |
| DAMAD | 52.1 ± 0.0 | 52.1 ± 0.0 | 52.1 ± 0.0 |

### Table D-F1: ablations, F1, drift conditions pooled (K = 5)

| Variant | SKAB | SMD | HAI |
|---|---|---|---|
| DAMAD | – | 24.1 ± 3.8 | 55.7 ± 0.0 |
| DAMAD-rndM1 | – | 26.1 ± 7.5 | 28.9 ± 0.0 |
| DAMAD-noM1 | – | 21.9 ± 2.2 | 25.8 ± 0.0 |
| DAMAD+mmd | – | 23.2 ± 7.3 | 7.3 ± 0.0 |
| DAMAD-mmd | – | 14.1 ± 6.3 | **59.8 ± 0.0** |
| DAMAD-noM3 | – | 25.3 ± 7.8 | 55.7 ± 0.0 |
| DAMAD-noM4 | – | 16.0 ± 8.7 | 59.2 ± 0.0 |
| DAMAD-noAcc | – | 23.8 ± 2.7 | 55.7 ± 0.0 |
| DAMAD-fo | – | **26.2 ± 5.5** | 51.3 ± 0.0 |
| DAMAD-msgd | – | 25.9 ± 7.3 | 28.6 ± 0.0 |

### Table D-FPR under drift: ablations, FPR under drift, drift conditions pooled (K = 5)

| Variant | SKAB | SMD | HAI |
|---|---|---|---|
| DAMAD | – | 15.8 ± 4.8 | **0.2 ± 0.0** |
| DAMAD-rndM1 | – | 18.8 ± 4.3 | 5.2 ± 0.0 |
| DAMAD-noM1 | – | 16.9 ± 5.2 | 4.0 ± 0.0 |
| DAMAD+mmd | – | 20.6 ± 5.3 | 19.0 ± 0.0 |
| DAMAD-mmd | – | 73.6 ± 15.1 | 0.6 ± 0.0 |
| DAMAD-noM3 | – | 22.3 ± 4.1 | 0.2 ± 0.0 |
| DAMAD-noM4 | – | 70.2 ± 9.1 | 0.6 ± 0.0 |
| DAMAD-noAcc | – | **13.8 ± 4.9** | 0.2 ± 0.0 |
| DAMAD-fo | – | 24.5 ± 21.4 | 0.3 ± 0.0 |
| DAMAD-msgd | – | 19.0 ± 7.4 | 2.9 ± 0.0 |

### Table D-adaptation steps: ablations, adaptation steps, drift conditions pooled (K = 5)

| Variant | SKAB | SMD | HAI |
|---|---|---|---|
| DAMAD | – | 286 ± 145 | **99 ± 0** |
| DAMAD-rndM1 | – | 282 ± 126 | 310 ± 0 |
| DAMAD-noM1 | – | 341 ± 99 | 164 ± 0 |
| DAMAD+mmd | – | 575 ± 276 | 99 ± 0 |
| DAMAD-mmd | – | 2413 ± 528 | 99 ± 0 |
| DAMAD-noM3 | – | 301 ± 121 | 99 ± 0 |
| DAMAD-noM4 | – | 1497 ± 1005 | 99 ± 0 |
| DAMAD-noAcc | – | 247 ± 66 | 99 ± 0 |
| DAMAD-fo | – | **217 ± 76** | 99 ± 0 |
| DAMAD-msgd | – | 387 ± 213 | 160 ± 0 |

### Table E: computational cost per run (means over all runs with K = 5)

| Method | ms_per_window | adapt_s | meta_update_s | n_adapt | memory_kb | n_params |
|---|---|---|---|---|---|---|
| IF | 0.017 | 0.24 | 0.0 | 1.0 | 0.0 | 0.0 |
| VAE-S | 0.227 | 0.0 | 0.0 | 1.0 | 0.0 | 182296.0 |
| VAE-FT | 0.229 | 0.114 | 0.0 | 1.0 | 0.0 | 182296.0 |
| VAE-INC | 0.264 | 16.799 | 0.0 | 1.0 | 0.0 | 182296.0 |
| VAE-DFT | 0.237 | 0.533 | 0.0 | 4.611 | 0.0 | 182296.0 |
| MAML-1 | 0.223 | 0.01 | 0.0 | 1.0 | 0.0 | 182296.0 |
| MSGD-1 | 0.227 | 0.01 | 0.0 | 1.0 | 0.0 | 182296.0 |
| OML-A | 0.236 | 0.041 | 0.0 | 3.86 | 61.885 | 182296.0 |
| DAMAD | 0.234 | 0.043 | 1.667 | 3.949 | 88.383 | 182296.0 |

### Table F: mean number of confirmed drift events per DAMAD run

| Dataset | gradual | incremental | none | recurring | sudden |
|---|---|---|---|---|---|
| skab | nan | nan | 0.72 | nan | nan |
| smd | 3.91 | 4.31 | 2.79 | 3.56 | 3.76 |
| hai | nan | nan | 0.0 | nan | 1.0 |
