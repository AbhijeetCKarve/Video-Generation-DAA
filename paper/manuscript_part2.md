
# 7 Results

All numbers are means ± standard deviations over five seeds, where each seed's value is first averaged over the held-out entities of a dataset. The complete tables, including per-dataset versions of every pooled table, are in the repository; the ones reproduced here are the ones the text refers to. In total 7,560 streaming runs were scored.

## 7.1 Few-shot cold start without injected drift

Table 8 gives point-wise F1 at each method's own threshold and AUROC on the original test streams with K = 5. Two things stand out. The AUROC column is almost flat across every VAE-based method on every dataset: 85--87 % on SKAB, 82--87 % on SMD, 69--78 % on PSM, 94--95 % on HAI. The ranking of the raw scores does not depend much on how the model was initialised or whether it adapts. What differs is F1, and F1 is decided by the threshold and by what the detector does after the first 300 windows.

Table 8. Cold start on held-out entities, no injected drift, K = 5. Point-wise F1 (%) at the deployed threshold and AUROC (%). Best per column in bold.

| Method | SKAB F1 | SMD F1 | PSM F1 | HAI F1 | SKAB AUROC | SMD AUROC | PSM AUROC | HAI AUROC |
|---|---|---|---|---|---|---|---|---|
| IF | 16.0 ± 4.7 | 18.3 ± 6.6 | 46.0 ± 1.9 | 9.1 ± 4.1 | **86.8 ± 4.6** | 79.7 ± 2.2 | 69.1 ± 2.4 | 73.0 ± 1.8 |
| VAE-S | 64.1 ± 5.9 | 29.4 ± 5.1 | **59.3 ± 2.1** | **32.7 ± 3.9** | 85.3 ± 3.0 | 84.1 ± 3.9 | **77.7 ± 0.9** | **94.9 ± 0.1** |
| VAE-FT | **65.6 ± 6.0** | 28.7 ± 4.6 | 52.4 ± 2.1 | 32.2 ± 4.0 | 86.7 ± 3.5 | 84.6 ± 4.7 | 73.3 ± 1.6 | 94.2 ± 0.2 |
| VAE-INC | 53.7 ± 2.4 | **32.9 ± 6.3** | 38.6 ± 0.7 | 31.1 ± 2.2 | 80.2 ± 3.0 | **86.7 ± 3.2** | 57.6 ± 0.9 | 94.8 ± 0.2 |
| VAE-DFT | 42.7 ± 6.4 | 29.4 ± 3.2 | 43.5 ± 9.0 | 32.1 ± 4.5 | 75.2 ± 3.1 | 81.8 ± 3.8 | 70.6 ± 3.6 | 94.3 ± 0.2 |
| MAML-1 | 64.1 ± 4.9 | 26.1 ± 5.3 | 52.6 ± 0.9 | 21.7 ± 1.0 | 85.8 ± 3.1 | 84.4 ± 4.5 | 76.3 ± 1.5 | 93.8 ± 0.4 |
| MSGD-1 | 64.0 ± 5.1 | 26.6 ± 4.5 | 53.6 ± 2.6 | 21.6 ± 0.4 | 85.8 ± 3.0 | 84.6 ± 4.3 | 75.3 ± 0.4 | 93.6 ± 0.2 |
| OML-A | 62.8 ± 4.5 | 27.0 ± 5.2 | 52.6 ± 1.6 | 23.5 ± 1.4 | 85.4 ± 3.0 | 84.6 ± 4.1 | 75.7 ± 2.0 | 94.2 ± 0.4 |
| DAMAD | 54.9 ± 4.8 | 29.4 ± 3.5 | 46.7 ± 14.5 | 25.7 ± 5.0 | 85.8 ± 3.1 | 82.9 ± 4.5 | 69.4 ± 6.3 | 94.1 ± 0.1 |

Without drift, the static VAE is as good as anything else and better than the meta-learned detectors on PSM and HAI. The meta-learned initialisation adapted once (MAML-1, MSGD-1) does not beat it on any dataset; on HAI it is 11 points behind, because its threshold, calibrated right after a five-window adaptation, ends up higher than the static one and recall suffers (precision 0.65 versus 0.72, recall 0.33 versus 0.39). DAMAD sits between the two groups. On SMD it matches the static VAE's F1 with less than half the false-alarm rate (8.0 % versus 17.8 % of normal steps) and higher precision (0.30 versus 0.27); on SKAB and PSM it trades recall for precision (SKAB: precision 0.87 versus 0.80, recall 0.44 versus 0.62). The SKAB result has a specific cause. SKAB faults persist to the end of the run, the gate fires on the fault onset in 72 % of runs, and the adaptation that follows fits the fault; the acceptance test cannot undo it because the pre-fault regime never comes back. This is the SP3 confound in its worst case and no unsupervised rule resolves it. On PSM the high standard deviation (± 14.5) comes from one seed in which an early adaptation on a contaminated calibration window set a threshold the detector did not recover from.

Table 9 shows F1 against the number of support windows. The lines are flat: on no dataset does going from one to ten support windows move any method by more than two points, and on SKAB and HAI the adapt-once meta-learners sit on or below the static VAE at every K. The meta-learned initialisation is not the bottleneck in this problem. Five windows of a new entity are enough for any of these initialisations to reach the quality the small VAE can reach; what is left is the question of what to do afterwards.

Table 9. F1 (%) versus support-set size K on the original test streams.

| Method | SKAB 1 | SKAB 5 | SKAB 10 | SMD 1 | SMD 5 | SMD 10 | PSM 1 | PSM 5 | PSM 10 | HAI 1 | HAI 5 | HAI 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VAE-S | 64.2 | 64.1 | 63.6 | 29.4 | 29.4 | 29.4 | 59.3 | 59.3 | 59.3 | 32.7 | 32.7 | 32.7 |
| VAE-FT | 66.7 | 65.6 | 64.3 | 28.3 | 28.7 | 28.4 | 52.1 | 52.4 | 52.4 | 33.8 | 32.2 | 31.0 |
| MAML-1 | 64.1 | 64.1 | 63.2 | 26.3 | 26.1 | 26.2 | 53.3 | 52.6 | 51.5 | 22.4 | 21.7 | 21.2 |
| MSGD-1 | 64.2 | 64.0 | 63.2 | 26.8 | 26.6 | 26.7 | 53.3 | 53.6 | 52.7 | 22.1 | 21.6 | 21.1 |
| OML-A | 63.2 | 62.8 | 62.3 | 26.7 | 27.0 | 26.8 | 53.4 | 52.6 | 51.0 | 23.6 | 23.5 | 23.9 |
| DAMAD | 54.7 | 54.9 | 55.2 | 30.2 | 29.4 | 29.2 | 33.3 | 46.7 | 45.6 | 26.3 | 25.7 | 25.5 |

![Figure 3. F1 versus support-set size. Error bars are standard deviations over seeds. The dashed line is the static VAE, which uses no support set.](../figures/fig_shots.png){#fig:shots width=100%}

## 7.2 Streaming drift

Tables 10 to 12 report the drift conditions on SMD, PSM and HAI with K = 5, pooled and per dataset, and Figure 4 plots the pooled F1 and false-alarm rate. The false-alarm rate after the first change point (Table 11) is where the methods separate. Pooled over the three datasets, the static VAE alarms on 57--75 % of normal steps after a change; the meta-learned detectors adapted once do the same (58--68 %), and OML-A, which adapts on an MMD trigger but never moves its threshold, is barely better (54--63 %). On SMD and PSM the static group is at 73--100 %. These detectors have not failed to see the anomalies; they have stopped being able to say anything, because almost every step is above the threshold that was set in the first regime. The incrementally updated VAE sits in the middle (24--61 %), and is the best method under incremental drift, where a slow shift is exactly what one optimiser step every five windows can follow. The two drift-aware methods are the only ones that keep the rate low in every condition: 23--31 % for VAE-DFT and 16--25 % for DAMAD.

Table 10. Point-wise F1 (%) by drift condition, K = 5. "none" is the original stream. Pooled rows average SMD, PSM and HAI; SKAB is excluded from the drift conditions (Section 6.3).

| Method | pooled none | pooled sudden | pooled gradual | pooled incr. | pooled recur. | SMD sudden | SMD gradual | SMD incr. | SMD recur. |
|---|---|---|---|---|---|---|---|---|---|
| IF | 16.6 ± 3.6 | 11.3 ± 2.4 | 11.1 ± 2.2 | 11.2 ± 2.3 | 11.7 ± 2.8 | 11.2 ± 4.1 | 10.9 ± 3.7 | 11.5 ± 4.4 | 11.9 ± 4.6 |
| VAE-S | **45.8 ± 4.2** | 18.6 ± 2.0 | 17.9 ± 2.2 | 18.6 ± 2.2 | 19.3 ± 2.2 | 9.3 ± 3.7 | 9.6 ± 3.8 | 10.2 ± 3.7 | 10.7 ± 3.7 |
| VAE-FT | 45.8 ± 3.1 | 18.5 ± 2.3 | 17.8 ± 2.4 | 18.5 ± 2.8 | 19.1 ± 2.4 | 10.1 ± 4.2 | 10.1 ± 3.9 | 10.9 ± 4.2 | 11.5 ± 4.2 |
| VAE-INC | 41.4 ± 2.3 | 17.0 ± 1.6 | **23.1 ± 3.3** | **25.7 ± 2.3** | 20.5 ± 3.8 | 11.1 ± 4.0 | 18.2 ± 5.0 | **23.9 ± 4.1** | 14.0 ± 6.1 |
| VAE-DFT | 36.1 ± 3.0 | 19.7 ± 3.8 | 20.2 ± 3.2 | 21.3 ± 2.2 | 21.7 ± 4.7 | 21.9 ± 5.7 | 19.6 ± 4.6 | 16.8 ± 4.1 | 22.0 ± 7.1 |
| MAML-1 | 42.1 ± 3.3 | 20.1 ± 2.2 | 20.1 ± 3.3 | 17.5 ± 2.3 | 20.8 ± 3.2 | 10.1 ± 4.0 | 10.4 ± 4.2 | 11.1 ± 4.2 | 11.3 ± 4.0 |
| MSGD-1 | 42.3 ± 3.4 | 18.8 ± 2.9 | 18.6 ± 5.0 | 17.3 ± 2.3 | 20.4 ± 3.7 | 11.0 ± 5.2 | 11.1 ± 5.2 | 11.1 ± 4.2 | 11.9 ± 4.8 |
| OML-A | 42.2 ± 3.1 | 20.8 ± 2.1 | 20.2 ± 3.4 | 19.5 ± 2.7 | 21.0 ± 3.3 | 10.7 ± 4.2 | 10.7 ± 4.4 | 11.5 ± 4.9 | 11.8 ± 4.1 |
| DAMAD | 40.0 ± 3.8 | **24.3 ± 2.5** | 23.0 ± 3.5 | 20.0 ± 1.3 | **26.5 ± 2.5** | **24.6 ± 5.8** | **20.3 ± 1.3** | 21.2 ± 1.7 | **23.9 ± 4.4** |

Table 11. False-alarm rate (%) on normal steps after the first change point, K = 5. Lower is better.

| Method | pooled sudden | pooled gradual | pooled incr. | pooled recur. | SMD sudden | SMD recur. | PSM sudden | PSM recur. | HAI sudden | HAI recur. |
|---|---|---|---|---|---|---|---|---|---|---|
| IF | 71.0 ± 3.2 | 67.5 ± 3.6 | 68.5 ± 5.5 | 56.1 ± 5.5 | 77.8 ± 2.4 | 64.2 ± 5.0 | 97.7 ± 4.1 | 82.6 ± 7.7 | 54.8 ± 5.7 | 37.9 ± 11.8 |
| VAE-S | 74.1 ± 3.1 | 71.9 ± 3.2 | 65.2 ± 2.7 | 57.2 ± 2.1 | 94.3 ± 5.8 | 73.3 ± 3.7 | 100.0 ± 0.0 | 92.1 ± 0.8 | 36.4 ± 5.1 | 24.6 ± 6.2 |
| VAE-FT | 75.0 ± 3.1 | 72.3 ± 3.6 | 65.5 ± 3.2 | 58.5 ± 2.6 | 94.9 ± 6.1 | 74.4 ± 3.7 | 100.0 ± 0.0 | 95.7 ± 1.6 | 38.4 ± 3.2 | 25.5 ± 5.6 |
| VAE-INC | 61.3 ± 6.2 | 40.1 ± 10.0 | **23.9 ± 0.7** | 43.7 ± 6.1 | 78.3 ± 10.1 | 54.7 ± 10.6 | 100.0 ± 0.0 | 100.0 ± 0.0 | 26.4 ± 6.2 | **14.8 ± 0.5** |
| VAE-DFT | 29.9 ± 8.7 | 25.8 ± 7.9 | 31.2 ± 2.3 | 22.6 ± 7.1 | 25.1 ± 14.4 | 22.9 ± 7.8 | 55.6 ± 22.7 | 34.9 ± 21.4 | 32.3 ± 7.9 | 19.7 ± 6.5 |
| MAML-1 | 68.1 ± 2.8 | 66.3 ± 4.5 | 64.2 ± 3.3 | 58.0 ± 2.3 | 93.1 ± 5.6 | 76.8 ± 3.9 | 100.0 ± 0.0 | 99.3 ± 0.6 | **21.6 ± 2.3** | 19.6 ± 2.7 |
| MSGD-1 | 66.8 ± 6.3 | 65.6 ± 7.6 | 64.2 ± 4.1 | 57.5 ± 4.9 | 90.0 ± 10.4 | 74.7 ± 7.2 | 100.0 ± 0.0 | 99.4 ± 1.0 | 23.2 ± 2.4 | 21.7 ± 4.7 |
| OML-A | 63.4 ± 5.0 | 62.8 ± 5.1 | 58.5 ± 3.3 | 53.8 ± 2.8 | 85.3 ± 9.3 | 71.0 ± 4.1 | 100.0 ± 0.0 | 99.5 ± 0.4 | 21.1 ± 1.9 | 17.1 ± 2.1 |
| DAMAD | **22.7 ± 3.0** | **24.0 ± 7.4** | 24.9 ± 4.3 | **15.7 ± 2.1** | **17.5 ± 7.6** | **13.5 ± 5.1** | **20.6 ± 12.3** | **30.7 ± 9.6** | 31.5 ± 8.4 | 16.1 ± 4.8 |

Table 12. Adaptation steps (windows after a change point until the rolling false-alarm rate is back at the pre-drift level plus five points; capped at the segment length) and the share of change points from which the detector recovered at all.

| Method | pooled sudden | pooled gradual | pooled incr. | pooled recur. | SMD sudden | PSM sudden | HAI sudden | recovered (%) |
|---|---|---|---|---|---|---|---|---|
| IF | 3041 ± 259 | 775 ± 209 | 573 ± 472 | 2018 ± 275 | 3726 ± 549 | 6323 ± 2387 | 1287 ± 355 | – |
| VAE-S | 3305 ± 471 | 1558 ± 566 | 585 ± 269 | 2081 ± 167 | 4790 ± 819 | 2810 ± 3 | 1028 ± 47 | 80 |
| VAE-FT | 3319 ± 491 | 1614 ± 436 | 683 ± 276 | 2081 ± 169 | 4815 ± 852 | 2805 ± 6 | 1028 ± 47 | – |
| VAE-INC | 3182 ± 517 | 1019 ± 482 | **122 ± 22** | 1896 ± 216 | 4102 ± 924 | 7397 ± 2 | 867 ± 80 | 85 |
| VAE-DFT | **559 ± 202** | 284 ± 116 | 201 ± 110 | 478 ± 192 | **584 ± 382** | 796 ± 1118 | **471 ± 87** | 97 |
| MAML-1 | 3076 ± 540 | 1745 ± 469 | 1273 ± 655 | 2114 ± 176 | 4543 ± 946 | 2788 ± 6 | 787 ± 6 | – |
| MSGD-1 | 2985 ± 662 | 1744 ± 392 | 1316 ± 363 | 2066 ± 292 | 4372 ± 1141 | 2789 ± 13 | 805 ± 42 | – |
| OML-A | 2910 ± 652 | 1718 ± 399 | 801 ± 609 | 1902 ± 207 | 4253 ± 1143 | 2793 ± 8 | 785 ± 4 | 83 |
| DAMAD | 619 ± 197 | **277 ± 143** | 186 ± 122 | **350 ± 139** | 697 ± 359 | **394 ± 92** | 539 ± 200 | 98 |

Recovery time tells the same story from the other side (Table 12). After a sudden change the static group needs 3,000--3,300 windows pooled, and on SMD close to 4,800, which is to say it never recovers within the segment; the value is the cap. DAMAD recovers in 190--620 windows depending on the pattern, VAE-DFT in 200--560, and both recover from 97--98 % of change points against 80--85 % for the rest. The adaptation itself takes twelve milliseconds; the time is spent waiting for five support windows and three hundred calibration windows, which is the price of setting a threshold without labels.

F1 under drift (Table 10) follows from the false-alarm rate but less cleanly, because F1 also rewards recall and the static detectors have plenty of it: pooled under drift, the static VAE has recall 0.71 against DAMAD's 0.55, bought with a 67 % false-alarm rate against 22 %. Pooled over datasets DAMAD has the best F1 under sudden (24.3) and recurring (26.5) drift, the incremental VAE under gradual (23.1) and incremental (25.7) drift, with DAMAD second in both. On SMD DAMAD is first under three of the four patterns and more than doubles the static VAE's F1 in all four (24.6 versus 9.3 under sudden drift). On PSM every method sits near the F1 that alarming on everything would score (44 %, Section 8.3), which makes F1 uninformative there and the false-alarm rate the number to read: 100 % for the static group, 21--33 % for DAMAD. On HAI the picture is different. The injected shift raises the static VAE's false-alarm rate only to 25--36 %, because the threshold set on the first regime of an HAI campaign is already high relative to the shifted residual, and DAMAD's false-alarm rate (16--32 %) is not better. MAML-1 and OML-A have the best HAI F1 under drift (30--31) and DAMAD the worst of the VAE group under incremental drift (14.5), where each of its one to two adaptations recalibrated the threshold upward on a window that contained an attack. HAI is the dataset on which the method helps least, and it is the most industrial of the four.

![Figure 4. Pooled point-wise F1 (left) and false-alarm rate after drift (right) by drift condition, K = 5. Error bars are standard deviations over seeds.](../figures/fig_drift.png){#fig:drift width=100%}

Detection latency is the one streaming metric on which DAMAD is worse. Pooled over the drift conditions the static and adapt-once detectors raise their first alarm three windows into an anomaly segment, VAE-DFT five to seven, DAMAD seven to eight; and DAMAD detects 77--79 % of segments against 85--88 % for the static group. Both follow from the recalibrated threshold being higher than a threshold set once on a quiet first regime. An operator who wants the earliest possible alarm and can live with alarms on most normal steps after a change should use the static detector; one who needs the alarm stream to stay meaningful after a change cannot.

Figure 5 shows one SMD stream under sudden drift. After the first change point the static VAE's residual sits permanently above its threshold. VAE-DFT and DAMAD both adapt within a few hundred windows and raise their thresholds; DAMAD does so with fewer adaptations and a threshold that tracks the regime level, and its residual trace keeps the labelled anomaly bursts visible above it. Figures 6 and 7 show the same for PSM and HAI; on HAI the threshold set after the second adaptation is visibly high, which is what the F1 numbers reflect.

![Figure 5. SMD machine-1-3 under sudden drift: log residual, threshold and alarms for the static VAE, drift-aware fine-tuning and DAMAD. Dotted lines are injected change points, red lines adaptation events, shaded bands labelled anomalies, grey the warm-up.](../figures/fig_trace_smd_sudden.png){#fig:trace_smd width=100%}

![Figure 6. PSM under sudden drift, same layout as Figure 5.](../figures/fig_trace_psm_sudden.png){#fig:trace_psm width=100%}

![Figure 7. HAI test campaign 1 under sudden drift, same layout as Figure 5.](../figures/fig_trace_hai_sudden.png){#fig:trace_hai width=100%}

## 7.3 Ablations

Table 13 removes or replaces one element of DAMAD at a time under the four drift conditions pooled, per dataset, and Figure 8 shows the pooled picture. Two components carry the result. Without threshold recalibration (noM4) the false-alarm rate goes to 67 % on SMD and 98 % on PSM and recovery takes 1,700--3,000 windows, which is the static detector's behaviour with extra steps; the adaptation of the model alone does not help if the threshold stays where it was. With MMD as the only gate (−mmd) the numbers are nearly as bad (66 % and 88 %), because the embedding statistic does not fire on the injected changes reliably and the detector then behaves as if it had no gate. Adding MMD to the residual gate (+mmd) is slightly worse than the residual gate alone on every dataset (F1 20.0 versus 22.5 on SMD, 13.9 versus 21.2 on HAI), which is what motivated dropping it from the method.

Table 13. Ablations under the four drift patterns pooled, K = 5: F1 (%), false-alarm rate after drift (%) and adaptation steps.

| Variant | F1 SMD | F1 PSM | F1 HAI | FPR SMD | FPR PSM | FPR HAI | Steps SMD | Steps PSM | Steps HAI |
|---|---|---|---|---|---|---|---|---|---|
| DAMAD | 22.5 ± 2.6 | 42.1 ± 11.8 | 21.2 ± 3.2 | 18.0 ± 3.0 | 26.7 ± 2.7 | 27.0 ± 6.5 | 362 ± 145 | 618 ± 476 | 300 ± 57 |
| random episodes (rndM1) | 22.8 ± 3.6 | 41.9 ± 9.2 | **29.5 ± 4.5** | 18.4 ± 3.5 | 30.3 ± 1.5 | **16.4 ± 8.3** | 345 ± 112 | 780 ± 356 | 292 ± 123 |
| chunk episodes (noM1) | 20.9 ± 1.7 | 36.2 ± 12.7 | 20.0 ± 2.4 | 18.8 ± 3.9 | 26.4 ± 8.7 | 26.8 ± 3.5 | 406 ± 146 | 398 ± 353 | 338 ± 27 |
| ADWIN + MMD gate (+mmd) | 20.0 ± 1.3 | 39.3 ± 5.4 | 13.9 ± 2.5 | 21.5 ± 4.7 | 32.5 ± 2.9 | 29.1 ± 3.2 | 596 ± 268 | 571 ± 248 | 379 ± 56 |
| MMD-only gate (−mmd) | 12.6 ± 3.3 | 42.7 ± 4.9 | 14.7 ± 5.0 | 66.0 ± 4.1 | 88.0 ± 9.5 | 30.8 ± 7.3 | 2128 ± 493 | 1827 ± 1082 | 412 ± 86 |
| no replay (noM3) | 22.0 ± 3.2 | 38.7 ± 14.8 | 21.0 ± 2.5 | 24.0 ± 1.5 | 27.4 ± 9.6 | 27.6 ± 5.1 | 384 ± 120 | 498 ± 588 | 305 ± 62 |
| no τ recalibration (noM4) | 13.6 ± 4.6 | **46.5 ± 1.8** | 28.3 ± 2.8 | 67.3 ± 9.0 | 98.2 ± 1.5 | 19.5 ± 0.7 | 1714 ± 711 | 2970 ± 227 | 537 ± 20 |
| no acceptance test (noAcc) | 23.0 ± 2.7 | 28.7 ± 4.7 | 20.0 ± 3.0 | **15.3 ± 2.2** | 22.3 ± 9.7 | 27.6 ± 4.3 | 277 ± 41 | **204 ± 81** | 295 ± 52 |
| FOMAML init (fo) | **24.3 ± 4.5** | 26.6 ± 8.1 | 27.5 ± 3.4 | 16.2 ± 4.1 | **18.2 ± 8.1** | 18.0 ± 3.2 | **269 ± 64** | 470 ± 540 | **230 ± 68** |
| Meta-SGD init (msgd) | 22.6 ± 3.2 | 33.8 ± 9.6 | 20.3 ± 2.3 | 21.7 ± 3.2 | 35.3 ± 16.0 | 26.2 ± 4.3 | 472 ± 155 | 781 ± 751 | 311 ± 57 |

The rest of the ablations are within seed noise or go the wrong way on one dataset, and we report them as such. Replay (noM3) changes F1 by less than a point; its one visible effect is a lower false-alarm rate on SMD (18 % with replay, 24 % without), which is consistent with a refreshed initialisation adapting more cleanly to a regime that resembles an earlier one, but the effect is small. The episode sampler makes no difference on SMD or PSM, and on HAI the regime-free random sampler is better (F1 29.5 versus 21.2). We read this as a sign that HAI's training campaigns are stationary enough that cutting them into 400-step regimes only reduces episode diversity; the ADWIN-bounded sampler is not harmful, but we cannot claim that it helps. The acceptance test is the component whose value depends on the dataset: on SMD removing it costs nothing (F1 23.0 versus 22.5, false-alarm rate 15 % versus 18 %), on PSM, where 28 % of steps are anomalous and the gate fires eight to fifteen times per run, removing it drops F1 from 42.1 to 28.7 because adaptations on anomalous windows are kept. The initialisation variants are a wash: FOMAML is better than MAML++ on SMD and HAI and much worse on PSM, Meta-SGD is close to MAML++ everywhere. Given the flat shot curves in Section 7.1 this is not surprising. For a VAE of this size the initialisation is not where the problem is.

![Figure 8. Ablations under drift, pooled over SMD, PSM and HAI. The full method is in red.](../figures/fig_ablation.png){#fig:ablation width=100%}

## 7.4 Gate behaviour

Under drift DAMAD confirms 3.7 changes per run on average and rejects 1.0 of them in the shadow period, so about a quarter of the adaptations it tries are undone. On the original streams the rate is 0.5 confirmations per run on HAI, 0.7 on SKAB, 3.0 on SMD and 8.4 on PSM. The SMD and PSM figures are not false positives in any useful sense: those streams carry their own regime changes (Figure 5 shows two in the first 8,000 windows of an SMD machine before any injection), and the comparison with the static detector's 18 % and 38 % false-alarm rates on the same streams says that adapting to them was the right call. Each confirmed change costs about 0.9 s of meta-update time on one CPU core; the adaptation itself costs 12 ms.

## 7.5 Cost

Every VAE-based method scores a window in about 0.24 ms on one CPU core (Table 14), Isolation Forest in 0.02 ms. DAMAD's steady-state cost is the same as the static VAE's; the shadow period adds a second forward pass for 600 windows after each adaptation. The regime memory holds 107 kB on average. The incrementally updated VAE is the expensive one at 18 s of optimiser time per run, because it takes a gradient step every five windows for the whole stream. All models have 182 k parameters.

Table 14. Computational cost per run, K = 5, means over all runs on one CPU core.

| Method | ms / window | adaptation s / run | meta-update s / run | adaptations / run | memory kB |
|---|---|---|---|---|---|
| IF | 0.018 | 0.25 (fit) | 0 | 1 | 0 |
| VAE-S | 0.238 | 0 | 0 | 1 | 0 |
| VAE-FT | 0.239 | 0.12 | 0 | 1 | 0 |
| VAE-INC | 0.276 | 18.2 | 0 | – | 0 |
| VAE-DFT | 0.246 | 0.53 | 0 | 4.5 | 0 |
| MAML-1 | 0.235 | 0.01 | 0 | 1 | 0 |
| MSGD-1 | 0.237 | 0.01 | 0 | 1 | 0 |
| OML-A | 0.247 | 0.05 | 0 | 4.5 | 145 |
| DAMAD | 0.245 | 0.05 | 1.84 | 4.1 | 107 |
