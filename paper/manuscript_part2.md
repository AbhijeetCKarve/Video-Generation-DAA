
# 7 Results

All numbers are means ± standard deviations over five seeds. Within a seed, a value is first averaged over the held-out entities of a dataset; where a table pools datasets, the per-dataset values are then averaged with equal weight per dataset, so that SMAP's 17 held-out channels do not outvote SWaT's one stream. The complete tables, including every per-dataset, per-condition version, are in the repository; the ones reproduced here are the ones the text refers to. In total 19,650 streaming runs were scored.

## 7.1 Few-shot cold start without injected drift

Tables 8 and 9 give point-wise F1 at each method's own threshold and AUROC on the original test streams with K = 5. Two things stand out. AUROC is nearly flat across the VAE-based methods on every dataset: 85--87 % on SKAB, 82--87 % on SMD, 69--78 % on PSM, 94--95 % on HAI, 83--89 % on SWaT, 57--62 % on WADI, 57--61 % on SMAP and 60--62 % on MSL. The ranking of raw scores does not depend much on how the model was initialised or whether it adapts. What differs is F1, and F1 is decided by the threshold and by what the detector does after the first few hundred windows.

Table 8. Cold start on held-out entities, no injected drift, K = 5: point-wise F1 (%) at the deployed threshold. Best per column in bold.

| Method | SKAB | SMD | PSM | HAI | SWaT | WADI | SMAP | MSL |
|---|---|---|---|---|---|---|---|---|
| IF | 16.0 ± 4.7 | 18.3 ± 6.6 | 46.0 ± 1.9 | 9.1 ± 4.1 | 50.4 ± 4.9 | **27.1 ± 1.6** | 2.9 ± 1.7 | 10.8 ± 3.7 |
| VAE-S | 64.1 ± 5.9 | 29.4 ± 5.1 | **59.3 ± 2.1** | **32.7 ± 3.9** | 25.5 ± 0.3 | 11.1 ± 0.4 | **10.0 ± 4.1** | 8.9 ± 5.9 |
| VAE-FT | **65.6 ± 6.0** | 28.7 ± 4.6 | 52.4 ± 2.1 | 32.2 ± 4.0 | 25.4 ± 0.3 | 10.9 ± 0.2 | 7.3 ± 3.2 | 11.7 ± 7.9 |
| VAE-INC | 53.7 ± 2.4 | **32.9 ± 6.3** | 38.6 ± 0.7 | 31.1 ± 2.2 | **57.6 ± 0.5** | 10.7 ± 4.1 | 6.0 ± 4.7 | 7.5 ± 5.3 |
| VAE-DFT | 42.7 ± 6.4 | 29.4 ± 3.2 | 43.5 ± 9.0 | 32.1 ± 4.5 | 30.4 ± 10.9 | 21.0 ± 4.1 | 7.1 ± 1.5 | **12.3 ± 9.3** |
| MAML-1 | 64.1 ± 4.9 | 26.1 ± 5.3 | 52.6 ± 0.9 | 21.7 ± 1.0 | 25.7 ± 0.3 | 12.2 ± 1.4 | 7.8 ± 5.6 | 10.9 ± 6.5 |
| MSGD-1 | 64.0 ± 5.1 | 26.6 ± 4.5 | 53.6 ± 2.6 | 21.6 ± 0.4 | 25.4 ± 0.2 | 12.4 ± 2.0 | 7.0 ± 4.8 | 10.9 ± 5.8 |
| OML-A | 62.8 ± 4.5 | 27.0 ± 5.2 | 52.6 ± 1.6 | 23.5 ± 1.4 | 26.1 ± 0.6 | 12.4 ± 1.4 | 5.0 ± 3.4 | 11.2 ± 7.5 |
| DAMAD | 54.9 ± 4.8 | 29.4 ± 3.5 | 46.7 ± 14.5 | 25.7 ± 5.0 | 55.5 ± 3.0 | 15.9 ± 6.9 | 7.0 ± 5.0 | 11.3 ± 7.5 |

Table 9. Cold start, no injected drift, K = 5: AUROC (%).

| Method | SKAB | SMD | PSM | HAI | SWaT | WADI | SMAP | MSL |
|---|---|---|---|---|---|---|---|---|
| IF | **86.8 ± 4.6** | 79.7 ± 2.2 | 69.1 ± 2.4 | 73.0 ± 1.8 | 83.9 ± 0.3 | **73.6 ± 2.0** | 60.5 ± 3.7 | 59.6 ± 5.9 |
| VAE-S | 85.3 ± 3.0 | 84.1 ± 3.9 | **77.7 ± 0.9** | **94.9 ± 0.1** | 86.3 ± 0.1 | 58.2 ± 1.3 | 59.3 ± 5.6 | 59.7 ± 6.2 |
| VAE-FT | 86.7 ± 3.5 | 84.6 ± 4.7 | 73.3 ± 1.6 | 94.2 ± 0.2 | 86.1 ± 0.2 | 56.9 ± 1.7 | 60.4 ± 2.3 | 59.9 ± 7.4 |
| VAE-INC | 80.2 ± 3.0 | **86.7 ± 3.2** | 57.6 ± 0.9 | 94.8 ± 0.2 | **89.1 ± 0.2** | 56.5 ± 9.2 | 57.6 ± 8.3 | 60.5 ± 7.3 |
| VAE-DFT | 75.2 ± 3.1 | 81.8 ± 3.8 | 70.6 ± 3.6 | 94.3 ± 0.2 | 82.7 ± 6.2 | 62.4 ± 0.8 | 57.2 ± 6.2 | **61.8 ± 7.9** |
| MAML-1 | 85.8 ± 3.1 | 84.4 ± 4.5 | 76.3 ± 1.5 | 93.8 ± 0.4 | 85.7 ± 0.3 | 59.4 ± 0.4 | 59.0 ± 6.5 | 59.9 ± 6.5 |
| MSGD-1 | 85.8 ± 3.0 | 84.6 ± 4.3 | 75.3 ± 0.4 | 93.6 ± 0.2 | 85.5 ± 0.2 | 58.8 ± 0.4 | **60.5 ± 5.8** | 60.0 ± 6.6 |
| OML-A | 85.4 ± 3.0 | 84.6 ± 4.1 | 75.7 ± 2.0 | 94.2 ± 0.4 | 85.0 ± 0.6 | 59.7 ± 0.4 | 59.7 ± 6.0 | 60.8 ± 6.9 |
| DAMAD | 85.8 ± 3.1 | 82.9 ± 4.5 | 69.4 ± 6.3 | 94.1 ± 0.1 | 86.8 ± 1.1 | 59.1 ± 1.4 | 58.1 ± 7.4 | 61.0 ± 6.8 |

The datasets fall into two groups. On SKAB, SMD, PSM and HAI the static VAE is as good as anything else and better than the meta-learned detectors on PSM and HAI. The meta-learned initialisation adapted once (MAML-1, MSGD-1) does not beat it on any of them; on HAI it is 11 points behind, because its threshold, calibrated right after a five-window adaptation, ends up higher than the static one and recall suffers (precision 0.65 versus 0.72, recall 0.33 versus 0.39). DAMAD sits between the two groups: on SMD it matches the static VAE's F1 with less than half the false-alarm rate (8.0 % versus 17.8 % of normal steps), on SKAB and PSM it trades recall for precision (SKAB: precision 0.87 versus 0.80, recall 0.44 versus 0.62). The SKAB result has a specific cause. SKAB faults persist to the end of the run, the gate fires on the fault onset in 72 % of runs, and the adaptation that follows fits the fault; the acceptance test cannot undo it because the pre-fault regime never comes back. This is the SP3 confound in its worst case and no unsupervised rule resolves it.

SWaT and WADI are the other group, and they are the datasets this paper is about. Their attack recordings were made days after their normal recordings, at different operating points, so the test stream *is* a drifted stream even before anything is injected. On the original SWaT stream the static VAE, both adapt-once meta-learners and the fine-tuned VAE alarm on 72--74 % of normal steps; on WADI on 49--57 %. Every one of them scores F1 ≈ 25 on SWaT and ≈ 11--12 on WADI, which is what alarming on most of the stream scores at those anomaly rates. DAMAD confirms 5.4 regime changes per SWaT run and 2.2 per WADI run on the original streams, brings the false-alarm rate down to 4.0 % and 6.4 %, and reaches F1 55.5 on SWaT (AUROC 86.8 %) against 25.5 for the static VAE, and 15.9 on WADI against 11.1. The incrementally updated VAE also copes with SWaT's shift (57.6, false-alarm rate 12 %) because the shift is slow enough for one gradient step every five windows to follow, but it does not cope with WADI's (10.7, 32 %). Isolation Forest, which has no threshold tied to a reconstruction model, is the best method on WADI (27.1) and second on SWaT; its advantage is that its score distribution moves less than a reconstruction residual does when the operating point changes.

SMAP and MSL are a third case, and a caution. Every method, including Isolation Forest, is weak on them: AUROC 57--62 %, point-wise F1 3--12 %, oracle-threshold F1 25--33 %. The telemetry channels of these datasets are one physical value plus 24 or 54 binary command flags, and a reconstruction model on eight-step windows of that input is not a good detector for them; the methods that do well on SMAP/MSL in the literature are sequence predictors with long context [@hundman2018smap]. We keep the two datasets because the drift behaviour of the methods is still informative there, but we do not read the absolute F1 numbers on them as meaning much.

Table 10 shows F1 against the number of support windows, and Figure 3 plots it. The lines are flat: on no dataset does going from one to ten support windows move any adapt-once method by more than two points, and on SKAB, PSM and HAI the adapt-once meta-learners sit on or below the static VAE at every K. The meta-learned initialisation is not the bottleneck in this problem. Five windows of a new entity are enough for any of these initialisations to reach the quality the small VAE can reach; what is left is the question of what to do afterwards. DAMAD is the only line that moves with K on SWaT and WADI (55 → 59 and 15 → 18), and that movement comes from its later adaptations, not the first one.

Table 10. F1 (%) at K = 1 / 5 / 10 support windows on the original test streams.

| Method | SKAB | SMD | PSM | HAI | SWaT | WADI | SMAP | MSL |
|---|---|---|---|---|---|---|---|---|
| VAE-S | 64 / 64 / 64 | 29 / 29 / 29 | 59 / 59 / 59 | 33 / 33 / 33 | 25 / 25 / 26 | 11 / 11 / 11 | 10 / 10 / 10 | 7 / 9 / 9 |
| VAE-FT | 67 / 66 / 64 | 28 / 29 / 28 | 52 / 52 / 52 | 34 / 32 / 31 | 26 / 25 / 26 | 11 / 11 / 11 | 6 / 7 / 7 | 9 / 12 / 12 |
| MAML-1 | 64 / 64 / 63 | 26 / 26 / 26 | 53 / 53 / 52 | 22 / 22 / 21 | 26 / 26 / 26 | 12 / 12 / 12 | 8 / 8 / 8 | 9 / 11 / 11 |
| MSGD-1 | 64 / 64 / 63 | 27 / 27 / 27 | 53 / 54 / 53 | 22 / 22 / 21 | 25 / 25 / 26 | 13 / 12 / 12 | 8 / 7 / 6 | 10 / 11 / 11 |
| OML-A | 63 / 63 / 62 | 27 / 27 / 27 | 53 / 53 / 51 | 24 / 23 / 24 | 26 / 26 / 27 | 13 / 12 / 15 | 4 / 5 / 5 | 10 / 11 / 11 |
| DAMAD | 55 / 55 / 55 | 30 / 29 / 29 | 33 / 47 / 46 | 26 / 26 / 25 | 55 / 55 / 59 | 15 / 16 / 18 | 4 / 7 / 4 | 10 / 11 / 11 |

![Figure 3. F1 versus support-set size on the original streams. Error bars are standard deviations over seeds; the dashed line is the static VAE, which uses no support set.](../figures/fig_shots.png){#fig:shots width=100%}

## 7.2 Streaming drift

Tables 11 to 13 report the drift conditions on the seven datasets that are long enough for them, with K = 5, pooled by condition and per dataset averaged over the four patterns; Figure 4 plots the pooled F1 and false-alarm rate. The false-alarm rate after the first change point (Table 12) is where the methods separate. Pooled over datasets, the static VAE alarms on 75--87 % of normal steps after a change; the meta-learned detectors adapted once do the same (73--83 %), and OML-A, which adapts on an MMD trigger but never moves its threshold, is barely better (72--81 %). On SWaT, WADI and PSM the whole static group is at 95--100 %. These detectors have not failed to see the anomalies; they have stopped being able to say anything, because almost every step is above the threshold that was set in the first regime. The incrementally updated VAE sits in the middle (44--82 %), and is the best method under incremental drift on four datasets, where a slow shift is exactly what one optimiser step every five windows can follow. The two drift-aware methods are the only ones that keep the rate low in every condition: 21--33 % for VAE-DFT and 17--30 % for DAMAD. Per dataset, DAMAD has the lowest rate on SMD, PSM, SWaT and WADI (11--27 %), VAE-DFT on SMAP and MSL, and the incremental VAE on HAI.

Table 11. Point-wise F1 (%) under drift, K = 5. Left: pooled over the seven datasets by condition ("none" is the original stream). Right: per dataset, averaged over the four drift patterns.

| Method | none | sudden | gradual | incr. | recur. | SMD | PSM | HAI | SWaT | WADI | SMAP | MSL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IF | 23.5 ± 1.7 | 21.0 ± 1.7 | 21.5 ± 1.8 | 20.6 ± 1.5 | 20.4 ± 1.5 | 11.4 ± 4.2 | 39.4 ± 0.6 | 5.7 ± 0.5 | 36.3 ± 2.6 | 16.9 ± 2.1 | 11.6 ± 2.6 | 24.9 ± 8.8 |
| VAE-S | 25.3 ± 1.5 | 23.7 ± 1.9 | 22.9 ± 2.0 | 24.4 ± 2.3 | 22.2 ± 1.7 | 10.0 ± 3.7 | 46.0 ± 1.6 | 27.0 ± 1.5 | 25.5 ± 0.2 | 12.1 ± 0.1 | **17.3 ± 4.0** | 25.2 ± 8.7 |
| VAE-FT | 24.1 ± 1.3 | 23.1 ± 2.0 | 22.7 ± 2.0 | 24.4 ± 2.4 | 21.8 ± 1.7 | 10.6 ± 4.1 | 45.3 ± 1.3 | 25.7 ± 1.8 | 25.5 ± 0.4 | 12.1 ± 0.1 | 16.5 ± 3.8 | 25.3 ± 8.8 |
| VAE-INC | 26.4 ± 0.8 | 22.2 ± 1.5 | 23.1 ± 2.2 | 22.0 ± 1.9 | 22.1 ± 2.0 | 16.8 ± 4.2 | 38.8 ± 2.1 | 25.8 ± 2.9 | 29.5 ± 0.1 | 11.9 ± 0.0 | 12.4 ± 4.1 | 21.2 ± 8.5 |
| VAE-DFT | 25.1 ± 2.4 | 24.3 ± 4.5 | 23.8 ± 3.1 | 26.1 ± 1.7 | 24.1 ± 2.6 | 20.1 ± 5.0 | 40.6 ± 6.7 | 17.7 ± 2.3 | 39.9 ± 7.7 | **20.1 ± 1.1** | 12.4 ± 3.3 | 21.4 ± 6.0 |
| MAML-1 | 22.4 ± 1.6 | 23.9 ± 2.0 | 23.8 ± 2.3 | 23.8 ± 2.2 | 22.7 ± 1.6 | 10.7 ± 4.1 | 47.8 ± 0.4 | 28.2 ± 3.1 | 25.5 ± 0.3 | 12.1 ± 0.1 | 15.2 ± 4.6 | 25.3 ± 8.8 |
| MSGD-1 | 22.5 ± 1.4 | 23.3 ± 1.8 | 23.1 ± 2.7 | 23.7 ± 2.3 | 22.4 ± 1.8 | 11.3 ± 4.8 | 47.3 ± 0.5 | 25.1 ± 4.1 | 25.3 ± 0.1 | 12.2 ± 0.1 | 15.2 ± 4.7 | 25.4 ± 8.8 |
| OML-A | 22.5 ± 1.4 | 24.1 ± 1.7 | 23.8 ± 2.4 | 24.5 ± 2.1 | 22.7 ± 1.6 | 11.2 ± 4.4 | **47.8 ± 0.9** | **29.6 ± 2.9** | 25.8 ± 0.5 | 11.9 ± 0.5 | 14.8 ± 5.0 | **25.4 ± 8.8** |
| DAMAD | **27.3 ± 3.3** | **26.7 ± 4.5** | **25.5 ± 5.0** | **26.5 ± 2.9** | **26.6 ± 3.2** | **22.5 ± 2.6** | 42.1 ± 11.8 | 21.2 ± 3.2 | **52.4 ± 6.7** | 18.5 ± 4.2 | 11.3 ± 3.6 | 16.3 ± 4.0 |

Table 12. False-alarm rate (%) on normal steps after the first change point, K = 5. Lower is better. Same layout as Table 11.

| Method | sudden | gradual | incr. | recur. | SMD | PSM | HAI | SWaT | WADI | SMAP | MSL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IF | 70.4 ± 3.9 | 65.9 ± 2.8 | 70.1 ± 3.3 | 54.2 ± 2.9 | 73.0 ± 2.9 | 88.2 ± 4.9 | 49.7 ± 9.2 | 52.4 ± 7.8 | 58.9 ± 12.2 | 43.1 ± 20.4 | 90.6 ± 0.8 |
| VAE-S | 86.8 ± 1.3 | 84.6 ± 1.3 | 78.3 ± 1.5 | 74.6 ± 1.2 | 85.2 ± 5.0 | 97.2 ± 0.2 | 32.1 ± 3.6 | 100.0 ± 0.0 | 96.8 ± 0.1 | 68.9 ± 3.7 | 87.2 ± 0.4 |
| VAE-FT | 86.8 ± 1.2 | 84.0 ± 1.5 | 77.4 ± 1.6 | 75.1 ± 1.1 | 85.8 ± 5.4 | 98.0 ± 0.7 | 32.9 ± 3.1 | 99.9 ± 0.1 | 96.9 ± 0.1 | 65.7 ± 3.8 | 86.5 ± 0.4 |
| VAE-INC | 82.4 ± 2.3 | 69.0 ± 4.0 | 43.9 ± 1.3 | 66.7 ± 2.2 | 50.2 ± 9.4 | 98.1 ± 0.0 | **18.3 ± 1.6** | 86.9 ± 0.2 | 95.1 ± 1.5 | 43.1 ± 3.0 | 66.7 ± 4.0 |
| VAE-DFT | 32.8 ± 7.9 | 28.0 ± 6.1 | **28.8 ± 8.0** | 20.8 ± 6.5 | 26.9 ± 8.2 | 48.1 ± 11.7 | 24.0 ± 2.5 | 14.6 ± 10.5 | 28.3 ± 16.5 | **18.1 ± 2.5** | **33.4 ± 7.7** |
| MAML-1 | 82.7 ± 1.2 | 80.3 ± 1.9 | 75.7 ± 1.0 | 73.4 ± 1.8 | 85.3 ± 5.4 | 99.4 ± 0.4 | 23.4 ± 1.2 | 99.8 ± 0.1 | 95.4 ± 1.5 | 56.6 ± 4.7 | 86.4 ± 0.3 |
| MSGD-1 | 82.3 ± 1.8 | 80.2 ± 2.7 | 75.6 ± 1.5 | 73.2 ± 2.7 | 83.1 ± 8.8 | 99.0 ± 1.4 | 25.0 ± 2.8 | 99.9 ± 0.1 | 94.8 ± 2.1 | 56.6 ± 4.1 | 86.3 ± 0.4 |
| OML-A | 81.0 ± 1.9 | 78.9 ± 2.1 | 73.0 ± 1.0 | 71.9 ± 2.0 | 79.9 ± 6.5 | 99.0 ± 0.9 | 19.3 ± 0.5 | 99.6 ± 0.3 | 94.3 ± 3.4 | 55.1 ± 4.6 | 86.2 ± 0.3 |
| DAMAD | **22.5 ± 5.6** | **22.8 ± 2.6** | 29.5 ± 5.7 | **16.7 ± 3.6** | **18.0 ± 3.0** | **26.7 ± 2.7** | 27.0 ± 6.5 | **11.4 ± 11.3** | **17.2 ± 10.4** | 19.1 ± 4.9 | 40.8 ± 4.6 |

Table 13. Adaptation steps (windows after a change point until the rolling false-alarm rate is back at the pre-drift level plus five points; capped at the segment length), pooled by condition and per dataset, and the share of change points recovered from at all (last column, pooled).

| Method | sudden | gradual | incr. | recur. | SMD | PSM | HAI | SWaT | WADI | SMAP | MSL | recovered (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IF | 1931 ± 296 | 403 ± 80 | 534 ± 152 | 1353 ± 313 | 2024 ± 107 | 2793 ± 1059 | 687 ± 152 | **163 ± 69** | **184 ± 75** | 832 ± 249 | 703 ± 132 | 85 |
| VAE-S | 2251 ± 145 | 1719 ± 154 | 929 ± 214 | 1918 ± 71 | 2552 ± 442 | 2904 ± 10 | 607 ± 24 | 2238 ± 673 | 2370 ± 1 | 796 ± 71 | 462 ± 55 | 78 |
| VAE-FT | 2249 ± 147 | 1753 ± 206 | 954 ± 210 | 1889 ± 43 | 2610 ± 292 | 2900 ± 26 | 632 ± 26 | 2260 ± 561 | 2371 ± 1 | 745 ± 84 | 462 ± 53 | 78 |
| VAE-INC | 2923 ± 140 | 1535 ± 518 | **111 ± 6** | 2357 ± 56 | 1913 ± 481 | 3742 ± 783 | 544 ± 20 | 2382 ± 219 | 2373 ± 0 | 726 ± 78 | 441 ± 45 | 81 |
| VAE-DFT | 512 ± 268 | 347 ± 119 | 422 ± 305 | 342 ± 127 | 393 ± 118 | 755 ± 517 | **285 ± 40** | 506 ± 389 | 417 ± 331 | 230 ± 29 | 253 ± 17 | 97 |
| MAML-1 | 2264 ± 193 | 1800 ± 145 | 1167 ± 211 | 1927 ± 101 | 2819 ± 399 | 3079 ± 136 | 620 ± 158 | 2677 ± 533 | 2272 ± 137 | 600 ± 45 | 459 ± 54 | 81 |
| MSGD-1 | 2168 ± 203 | 1688 ± 107 | 1115 ± 136 | 1813 ± 130 | 2696 ± 493 | 3037 ± 156 | 756 ± 195 | 2102 ± 339 | 2226 ± 134 | 596 ± 44 | 459 ± 55 | – |
| OML-A | 2223 ± 221 | 1792 ± 132 | 804 ± 298 | 1865 ± 137 | 2513 ± 562 | 2913 ± 496 | 528 ± 6 | 2459 ± 297 | 2239 ± 127 | 586 ± 47 | 459 ± 54 | 81 |
| DAMAD | **437 ± 96** | **264 ± 98** | 229 ± 253 | **279 ± 72** | **362 ± 145** | **618 ± 476** | 300 ± 57 | 208 ± 37 | 203 ± 128 | **206 ± 39** | **218 ± 18** | 98 |

Recovery time tells the same story from the other side (Table 13). After a sudden change the static group needs 2,200--2,300 windows pooled, and on SMD, PSM, SWaT and WADI 2,200--3,100, which is to say it never recovers within the segment; the value is the cap. DAMAD recovers in 230--440 windows depending on the pattern, VAE-DFT in 340--510, and both recover from 97--98 % of change points against 78--85 % for the rest. The adaptation itself takes eleven milliseconds; the time is spent waiting for five support windows and a calibration window, which is the price of setting a threshold without labels.

F1 under drift (Table 11) follows from the false-alarm rate but less cleanly, because F1 also rewards recall and the static detectors have plenty of it: pooled under drift, the static VAE has recall 0.76 against DAMAD's 0.43, bought with an 81 % false-alarm rate against 23 %. Pooled with equal weight per dataset DAMAD has the best F1 in every condition, 25.5--26.7 against 22.2--24.4 for the static VAE and 23.8--26.1 for VAE-DFT, but the per-dataset columns show where that comes from and where it does not. On SWaT DAMAD is first under every pattern (52.4 averaged, against 25.5 for the static group and 39.9 for VAE-DFT); on SMD first under three of four patterns and more than double the static VAE (22.5 versus 10.0); on WADI second to VAE-DFT (18.5 versus 20.1, both far above the 12 of the static group). On PSM, SMAP and MSL the static group has the higher F1, and in all three cases that F1 is the one alarming on most of the stream earns: 44 % on PSM, 20 % on SMAP, 25 % on MSL (Section 8.3), reached with false-alarm rates of 87--99 %. On HAI the injected shift raises the static VAE's false-alarm rate only to 32 %, because the threshold set on the first regime of an HAI campaign is already high relative to the shifted residual, and DAMAD's rate (27 %) is not much better while its recalibrated thresholds cost it recall (F1 21.2 against 27.0). HAI is the one industrial dataset on which the method brings no gain.

![Figure 4. Pooled point-wise F1 (left) and false-alarm rate after drift (right) by drift condition, K = 5, each dataset weighted equally. Error bars are standard deviations over seeds.](../figures/fig_drift.png){#fig:drift width=100%}

Detection latency is the streaming metric on which DAMAD is worst, and the eight-dataset view makes that plainer than the four-dataset one did. Averaged over drift patterns the static and adapt-once detectors raise their first alarm 2--6 windows into an anomaly segment on SMD, PSM, HAI, SWaT and WADI; DAMAD needs 9--31 windows there and 51--144 on the NASA channels, and it detects fewer segments (51--84 % against 80--97 % for the static group on the same datasets). Both follow from the recalibrated threshold being higher than a threshold set once on a quiet first regime; on SWaT and WADI, where DAMAD's threshold is recalibrated after every one of several confirmed changes, the segment detection rate is only 48--51 %. An operator who wants the earliest possible alarm and can live with alarms on most normal steps after a change should use the static detector; one who needs the alarm stream to stay meaningful after a change cannot. The trade is explicit and we do not hide it.

Figure 5 shows one SMD stream under sudden drift and Figure 6 the SWaT stream. After the first change point the static VAE's residual sits permanently above its threshold. VAE-DFT and DAMAD both adapt within a few hundred windows and raise their thresholds; DAMAD does so with fewer adaptations and a threshold that tracks the regime level, and its residual trace keeps the labelled anomaly bursts visible above it. On SWaT the long attack between windows 23,000 and 27,000 triggers an adaptation in both drift-aware methods, which then set the threshold at the attack level; the acceptance test does not undo it because by the time the shadow period ends the stream has moved on to a third level. This is the mechanism behind DAMAD's low segment detection rate on SWaT, and it is visible in the trace.

![Figure 5. SMD machine-1-3 under sudden drift: log residual, threshold and alarms for the static VAE, drift-aware fine-tuning and DAMAD. Dotted lines are injected change points, red lines adaptation events, shaded bands labelled anomalies, grey the warm-up.](../figures/fig_trace_smd_sudden.png){#fig:trace_smd width=100%}

![Figure 6. SWaT under sudden drift, same layout as Figure 5. The attack recording sits at a higher operating level than the normal recording from the start, which is why the static VAE's residual is above its threshold for most of the stream even before the injected change at window 15,700.](../figures/fig_trace_swat_sudden.png){#fig:trace_swat width=100%}

## 7.3 Ablations

Table 14 removes or replaces one element of DAMAD at a time under the four drift conditions, per dataset, and Figure 7 shows the pooled picture. Two components carry the result. Without threshold recalibration (noM4) the false-alarm rate goes to 67 % on SMD, 98 % on PSM, 96 % on SWaT, 80 % on WADI and 83 % on MSL, and recovery takes 1,700--3,000 windows on the industrial datasets, which is the static detector's behaviour with extra steps; the adaptation of the model alone does not help if the threshold stays where it was. With MMD as the only gate (−mmd) the numbers are nearly as bad on SMD, PSM and WADI (66 %, 88 %, 96 %), because the embedding statistic does not fire on the injected changes reliably and the detector then behaves as if it had no gate. Adding MMD to the residual gate (+mmd) is worse than the residual gate alone on five of the seven datasets in F1 and better on SWaT only, which is what motivated dropping it from the method.

Table 14. Ablations under the four drift patterns, K = 5, per dataset: F1 (%) and false-alarm rate after drift (%). Adaptation steps are in the repository tables.

| Variant | F1 SMD | F1 PSM | F1 HAI | F1 SWaT | F1 WADI | F1 SMAP | F1 MSL | FPR SMD | FPR PSM | FPR HAI | FPR SWaT | FPR WADI | FPR SMAP | FPR MSL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DAMAD | 22.5 | 42.1 | 21.2 | 52.4 | 18.5 | 11.3 | 16.3 | 18.0 | 26.7 | 27.0 | 11.4 | 17.2 | 19.1 | 40.8 |
| random episodes (rndM1) | 22.8 | 41.9 | **29.5** | 48.4 | 22.9 | 11.9 | 16.3 | 18.4 | 30.3 | **16.4** | 17.2 | 23.4 | 18.7 | 40.8 |
| chunk episodes (noM1) | 20.9 | 36.2 | 20.0 | 48.4 | 19.6 | 11.4 | 16.3 | 18.8 | 26.4 | 26.8 | 10.1 | 18.5 | 18.2 | 41.5 |
| ADWIN + MMD gate (+mmd) | 20.0 | 39.3 | 13.9 | 55.1 | 17.0 | 7.8 | 13.7 | 21.5 | 32.5 | 29.1 | 5.8 | 20.4 | **16.1** | **35.2** |
| MMD-only gate (−mmd) | 12.6 | 42.7 | 14.7 | 48.0 | 12.2 | 10.6 | 13.4 | 66.0 | 88.0 | 30.8 | 13.7 | 95.8 | 20.2 | 36.9 |
| no replay (noM3) | 22.0 | 38.7 | 21.0 | **61.3** | 18.2 | **12.8** | 16.1 | 24.0 | 27.4 | 27.6 | 4.9 | 28.5 | 23.2 | 41.9 |
| no τ recalibration (noM4) | 13.6 | **46.5** | 28.3 | 26.7 | 12.6 | 11.2 | **25.4** | 67.3 | 98.2 | 19.5 | 96.2 | 80.1 | 45.2 | 83.0 |
| no acceptance test (noAcc) | 23.0 | 28.7 | 20.0 | 58.8 | 16.4 | 11.7 | 16.0 | **15.3** | 22.3 | 27.6 | 9.3 | 17.3 | 19.0 | 40.8 |
| FOMAML init (fo) | **24.3** | 26.6 | 27.5 | 60.8 | **23.8** | 11.0 | 15.7 | 16.2 | **18.2** | 18.0 | **3.3** | **12.6** | 18.1 | 40.1 |
| Meta-SGD init (msgd) | 22.6 | 33.8 | 20.3 | 56.5 | 19.5 | 12.5 | 18.8 | 21.7 | 35.3 | 26.2 | 11.8 | 19.0 | 18.7 | 43.9 |

The rest of the ablations are within seed noise or go opposite ways on different datasets, and we report them as such. Replay (noM3) changes F1 by less than a point on five datasets, lowers the false-alarm rate on SMD (18 % with replay, 24 % without) and WADI (17 % versus 29 %), and on SWaT removing it is clearly better (F1 61.3 versus 52.4, false-alarm rate 4.9 % versus 11.4 %): on a stream with several confirmed changes in a row, refreshing $\theta^*$ from remembered regimes makes the next adaptation land somewhere between the old and the new regime, and on SWaT that is the wrong place. The episode sampler makes no difference on SMD, PSM, SWaT, SMAP or MSL, and on HAI and WADI the regime-free random sampler is better; the ADWIN-bounded sampler is not harmful, but we cannot claim that it helps. The acceptance test is the component whose value depends on the dataset: on SMD, SWaT and WADI removing it costs nothing or helps a little, on PSM, where 28 % of steps are anomalous and the gate fires twelve times per run, removing it drops F1 from 42.1 to 28.7 because adaptations on anomalous windows are kept. The initialisation variants are not a wash on the eight-dataset view: FOMAML beats MAML++ on SMD, HAI, SWaT and WADI in both F1 and false-alarm rate and loses badly on PSM (26.6 versus 42.1). We kept MAML++ as the reference because it is the more stable of the two during meta-training, but a reader who wants the smallest false-alarm rate on a water-treatment stream should take the FOMAML numbers.

![Figure 7. Ablations under drift, pooled over the seven datasets with equal weight. The full method is in red.](../figures/fig_ablation.png){#fig:ablation width=100%}

## 7.4 Gate behaviour

Under drift DAMAD confirms between 1.1 (MSL) and 12.2 (PSM) changes per run and rejects 1 % of them on the NASA channels, 29 % on SMD, 35 % on SWaT and 40 % on PSM in the shadow period. On the original streams the rate is 0.2 confirmations per run on SMAP and MSL, 0.5 on HAI, 0.7 on SKAB, 2.2 on WADI, 3.0 on SMD, 5.4 on SWaT and 8.4 on PSM. The SWaT, WADI, SMD and PSM figures are not false positives in any useful sense: those streams carry their own regime changes (Figure 6 shows SWaT's; Figure 5 shows two in the first 8,000 windows of an SMD machine before any injection), and the static detector's 73 %, 57 %, 18 % and 38 % false-alarm rates on the same streams say that adapting to them was the right call. Each confirmed change costs about 0.7 s of meta-update time on one CPU core; the adaptation itself costs 11 ms.

## 7.5 Cost

Every VAE-based method scores a window in 0.22--0.26 ms on one CPU core (Table 15), Isolation Forest in 0.01 ms. DAMAD's steady-state cost is the same as the static VAE's; the shadow period adds a second forward pass for a few hundred windows after each adaptation. The regime memory holds 71 kB on average. The incrementally updated VAE is the expensive one at 11 s of optimiser time per run, because it takes a gradient step every five windows for the whole stream. The model has 36 k parameters on SKAB and 273 k on WADI, set by the input width.

Table 15. Computational cost per run, K = 5, means over all runs on one CPU core.

| Method | ms / window | adaptation s / run | meta-update s / run | adaptations / run | memory kB |
|---|---|---|---|---|---|
| IF | 0.013 | 0.23 (fit) | 0 | 1 | 0 |
| VAE-S | 0.220 | 0 | 0 | 1 | 0 |
| VAE-FT | 0.222 | 0.11 | 0 | 1 | 0 |
| VAE-INC | 0.255 | 11.2 | 0 | – | 0 |
| VAE-DFT | 0.229 | 0.40 | 0 | 3.5 | 0 |
| MAML-1 | 0.219 | 0.01 | 0 | 1 | 0 |
| MSGD-1 | 0.220 | 0.01 | 0 | 1 | 0 |
| OML-A | 0.231 | 0.04 | 0 | 4.0 | 100 |
| DAMAD | 0.228 | 0.03 | 1.32 | 3.0 | 71 |
