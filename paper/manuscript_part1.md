---
title: "Drift-aware meta-adaptive anomaly detection for few-shot, non-stationary industrial IoT streams: a benchmarking protocol and the DAMAD detector"
author:
  - Abhijeet Chandrakant Karve^1^ (corresponding author, ackarve11@gmail.com)
  - Santosh Darade^1^
  - ^1^Department of Computer Science and Engineering, MIT Art, Design and Technology University, Pune, India
date: ""
bibliography: references.bib
csl: ieee.csl
link-citations: true
---

# Abstract {.unnumbered}

Sensor streams from industrial plants have to be watched for faults with almost no labelled examples, under distributions that keep moving, and with new fault types showing up after deployment. Meta-learning is built for the few-shot part of that problem, but a systematic review we carried out of 67 peer-reviewed papers (2020--2025) found no method that combines meta-learning with online adaptation on a non-stationary stream and is evaluated on an industrial benchmark. This paper closes that gap in three steps. First, we condense the review into a four-dimensional taxonomy of meta-learning anomaly detectors and a benchmarking protocol with strictly point-wise metrics, controlled drift injection, and three streaming measures (detection latency, adaptation steps, false-alarm rate under drift). Second, we build DAMAD, the Drift-Aware Meta-Adaptive Detector, as a working system: a MAML++-initialised variational autoencoder that adapts in K gradient steps when a regime change is confirmed, a regime-indexed memory that replays past regimes during meta-updates, a gated extreme-value threshold, and a champion/challenger check that undoes an adaptation if the old model turns out to fit the following data better. Building it changed two design decisions from our earlier conceptual sketch: the drift gate has to watch the model residual rather than the raw input, and a change has to be confirmed by the gain it brings, otherwise long anomalies masquerade as drift. Third, we run DAMAD against eight baselines (Isolation Forest, static, fine-tuned, incrementally updated and drift-aware VAEs, MAML and Meta-SGD adapted once, and an MMD-triggered meta-adapter) on eight benchmarks, SWaT, WADI, HAI 21.03, SMAP, MSL, SMD, SKAB and PSM, over five seeds, four drift patterns and ten ablations, 19,650 streaming runs in all. Without injected drift, the static VAE is as good as any meta-learned detector on six of the eight, and the number of support windows makes no difference between one and ten: the initialisation is not the bottleneck. SWaT and WADI are the exception, because their attack recordings sit at a different operating point from their normal recordings: there the static and adapt-once detectors alarm on 49--74 % of normal steps and DAMAD on 4--6 %, with F1 55 against 26 on SWaT. Under injected drift the static and adapt-once detectors alarm on 73--87 % of normal steps pooled (95--100 % on SWaT, WADI and PSM) and do not recover; DAMAD keeps the rate at 17--30 %, recovers within 230--440 windows, and has the best pooled point-wise F1 under every pattern, driven by SWaT, WADI and SMD. On HAI it brings no gain, on SMAP and MSL every method is weak, and its recalibrated thresholds cost it detection latency everywhere. The ablations show that threshold recalibration and the residual-side gate carry the result, the acceptance test matters where anomalies are long, replay helps on some streams and hurts on SWaT, and the choice of meta-learner is secondary. Code, loaders and every result table are released.

**Keywords:** meta-learning; few-shot learning; anomaly detection; industrial Internet of Things; concept drift; streaming data; variational autoencoder; benchmarking protocol.

# 1 Introduction

Industrial Internet of Things (IIoT) installations stream readings from thousands of sensors, and someone, or something, has to notice when a reading pattern means that a pump is failing, a valve is stuck, or a controller has been tampered with [@chandola2009survey; @pang2021deep]. A missed anomaly costs production time and sometimes equipment or safety. Deep anomaly detection (AD) has produced a long list of methods for this: autoencoders, variational autoencoders [@kingma2014vae], LSTM predictors, adversarial reconstruction [@audibert2020usad] and others, with strong numbers on public benchmarks.

The numbers rely on three assumptions that an IIoT deployment rarely satisfies at once. The first is that labelled faults exist in useful quantity. A turbine that fails once in two years does not provide a training set. The second is that the data distribution is stationary. Equipment ages, loads shift with the season, and operators change set-points, so the statistics of normal operation move [@gama2014drift; @lu2019drift]. The third is that the fault types at deployment time are the ones seen during training. New failure modes appear, and the detector is expected to flag them from a handful of examples. Each problem has its own literature. What is missing is a method, and an evaluation, for the case where all three hold together.

Meta-learning is the natural starting point for the few-shot side. A meta-learner is trained over a distribution of tasks and comes out with an initialisation, an embedding or a memory that adapts to a new task from very little data [@finn2017maml; @snell2017proto; @hospedales2022meta]. Treating each operating regime, or each fault type, as a task makes the application to IIoT straightforward in principle. A few papers have done exactly that [@moon2023mavae; @feng2024metauad; @tian2024omlog]. What we found when we reviewed the field systematically is that the meta-learning methods are trained offline and never updated, the streaming methods do not meta-learn, and almost none of either group is evaluated on an established industrial benchmark.

An earlier version of this work, accepted at PCEMS 2026, reported the review and sketched a conceptual architecture for the empty cell of the resulting taxonomy. It did not build or evaluate it. This paper does. We kept the taxonomy and the review findings, rewrote the protocol around what we learned while running it, and report what it took to make the architecture work on four public datasets.

The contributions are as follows.

1. A four-dimensional taxonomy of meta-learning AD methods (paradigm, detection mechanism, streaming capability, industrial validation) grounded in a PRISMA-style review of 67 papers, and a gap map showing that the online meta-adaptive column of that taxonomy is empty (Section 3).
2. A benchmarking protocol for this class of methods: open datasets, synthetic drift injected at known change points, strictly point-wise metrics with no point-adjust, three streaming metrics, and a fixed set of baselines and ablations (Section 4).
3. DAMAD, a working online meta-adaptive detector with four modules that each map to one of three sub-problems we identify. Two design choices differ from our earlier sketch, and we explain why with evidence (Section 5).
4. An evaluation on SWaT, WADI, HAI 21.03, SMAP, MSL, SMD, SKAB and PSM, five seeds, four drift patterns, eight baselines and ten ablations, with detection latency, adaptation speed, false-alarm rate under drift and computational cost reported alongside F1 and AUROC (Sections 6 and 7). The results are not uniformly in the method's favour, and we report where they are not.
5. An open implementation in which every method, baseline and ablation is a configuration of one streaming loop, so the comparison is like for like.

The paper is organised as follows. Section 2 gives background on AD, meta-learning and concept drift. Section 3 summarises the systematic review, the taxonomy and the gap map. Section 4 states the three sub-problems and the protocol. Section 5 presents DAMAD. Section 6 describes the experimental setup, Section 7 the results, Section 8 discusses limitations and Section 9 concludes.

# 2 Background

## 2.1 Anomaly detection on multivariate streams

We consider a multivariate stream $x_1, x_2, \dots$ with $x_t \in \mathbb{R}^d$. A detector assigns a score $s(x_t)$ to each step and raises an alarm when $s(x_t) > \tau$. Chandola et al. [@chandola2009survey] distinguish point anomalies (one aberrant reading), contextual anomalies (normal in isolation, aberrant given recent history) and collective anomalies (a sequence that is only aberrant as a whole). Industrial faults are mostly of the last two kinds, which is why detectors work on windows rather than single readings.

The semi-supervised formulation fits IIoT best: train on normal data only, score by departure from learned normality. Reconstruction-based models dominate this formulation. An autoencoder or VAE [@kingma2014vae] learns to reproduce normal windows and scores a window by its reconstruction error,

$$ s(x) = \lVert x - \mathrm{Dec}(\mathrm{Enc}(x)) \rVert^2 \qquad \text{(1)} $$

Every method in that family assumes that the training distribution is the deployment distribution. When it is not, the error in Eq. (1) rises for normal data too, and the model has no way of knowing that it is now wrong [@kermenov2023drift; @wahab2022online].

## 2.2 Meta-learning

Meta-learning makes the learning procedure the object of optimisation [@hospedales2022meta]. Optimisation-based methods learn a parameter initialisation $\theta^*$ from which a few gradient steps on a small support set $S_i$ give a good model for task $T_i$. MAML [@finn2017maml] writes this as an inner step,

$$ \theta_i' = \theta - \alpha \nabla_\theta \mathcal{L}_{S_i}(\theta) \qquad \text{(2)} $$

and an outer step over tasks evaluated on their query sets $Q_i$,

$$ \theta \leftarrow \theta - \beta \nabla_\theta \sum_i \mathcal{L}_{Q_i}(\theta_i') \qquad \text{(3)} $$

MAML++ [@antoniou2019mamlpp] stabilises this with per-layer, per-step inner learning rates and a multi-step query loss; Meta-SGD [@li2017metasgd] learns a per-parameter inner learning rate; first-order variants [@nichol2018fomaml] drop the second derivative in Eq. (3). Because the learner can be any differentiable model, an autoencoder works as the base learner, which is what makes optimisation-based meta-learning the right paradigm for reconstruction-based AD. Metric-based methods [@snell2017proto] learn an embedding in which a query is classified by distance to class prototypes; model-based methods use an external memory and adapt with a forward pass. Both are cheap at inference time but, as Section 3 shows, neither has been combined with streaming adaptation.

## 2.3 Concept drift

A stream exhibits concept drift when the joint distribution of readings and labels at time $t$ differs from that at $t + \Delta t$ [@gama2014drift; @lu2019drift]. Four patterns are usually distinguished: sudden, gradual (the two regimes are mixed over a transition period), incremental (a slow monotone shift) and recurring (earlier regimes return). Detection methods fall into three classes. Error-rate monitors such as DDM [@gama2004ddm] need labelled feedback and are out of reach in unsupervised AD. Distribution monitors such as ADWIN [@bifet2007adwin] watch a statistic of the stream and come with bounds on false positives and false negatives. Representation monitors watch the model's own internal state, for example by comparing kernel embeddings with maximum mean discrepancy (MMD) [@gretton2012mmd]. Hinder et al. survey detection and adaptation in detail [@hinder2024a; @hinder2024b]. Continual learning supplies the tools for updating a model without forgetting what it knew [@kirkpatrick2017ewc; @rolnick2019replay; @wang2024continual]; the connection to meta-learning, where a distribution shift becomes a change of task distribution, is the one this paper exploits.

# 3 Systematic review and taxonomy

## 3.1 Method

The review follows the PRISMA 2020 reporting items [@page2021prisma] as far as a two-author study allows, and this section states exactly what was done rather than what a full-scale review would do. Two sources were searched for January 2018 to December 2025, the period since MAML [@finn2017maml] started the current wave of gradient-based meta-learning: IEEE Xplore, exported on 28 September 2026, and Lens.org, which aggregates Crossref, PubMed, Microsoft Academic and OpenAlex records and therefore covers Elsevier, Springer, MDPI and ACM venues alongside IEEE. Two search strings were used. The primary string targeted the intersection of meta-learning and AD: ("meta-learning" OR "few-shot learning" OR "MAML" OR "prototypical network" OR "learning to learn") AND ("anomaly detection" OR "fault detection" OR "outlier detection") AND ("Internet of Things" OR "IoT" OR "IIoT" OR "streaming data" OR "time series" OR "industrial"). The secondary string captured concept drift and AD jointly: ("concept drift" OR "distribution shift" OR "non-stationary" OR "online learning") AND ("anomaly detection" OR "fault detection") AND ("IoT" OR "IIoT" OR "streaming" OR "industrial"). The IEEE Xplore export was run with the primary string, each term applied to the "All Metadata" field (title, abstract and index terms); Lens.org was run with both strings.

Table 1 lists the inclusion and exclusion criteria and Table 2 the selection. The three exports held 788 records (IEEE Xplore 188, Lens primary 124, Lens secondary 476); matching on DOI and then on normalised title removed 93 duplicates within and across sources, leaving 695 unique works. Screening ran in three steps. First, 466 records whose title, abstract and keywords contain no meta-learning or few-shot term (meta-learning, few-shot, one-shot, MAML, prototypical, Siamese, metric learning, learning to learn) were excluded under EC1 without further reading; almost all of them are the drift-and-AD papers that the secondary string was designed to retrieve, and they inform Section 2.3 but are not meta-learning papers. Second, 29 of the remaining 229 records were preprints, book chapters, editorials, datasets, reports or theses and were excluded under EC4. Third, the remaining 200 records were read at title-and-abstract level by the first author: 82 were excluded under EC1 (meta-learning in the stacking-ensemble, AutoML or hyper-parameter sense, few-shot learning mentioned only as motivation, or no anomaly or fault detection task), 50 under EC2 as image-only, two as surveys with no method to classify, one under EC3 as a plain application of an existing method, and 65 were retained. Two papers that we knew from earlier reading and that meet the criteria but were not retrieved by either string, MAVAE [@moon2023mavae] and the 5G industrial-internet detector of Yan et al. [@yan2024fewshot], were added from our reference list. The corpus is 67 papers. One in 2020, three in 2021, five in 2022, 13 in 2023, 13 in 2024 and 32 in 2025: 87 % of it is from 2023 onwards, and nothing before 2020 survived screening. Appendix A lists every paper with its DOI and its codes.

Two limits of the procedure should be stated. No full-text stage was carried out, so the taxonomy codes in Section 3.2 come from titles, abstracts and keywords; where an abstract names a method ("MAML", "prototypical network") the code is reliable, and where it says only "meta-learning" the paradigm is recorded as not stated. And the screening was done by one author, so the inter-rater agreement that a two-reader review reports is not available; the screening sheet with a one-line reason for every decision is released with the code so that any reader can audit it.

Table 1. Inclusion (IC) and exclusion (EC) criteria as applied.

| Code | Criterion |
|---|---|
| IC1 | Proposes or evaluates meta-learning or few-shot learning for anomaly or fault detection on sensor, telemetry, network or log data |
| IC2 | Published January 2018 to December 2025 |
| IC3 | Journal or conference paper as typed by the source database; English |
| EC1 | No meta-/few-shot component, or "meta-learning" in the ensemble, AutoML or hyper-parameter sense, or few-shot scarcity named only as motivation, or no detection task |
| EC2 | Image or video anomaly detection only |
| EC3 | Applies an existing method with no methodological contribution |
| EC4 | Preprint, book chapter, editorial, dataset, report or thesis |

Table 2. Selection summary.

| Stage | Outcome |
|---|---|
| 1. Identification (IEEE Xplore, Lens.org primary, Lens.org secondary) | 788 records; 695 after removing 93 duplicates |
| 2. Keyword pre-screen (no meta-/few-shot term) | 466 excluded (EC1); 229 retained |
| 3. Publication type | 29 excluded (EC4); 200 read |
| 4. Title and abstract reading | 82 EC1, 50 EC2, 2 surveys, 1 EC3; 65 retained |
| 5. Reference-list additions | 2 added |
| Final corpus | 67 papers |

## 3.2 A four-dimensional taxonomy

Earlier surveys classify AD methods along one axis, usually algorithm family [@chandola2009survey; @pang2021deep] or application domain [@belay2023iot]. One axis hides trade-offs that matter here: a method can be excellent at few-shot adaptation and completely static, or drift-aware and never tested on industrial hardware. We classify every paper in the corpus along four axes at once.

*D1, learning paradigm.* OPT: optimisation-based meta-learning, learning a shared initialisation (MAML, MAML++, Meta-SGD). MET: metric-based, learning a task-agnostic embedding (Siamese, prototypical and relation networks). MOD: model-based, using memory, hypernetworks or a pretrained sequence model. HYB: two or more of the above. NML: few-shot learning without a meta-learning paradigm, by transfer and fine-tuning or by generating synthetic samples. NS: the abstract says "meta-learning" or "few-shot" and no more.

*D2, detection mechanism.* REC: reconstruction error (AE, VAE, transformer). DIS: distance to learned prototypes or embeddings. DEN: density estimation. PRE: prediction error. CLS: supervised few-shot classification of known fault or attack classes. HYB: a combination.

*D3, streaming and drift capability.* STA: trained offline, no online update. INC: incremental or class-incremental updates without explicit drift awareness. DAW: detects distribution shift and triggers adaptation. OMA: online meta-adaptive, meaning the meta-level itself (the initialisation or the task distribution) is updated as the stream evolves.

*D4, industrial validation.* IIV: evaluated on an established industrial or telemetry benchmark (SWaT [@goh2016swat], WADI [@ahmed2017wadi], HAI [@shin2021hai], SMAP/MSL [@hundman2018smap]). IOV: evaluated on other IoT, industrial or network data (bearing and motor rigs, process data, intrusion datasets, satellite telemetry without a named benchmark). GEN: generic datasets. THE: theory or simulation only.

Table 3 places representative papers on the grid, and Figure 1 plots the whole corpus on the D1 × D3 plane. Metric-based methods are the largest group, 22 of the 67 papers (33 %); optimisation-based methods follow with 19 (28 %); 11 (16 %) are few-shot methods with no meta-learning paradigm at all, mostly transfer learning with a handful of target samples; four are model-based, two hybrid, and nine state no paradigm in the abstract. On D2 the corpus is dominated by supervised few-shot classification of known fault classes (33 papers, 49 %), which is the bearing and motor fault-diagnosis literature; 20 papers score by distance to prototypes, eight by reconstruction, one by prediction and five by a combination. On D3, 62 papers (93 %) are static, four update incrementally [@yue2023incremental; @pu2024fseocl; @du2024fscil] and one, OMLog [@tian2024omlog], detects drift before it adapts. On D4, one paper [@tuli2022tranad] uses the industrial benchmarks of this study, 61 use other IoT, industrial or network data and five use generic data.

Table 3. Taxonomy placement of representative papers. Rows marked "context" are cited in the text but are not meta-learning papers and are not in the corpus.

| Paper | Year | D1 | D2 | D3 | D4 |
|---|---|---|---|---|---|
| Finn et al. [@finn2017maml] (context) | 2017 | OPT/MAML | n/a | STA | GEN |
| Zhang et al. [@zhang2020maml] | 2020 | OPT/MAML | CLS | STA | IOV |
| Zhou et al. [@zhou2021siamese] | 2021 | MET/Siamese | DIS | STA | IOV |
| Tuli et al., TranAD [@tuli2022tranad] | 2022 | OPT/MAML | REC | STA | IIV |
| Wahab [@wahab2022online] (context) | 2022 | none | PRE | INC | IOV |
| Chen et al. [@chen2023metabearing] | 2023 | OPT/MAML | CLS | STA | IOV |
| Yue et al. [@yue2023incremental] | 2023 | OPT | CLS | INC | IOV |
| Moon et al., MAVAE [@moon2023mavae] | 2023 | OPT/MAML | REC (VAE) | STA | GEN |
| Kermenov et al. [@kermenov2023drift] (context) | 2023 | none | REC | INC | IIV |
| Belay et al. [@belay2023iot] (context) | 2023 | none | REC+DIS | STA | IIV |
| Li et al. [@li2024rrpn] | 2024 | MET/prototypical | DIS | STA | IOV |
| Pu et al. [@pu2024fseocl] | 2024 | NML | HYB | INC | IOV |
| Du et al. [@du2024fscil] | 2024 | NS | CLS | INC | IOV |
| Yan et al. [@yan2024fewshot] | 2024 | MET | DIS | STA | IOV |
| Tian et al., OMLog [@tian2024omlog] | 2025 | MOD | PRE | DAW | GEN |
| DAMAD (this work) | 2026 | HYB | REC | OMA | IIV |

![Figure 1. Coverage of the 67 reviewed papers on the D1 × D3 plane. The online meta-adaptive column is empty for every paradigm; the drift-aware column holds one paper. The bottom-right cell of the original sketch, hybrid and online meta-adaptive, is the target of this work.](../figures/fig_gapmap.png){#fig:gapmap width=85%}

## 3.3 Three findings

*Finding 1, static dominance.* 62 of the 67 papers sit in the STA column, and the four that update do so by adding fault classes or samples, not by watching the stream. Methods designed for offline training are being applied to a problem that is online by nature. The finding has a second face that the D2 counts show: half of the corpus treats the problem as supervised classification of fault classes seen at training time, which is a different problem from detecting a fault that has never been seen.

*Finding 2, the OMA gap.* No paper in the corpus updates its meta-learning strategy in response to stream evolution. The column is empty for every paradigm and every year. The closest are OMLog [@tian2024omlog], which detects a shift and adapts once, and the three incremental methods, which never ask whether the stream has moved.

*Finding 3, the validation gap.* One paper in the corpus evaluates on the industrial benchmarks of this study: TranAD [@tuli2022tranad], a transformer reconstruction detector that uses MAML during training so that it can be trained on a fraction of the data, and that reports on SWaT, WADI, SMAP, MSL and SMD. Its meta-learning is a training aid; nothing is adapted at deployment, and its scores are point-adjusted. Every other paper that meta-learns is evaluated on bearing and motor rigs, process datasets, intrusion datasets or telemetry without a named benchmark, and no paper evaluates few-shot *adaptation* on SWaT, WADI, HAI, SMAP or MSL. The benchmarks exist and the methods exist; the two have not met.

Two papers deserve mention because they come closest. MAVAE [@moon2023mavae] wraps a VAE in a MAML outer loop and shows that five labelled normal windows suffice to adapt to a new sensor type. It is trained offline and never updated. OMLog [@tian2024omlog] uses MMD on log-sequence embeddings to detect a shift and then runs few-shot meta-adaptation; it is the only DAW method in the corpus, but it is built for discrete log sequences and has no memory of past regimes and no threshold management. Our baselines MAML-1 and OML-A (Section 6) transfer these two ideas to sensor streams so that they can be compared with DAMAD directly.

# 4 Problem statement and benchmarking protocol

## 4.1 Three sub-problems

Achieving the OMA capability requires solving three sub-problems that the corpus does not solve together.

*SP1, drift-aware episode construction.* Episodic meta-learning samples support and query sets that should come from one coherent task. In a non-stationary stream, naive temporal sampling mixes pre- and post-change observations into the same episode and destabilises the inner loop. The sampler has to know where one regime ends and the next begins.

*SP2, online meta-initialisation update without forgetting.* The initialisation $\theta^*$ must keep up with the stream if it is to remain a useful starting point, but updating it on the newest regime alone overwrites what it knew about earlier regimes. This is catastrophic forgetting at the meta level [@kirkpatrick2017ewc].

*SP3, threshold recalibration under drift without labels.* Drift and anomalies both raise the reconstruction error. Only one of them should move the threshold $\tau$. Telling the two apart, and recalibrating $\tau$ in the right case only, has to be done without labels at deployment time.

## 4.2 Evaluation problems in the reviewed work

Two evaluation practices make cross-paper comparison unreliable. The first is point-adjust scoring, under which one true positive anywhere inside an anomalous segment counts the whole segment as detected. Point-adjust F1 can sit 15--30 points above point-wise F1 on the same scores, and a random scorer can reach high point-adjust F1 on long segments [@kim2022rigorous; @garg2022evaluation; @wu2023flawed]. The second is that no reviewed paper reports a streaming metric: how long detection takes, how fast the detector recovers after a change, or how many false alarms the change itself causes.

## 4.3 The protocol

Table 4 states the protocol we use in Sections 6 and 7. It differs from the version in our PCEMS paper in two respects. The dataset list is split into an open tier that anyone can download (HAI, SMD, SKAB, PSM, SMAP, MSL) and a licensed tier (SWaT, WADI, obtained under the iTrust data-use agreement), and both tiers are reported here. And the drift injection is specified exactly, so that every method sees the same stream.

Table 4. The benchmarking protocol.

| Element | Specification |
|---|---|
| Datasets | Open tier: HAI 21.03 (ICS testbed), SMAP and MSL (spacecraft telemetry), SMD (server machines), SKAB (rotating-machinery rig), PSM (server metrics). Licensed tier: SWaT and WADI (water treatment and distribution testbeds, iTrust agreement). |
| Few-shot setting | Held-out entities (machines, runs, campaigns) never seen in meta-training; K ∈ {1, 5, 10} support windows at the start of each stream. |
| Drift injection | Affine per-sensor shift on a random half of the sensors (offset 1.5 training standard deviations, scale factor 1.3) applied after change points at 35 % and 60 % of the stream (sudden, gradual with a 5 % transition, recurring with a third point at 80 %), or growing linearly over 30 % of the stream (incremental). Labels unchanged. |
| AD metrics | Precision, recall and F1 at the method's own deployed threshold, strictly point-wise; AUROC and AUPRC threshold-free. Point-adjust is prohibited. Oracle-threshold F1 may be reported for context only. |
| Streaming metrics | Detection latency (steps from segment onset to the first alarm inside it); adaptation steps (steps after a change point until the rolling false-alarm rate returns to the pre-drift level plus 5 points); false-alarm rate on normal steps after the first change point. |
| Warm-up | The first K + 300 windows (K + 100 on SKAB) are used for adaptation and threshold calibration by every method and excluded from scoring. |
| Threshold | Peaks-over-threshold [@siffer2017pot] at risk q = 10^-2^ for every method, so that threshold selection is not a confound. |
| Baselines | Isolation Forest, static VAE, fine-tuned VAE, incrementally updated VAE, drift-aware fine-tuned VAE, MAML-adapted-once VAE, Meta-SGD-adapted-once VAE, MMD-triggered meta-adapter. |
| Statistics | Mean ± standard deviation over five seeds; the seed also changes the entity split. |
| Ablations | Each module removed or replaced in isolation. |
| Cost | Scoring time per window, adaptation time, meta-update time, memory footprint, parameter count. |

# 5 DAMAD

## 5.1 Overview

DAMAD has four modules arranged around a streaming VAE (Figure 2). In steady state every window $x_t$ is encoded, reconstructed and scored by Eq. (1), and an alarm is raised if the score exceeds $\tau$. Module 1 watches the residual for a regime change. When a change is confirmed, the next K windows become the support set, Module 2 adapts a fresh copy of $\theta^*$ to them in K gradient steps, Module 4 recalibrates $\tau$ on the residuals that follow, Module 3 stores the regime that just ended, and a replay meta-update refreshes $\theta^*$ from the new regime and a few remembered ones. A champion/challenger check runs in parallel for a while: the previous model keeps scoring in the shadow, and if it fits the stream better than the adapted one, the adaptation and the new threshold are undone.

![Figure 2. DAMAD, band by band. A: what is prepared once, offline (regimes, episodes, the meta-trained starting point θ*). B: the path every window takes while the plant runs. C: the residual-side drift gate that decides whether the plant has changed. D: the six things that happen after a confirmed change, including the safety check that undoes an adaptation if the old model turns out to fit better. Dashed arrows carry the adapted model and the new threshold back into the per-step path.](../figures/fig_damad_architecture.png){#fig:arch width=100%}

## 5.2 Module 2: the meta-learned VAE

The base learner is an MLP VAE on flattened windows of W = 8 steps, so the input dimension is $8d$. The encoder has two hidden layers (128 and 64 units, ELU) producing a 16-dimensional Gaussian posterior; the decoder mirrors it. The training loss is the negative ELBO with the KL term weighted by $\beta = 0.1$; the anomaly score is the mean squared reconstruction error through the posterior mean, which is deterministic.

Meta-training follows MAML++ [@antoniou2019mamlpp]. A task is a regime (Section 5.3). An episode draws K support windows from the first half of the regime and 32 query windows from the second half, so that the inner loop cannot see the query steps. Three inner steps are taken with learnable per-layer, per-step learning rates, and the outer loss is a weighted sum of the query loss after each inner step, annealed over the first 200 outer iterations towards the final step only. We use the first-order approximation [@nichol2018fomaml]; for a model of this size on CPU the second-order term buys little. The inner gradient is clipped to norm 10 before the step. Without the clipping a support set that happens to hold a few windows at the edge of the clipping range throws the adapted parameters far away and meta-training diverges, which is what happened in our first runs. Meta-training runs 400 outer iterations with a meta-batch of four regimes and Adam at $10^{-3}$. At deployment, adaptation is the same three inner steps from $\theta^*$ on the K support windows.

## 5.3 Module 1: regime boundaries and the drift gate

Module 1 has two jobs: cutting the training streams into regimes for episode construction (SP1), and deciding online when the deployed model should adapt.

*Training-time segmentation.* One ADWIN [@bifet2007adwin] runs per sensor on block means of ten steps. A regime boundary is placed when at least 20 % of the sensors have reported a change within the last 200 steps and the current regime is at least 400 steps long. Over-segmentation only costs episode diversity, so the vote is permissive. On SMD this yields 870 regimes with a median length of 400 steps from 20 training machines. The ablations replace this sampler with fixed chunks of the same median length and with regime-free random sampling.

*Online gate.* Our PCEMS sketch ran ADWIN on the raw input with MMD on the embeddings as a second detector. Neither survived contact with real streams in that form. On server and process data the input statistics never stop moving, so a gate that fires on input change adapts every few hundred steps whether or not the model has stopped fitting. The quantity that matters is whether the model still fits. The gate therefore runs ADWIN on block means (ten windows) of the log residual, and only changes in which the retained window has the higher mean count, because a model that fits better than before needs no adaptation. The change must also be material: the retained mean has to exceed the level recorded after the last adaptation by at least 0.5 log units, a 65 % rise in residual. One such hit confirms a change; the block mean, the direction rule and the minimum shift already guard against spikes. A refractory period of 400 windows separates adaptations.

We also implemented the MMD branch [@gretton2012mmd]: the kernel two-sample statistic between the encoder embeddings of the last 64 windows and 300 reference embeddings recorded after the last adaptation, with a block-bootstrap null (the largest MMD² between any contiguous 64-window block of the reference set and the rest of it, times 1.5) and two consecutive exceedances required. Even with that conservative null it over-triggers on ordinary within-regime variation, and every adaptation it causes costs a fresh threshold calibration on a short window. Section 7.4 reports the variants with MMD alone and with both detectors; the full method uses the residual gate only.

## 5.4 Module 4: gated threshold

$\tau$ is set by the peaks-over-threshold method [@siffer2017pot]: a generalised Pareto distribution is fitted to the residual excesses above the 98th empirical percentile of a calibration window and $\tau$ is the quantile of that tail at risk $q = 10^{-2}$. The calibration window is the 300 windows that follow adaptation (100 on SKAB). Between confirmed changes $\tau$ does not move, whatever the residual does in the short term. This is the gating that keeps the false-alarm rate in check during ordinary stream variation and it is the same procedure for every method in the study, so the comparison does not reward one method's threshold heuristics over another's.

## 5.5 Module 3: regime memory and replay

The buffer holds one entry per regime: the last 300 steps of the regime, its per-sensor mean and variance, and the $\tau$ that was in force. Capacity is eight regimes; the oldest leaves first. After an adaptation has been accepted, $\theta^*$ is refreshed by ten outer iterations of the meta-learner on episodes drawn from the current regime and up to three remembered regimes, sampled with probability proportional to a similarity term (closeness of the regime means) plus a recency bonus. This is experience replay [@rolnick2019replay] at the level of regimes rather than records, which keeps the buffer at a few hundred kilobytes.

## 5.6 The acceptance test

The three sub-problems interact through one confound: a long anomaly raises the residual, so it can confirm a change, and the detector will then adapt to the anomaly and calibrate $\tau$ on it. When normal operation resumes, the adapted model fits it worse than the old one did, and false alarms flood in. We observed exactly this on SMD, where anomaly segments can last several hundred steps. The remedy is to make the decision falsifiable. After adaptation and recalibration, the previous model and its threshold are kept as a champion for 600 windows (200 on SKAB) while the adapted model scores. Every 50 windows the rolling medians of the two log residuals are compared; if the champion is better by more than 0.1 log units, the adaptation, the new $\tau$ and the memory entry are undone. A first check at the end of the calibration window catches the obvious cases early. The idea has a precedent in paired learners for concept drift [@bach2008paired], where a stable and a reactive learner compete. Here the competition decides whether the thing that moved was the regime or an anomaly, which is SP3 stated operationally.

## 5.7 Cost

In steady state DAMAD does one forward pass per window plus O(log n) ADWIN work per ten windows. During the shadow period a second forward pass is added. Adaptation costs three gradient steps on K windows; a replay meta-update costs ten outer iterations on four episodes. The buffer holds at most eight regimes × 300 steps × d floats. Section 7.6 reports the measured figures.

## 5.8 Placement in the taxonomy

DAMAD is HYB on D1 (an optimisation-based initialisation with a model-based memory), REC on D2, OMA on D3 because $\theta^*$ itself is updated at deployment time, and IIV on D4 because it is evaluated on SWaT, WADI, HAI, SMAP and MSL in Section 6. To our knowledge it is the first method evaluated in that cell.

# 6 Experimental setup

## 6.1 Datasets and entities

Table 5 lists the datasets. An *entity* is one monitored unit with a normal-only training stream and a labelled test stream, and it is the unit of the few-shot split: a held-out entity is one the meta-learner never saw. Values are standardised with the entity's own training statistics and clipped to ±10 standard deviations; without the clipping a sensor that barely moves in training turns ordinary test noise into values in the thousands.

*HAI 21.03* [@shin2021hai] comes from a hardware-in-the-loop testbed with a boiler, a turbine and a water-treatment process, 79 tags at 1 Hz, three attack-free training campaigns and five test campaigns with labelled attacks. We average the signals over 10-second blocks, pool the training campaigns (keeping them as separate streams for regime segmentation, since they were recorded weeks apart) and treat each test campaign as an entity. *SMD* [@su2019omnianomaly] has 28 server machines with 38 metrics at one-minute resolution; each machine is an entity, and 30 % of the machines are held out per seed. *SKAB* [@katser2020skab] is a water-circulation rig with 8 sensors at 1 Hz and 34 short runs in which a valve or the pump is manipulated. The anomaly-free recording sits at a very different flow level from most runs, so each run is standardised with its own normal prefix, which becomes its training stream; one run with almost no prefix is dropped, and 30 % of runs are held out per seed. This makes SKAB a genuine few-shot setting: the detector meets a new run with a few hundred seconds of normal operation. *PSM* [@abdulaal2021psm] is a single stream of 25 server metrics; regimes for meta-training are carved from its training part, and its test part is the held-out stream. *SWaT* [@goh2016swat] and *WADI* [@ahmed2017wadi] are the iTrust water-treatment (51 tags, 36 attacks) and water-distribution (123 tags after dropping four empty channels, 15 attacks) testbeds, used under the iTrust data-use agreement; both are downsampled to 10 s by stride, the first six hours of SWaT's normal trace are dropped as the plant start-up transient, and each is one entity treated like PSM. *SMAP* and *MSL* [@hundman2018smap] are the NASA telemetry channels of the telemanom release: 55 SMAP channels with 25 features and 27 MSL channels with 55 features, each with its own training and labelled test stream, one entity per channel and 30 % of channels held out per seed. Their test streams are 1,100 to 8,600 windows long, so these two datasets use a 200-window calibration and a 400-window shadow period.

Table 5. Datasets. Test lengths are in windows after preprocessing; anomaly rate is the share of labelled steps.

| Dataset | Domain | d | Entities (held out) | Test length | Anomaly rate | Sampling |
|---|---|---|---|---|---|---|
| HAI 21.03 | ICS testbed | 79 | 5 (5) | 4k--12k | 1.4--2.9 % | 10 s (block mean) |
| SMD | servers | 38 | 28 (8) | 24k--29k | 4.2 % avg. | 1 min |
| SKAB | rotating machinery | 8 | 33 (10) | 0.9k--1.2k | 35 % avg. | 1 s |
| PSM | servers | 25 | 1 (1) | 88k | 28 % | 1 min |
| SWaT | water treatment testbed | 51 | 1 (1) | 45k | 12 % | 10 s (stride) |
| WADI | water distribution testbed | 123 | 1 (1) | 17k | 5.8 % | 10 s (stride) |
| SMAP | spacecraft telemetry | 25 | 55 (17) | 4.4k--8.6k | 12 % avg. | native |
| MSL | rover telemetry | 55 | 27 (8) | 1.1k--6.1k | 12 % avg. | native |

## 6.2 Methods

Every method runs through the same streaming loop and differs only in configuration (Table 6). All VAE-based methods share the architecture of Section 5.2. The static VAE is trained for 1,500 Adam steps on 60,000 pooled normal windows from the meta-training entities. Meta-learners are trained as in Section 5.2 on regimes from the meta-training entities. Isolation Forest uses 100 trees on 20,000 pooled windows. Every method calibrates its threshold with the same POT procedure on the same warm-up windows.

Table 6. Methods. "adapt once" means K-shot adaptation at the start of the stream and nothing after.

| Name | Initialisation | Reaction to drift | Gate | Replay | τ recalibration |
|---|---|---|---|---|---|
| IF | Isolation Forest [@liu2008iforest] | none | – | – | – |
| VAE-S | static VAE | none | – | – | – |
| VAE-FT | static VAE | fine-tune once (30 Adam steps on K windows) | – | – | – |
| VAE-INC | static VAE | one Adam step every 5 windows on the last 32 non-alarmed windows [@wahab2022online] | – | – | – |
| VAE-DFT | static VAE | fine-tune on K post-change windows | residual ADWIN, acceptance test | – | yes |
| MAML-1 | MAML++ θ* | adapt once [@moon2023mavae] | – | – | – |
| MSGD-1 | Meta-SGD θ* | adapt once | – | – | – |
| OML-A | MAML++ θ* | K-step adapt on change [@tian2024omlog] | MMD | – | – |
| DAMAD | MAML++ θ* | K-step adapt on change | residual ADWIN, acceptance test | yes | yes |

VAE-DFT shares DAMAD's gate, acceptance test and recalibration and differs only in adapting from the static initialisation by fine-tuning; it therefore isolates the contribution of the meta-learned initialisation. OML-A differs from DAMAD in using MMD on the embeddings as its only gate and in having no memory, no recalibration and no acceptance test, which is the OMLog recipe.

The ablations (Table 7) remove or replace one element of DAMAD at a time.

Table 7. Ablations.

| Variant | Change |
|---|---|
| DAMAD-rndM1 | episodes drawn from anywhere in the training stream, no regime boundaries |
| DAMAD-noM1 | episodes from fixed chunks of the median ADWIN-regime length |
| DAMAD+mmd | residual ADWIN and MMD both as the gate (the PCEMS sketch) |
| DAMAD-mmd | MMD only as the gate |
| DAMAD-noM3 | no replay meta-update |
| DAMAD-noM4 | threshold never recalibrated after the initial calibration |
| DAMAD-noAcc | no acceptance test |
| DAMAD-fo | FOMAML initialisation (single inner learning rate, no multi-step loss) |
| DAMAD-msgd | Meta-SGD initialisation |

## 6.3 Conditions, metrics and implementation

Each held-out entity of HAI, SMD, PSM, SWaT, WADI, SMAP and MSL is run under five stream conditions: its original test stream and the four injected-drift versions of Table 4. SKAB runs are about a thousand windows long, which is not enough to hold a 100-window calibration, a 200-window shadow period and a refractory period between two injected changes, so SKAB is used for the few-shot cold-start setting only. Ablations are scored under the drift conditions. The few-shot sweep (K = 1, 5, 10) is run on the original streams for the methods that adapt at the start; all drift conditions use K = 5. Metrics are those of Table 4. Detection latency is averaged over anomaly segments in which an alarm occurred, and the share of segments with any alarm is reported next to it. Adaptation steps use a rolling window of 100 steps and are capped at the length of the post-change segment if the rate never recovers.

Everything is implemented in PyTorch 2 and NumPy and runs on CPU; one seed of the whole study takes about an hour per dataset on a four-core machine with one thread per job. Reported timings come from that machine. Five seeds change the network initialisation, the episode sampling, the drift realisation and the entity split.
