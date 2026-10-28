# 8 Discussion

## 8.1 What the results say about the three findings

Finding 1 of the review was that static methods are being applied to an online problem. The drift conditions make the cost of that visible: a static VAE whose threshold was set on the first regime alarms on 94 % of normal steps on SMD and 100 % on PSM, SWaT and WADI after a sudden change, and the meta-learned model adapted once (MAML-1) does the same, because a good initialisation does not help a model that is never asked to adapt again. SWaT and WADI show that the problem is not an artefact of injection: on their original attack recordings the same detectors alarm on 73 % and 57 % of normal steps, because the plant was running at a different operating point when the attack data were collected. Finding 2 was that nobody updates the meta-level online. We did, and the plain summary is that the online meta-update (replay) is the smallest part of DAMAD in effect size; the parts that matter are the ones that decide *when* to adapt, *whether to keep* the adaptation, and *where to put the threshold afterwards*. Finding 3 was the validation gap. The study closes it for the method at hand: SWaT, WADI, HAI, SMAP and MSL are all reported, and the two water testbeds are where the method helps most. HAI is the dataset on which DAMAD helps least: its static thresholds are already high relative to the injected shift, so there is less of a false-alarm flood to prevent, and every recalibration on a window that contains an attack costs recall.

A fourth point is not in the review, but Section 7.1 makes it clearly enough to state on its own. For a small reconstruction model, the meta-learned initialisation is not what limits few-shot anomaly detection on these streams. One support window gives the same F1 as ten on every dataset, and a static VAE trained on pooled normal data is as good a starting point as MAML++ or Meta-SGD. The one thing that does move F1 on a cold start is adapting *again* when the stream leaves the regime the support set came from, which is what separates DAMAD from the adapt-once detectors on SWaT and WADI. The few-shot literature we reviewed measures the quality of the initialisation; the deployment problem is dominated by what happens in the hours after it.

## 8.2 What building DAMAD changed

Three decisions in the implemented system differ from our conceptual sketch, and each came from a failure we could see in the traces.

The gate moved from the input to the residual. An input-side detector asks whether the world changed; a residual-side detector asks whether the model stopped fitting. Only the second question is the one that should trigger retraining, and on real streams the two questions have very different answers.

The MMD branch was demoted to an ablation. Two-sample tests on embeddings are sensitive by design, and a conservative null built from contiguous blocks of the reference set was still not conservative enough. Every false trigger costs a threshold calibration on a short window, and that is where recall is lost.

The acceptance test was added. Sub-problem SP3 asks how to tell drift from a long anomaly without labels. Our answer is operational: adapt, then let the old model compete for a while, and undo the adaptation if the old model wins. The decision is wrong sometimes, mostly when the anomaly outlasts the shadow period, as the long SWaT attack in Figure 6 does, but it is checkable, which a one-shot decision rule is not.

Replay turned out to be the least reliable module. It lowers the false-alarm rate on SMD and WADI and raises it on SWaT, where a run holds five or six confirmed changes and a $\theta^*$ refreshed from remembered regimes starts the next adaptation from the wrong place. A production system should treat it as a switch, not a default.

## 8.3 Limitations

*Injected drift.* The drift conditions are synthetic affine shifts. They are reproducible and they do break static detectors in the way real drift does, but they are not real drift. The no-drift condition on SMD and PSM, where the streams carry their own nonstationarity, is the closest we get to the real case, and it is also the condition on which the methods are closest together.

*Short calibration windows.* Every threshold in the study is set from 300 windows, which is what an operator would have after a change. With a 28 % anomaly rate (PSM) the calibration window is often contaminated and the recalibrated threshold is conservative. Robust calibration under contamination is an open problem and the reason our recall on PSM is lower than that of methods which never recalibrate.

*The degenerate strategy.* On datasets with a high anomaly rate, alarming on everything scores a point-wise F1 of 2p/(1+p) where p is the anomaly rate: 0.44 on PSM, 0.25 on MSL, 0.22 on SWaT, 0.20 on SMAP and about 0.5 on SKAB. Under drift on PSM, SWaT, SMAP and MSL the static group sits within a few points of those values with false-alarm rates of 69--100 %, which is that strategy by another name, and on three of those four it "wins" on F1. This is why the protocol reports the false-alarm rate next to F1 and why we do not rank methods on F1 alone.

*Persistent faults.* When an anomalous state lasts until the end of the stream, as on SKAB, no unsupervised rule can tell it from a regime change; DAMAD adapts to it and loses recall, and the acceptance test cannot help because the old regime never returns. A detector that must handle such faults needs either a bound on how long an anomaly can last, supplied by the operator, or a label.

*Latency and missed segments.* Recalibrated thresholds are higher than a threshold set once on a quiet first regime. The first alarm in an anomaly segment comes 7--25 windows later on the industrial datasets and far later on the NASA channels, and on SWaT and WADI only about half of the anomaly segments produce any alarm at all, against 80--90 % for the static group. The trade is explicit in Section 7.2 and it is the first thing to improve.

*SMAP and MSL.* The base learner is a poor match for telemetry channels that consist of one physical value and dozens of binary command flags; every method scores AUROC around 0.6 there. The drift comparison on those datasets is still valid because all methods share the base learner, but a sequence model would be needed before any absolute number on SMAP or MSL meant anything.

*Licensed benchmarks.* SWaT and WADI are used under the iTrust data-use agreement and cannot be redistributed with the code; the loader reads the iTrust release and the preprocessing (stride-10 downsampling, MinMax scaling on the normal trace, start-up trimming) is specified so that the arrays can be rebuilt bit-exactly from the original files.

*One base learner.* All VAE-based methods share one small MLP architecture so that the comparison isolates the adaptation policy. A sequence model would score higher in absolute terms on every method.

*Hyperparameters.* The gate's minimum shift (0.5 log units), the refractory period, the shadow length and the POT risk level were chosen on two SMD machines during development and then frozen for all datasets. They are reported, not tuned per dataset.

## 8.4 Threats to validity

Internal validity rests on every method running through the same loop with the same threshold procedure, the same warm-up and the same streams; we checked that by making each method a configuration rather than a separate implementation. External validity is limited by the four datasets and the synthetic drift. Construct validity of the streaming metrics is the main risk: adaptation steps depend on the rolling window and the margin, and detection latency is only defined for detected segments, which is why the detection rate is reported with it.

# 9 Conclusion

We set out to find a method that is few-shot capable, drift-aware and deployable online for industrial sensor streams, found none in 66 papers, and built one. The review and taxonomy locate the gap; the protocol says how a method in that gap should be measured; DAMAD shows that the gap can be filled with existing parts, provided three things are done that the parts do not do on their own: watch the residual rather than the input, keep the threshold still except after a confirmed change, and let the old model contest every adaptation. On eight benchmarks, including the two water testbeds the field treats as its reference, that is enough to keep the alarm stream meaningful after a change where every static or adapt-once detector stops being useful; it is not enough to match their detection latency, and on telemetry channels the base learner, not the adaptation policy, is the limit. The remaining distance to a production system is in robust threshold calibration under contamination and in the latency cost of recalibration, and the released code is arranged so that either can be worked on by changing one configuration.

# Data and code availability {.unnumbered}

The implementation, the dataset loaders, the experiment runner and every result table in this paper are available at the project repository. HAI 21.03, SMD, SKAB, PSM, SMAP and MSL are public and the loaders fetch or read them; SWaT and WADI must be requested from iTrust.

# Declaration {.unnumbered}

The authors declare no competing interests. This research received no specific grant. SWaT and WADI data were obtained from iTrust, Singapore University of Technology and Design, under its data-use agreement.

# Appendix A. The review corpus {.unnumbered}

The 66 papers of Section 3 with the codes of the four taxonomy axes (D1 paradigm, D2 mechanism, D3 streaming capability, D4 validation; abbreviations as in Section 3.2). The screening sheet with every excluded record and its reason is released with the code.

| # | Year | First author | Title | Venue | D1 | D2 | D3 | D4 | DOI |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2020 | Shen Zhang | Few-Shot Bearing Anomaly Detection Based on Model-Agnostic Meta-Learning | 2020 International Conference on Electrical Machines and Sys | OPT | CLS | STA | IOV | 10.23919/ICEMS50442.2020.9291099 |
| 2 | 2021 | Jinglin Zhang | Diagnosis of Interturn Short-Circuit Faults in Permanent Magnet Synchronous Motors Based on Few-Shot Learning Under a Federated Learning Framework | IEEE Transactions on Industrial Informatics | MET | DIS | STA | IOV | 10.1109/tii.2021.3067915 |
| 3 | 2021 | Xiaokang Zhou | Siamese Neural Network Based Few-Shot Learning for Anomaly Detection in Industrial Cyber-Physical Systems | IEEE Transactions on Industrial Informatics | MET | DIS | STA | IOV | 10.1109/tii.2020.3047675 |
| 4 | 2021 | G. Yu | Subspace-based domain adaptation for few-shot fault diagnosis | 2021 CAA Symposium on Fault Detection, Supervision, and Safe | NML | CLS | STA | IOV | 10.1109/safeprocess52771.2021.9693695 |
| 5 | 2022 | Mohamed-Ali Tnani | Efficient Feature Learning Approach for Raw Industrial Vibration Data Using Two-Stage Learning Framework. | Sensors (Basel, Switzerland) | MET | DIS | STA | IOV | 10.3390/s22134813 |
| 6 | 2022 | Yi-Cheng Yu | Fast Adaption for Multi Motor Anomaly Detection via Meta Learning and deep unsupervised learning | 2022 IEEE 31st International Symposium on Industrial Electro | OPT | REC | STA | IOV | 10.1109/isie51582.2022.9831559 |
| 7 | 2022 | Y. Liu | The Adaptive Personalized Federated Meta-Learning for Anomaly Detection of Industrial Equipment | IEEE Journal of Radio Frequency Identification | OPT | CLS | STA | IOV | 10.1109/jrfid.2022.3209657 |
| 8 | 2022 | Shreshth Tuli | TranAD | Proceedings of the VLDB Endowment | OPT | REC | STA | IIV | 10.14778/3514061.3514067 |
| 9 | 2022 | T. Ye | FLAG: Few-Shot Latent Dirichlet Generative Learning for Semantic-Aware Traffic Detection | IEEE Transactions on Network and Service Management | NML | CLS | STA | IOV | 10.1109/tnsm.2021.3131266 |
| 10 | 2023 | Moon Noh Jung Lee Hwang | Anomaly detection using a model-agnostic meta-learning-based variational auto-encoder for facility management | Journal of Building Engineering | OPT | REC | STA | GEN | 10.1016/j.jobe.2023.106099 |
| 11 | 2023 | Farhan Md. Siraj | A Few-Shot Learning Based Fault Diagnosis Model Using Sensors Data from Industrial Machineries | Vibration | MET | DIS | STA | IOV | 10.3390/vibration6040059 |
| 12 | 2023 | Chandana Priya Nivarthi | Towards Few-Shot Time Series Anomaly Detection with Temporal Attention and Dynamic Thresholding | 2023 International Conference on Machine Learning and Applic | NML | REC | STA | GEN | 10.1109/icmla58977.2023.00218 |
| 13 | 2023 | Ke Yue | An Emerging Fault Diagnosis Framework with Incremental Meta-Learning for Rotating Machinery | 2023 International Conference on Sensing, Measurement & Data | OPT | CLS | INC | IOV | 10.1109/icsmd60522.2023.10490806 |
| 14 | 2023 | L. Cheng | MMFSL: A Novel Multimodal Few-Shot Learning Framework for Fault Diagnosis of Industrial Bearings | IEEE Transactions on Instrumentation and Measurement | NML | CLS | STA | IOV | 10.1109/tim.2023.3289549 |
| 15 | 2023 | Caiyun Wu | Engine fault detection algorithm EA-EFNC based on few-shot learning | Third International Conference on Machine Learning and Compu | NS | CLS | STA | IOV | 10.1117/12.2675146 |
| 16 | 2023 | V. L. Cao | Few-Shot Learning with Discriminative Representation for Cyberattack Detection | 2023 15th International Conference on Knowledge and Systems  | MET | DIS | STA | IOV | 10.1109/kse59128.2023.10299444 |
| 17 | 2023 | Z. Shi | Few-Shot Network Intrusion Detection Based on Model-Agnostic Meta-Learning with L2F Method | 2023 IEEE Wireless Communications and Networking Conference  | OPT | CLS | STA | IOV | 10.1109/wcnc55385.2023.10118898 |
| 18 | 2023 | X. Ye | Rolling bearing fault diagnosis with variable load and few samples based on multifeature fusion meta-learning | 2023 CAA Symposium on Fault Detection, Supervision and Safet | OPT | CLS | STA | IOV | 10.1109/safeprocess58597.2023.10295704 |
| 19 | 2023 | J. Chen | A Meta-Learning Method for Electric Machine Bearing Fault Diagnosis Under Varying Working Conditions With Limited Data | IEEE Transactions on Industrial Informatics | OPT | CLS | STA | IOV | 10.1109/tii.2022.3165027 |
| 20 | 2023 | Y. Liu | Semi-supervised Few-shot Network Intrusion Detection based on Meta-learning | 2023 IEEE International Conferences on Internet of Things (i | NS | CLS | STA | IOV | 10.1109/ithings-greencom-cpscom-smartdata-cybermatics60724.2023.00097 |
| 21 | 2023 | S. Fang | Few-Shot Fault Diagnosis of Rolling Bearings Based on Multidimensional Global Attention Siamese Network | IECON 2023- 49th Annual Conference of the IEEE Industrial El | MET | DIS | STA | IOV | 10.1109/iecon51785.2023.10312375 |
| 22 | 2023 | X. Zhang | Imbalanced Fault Diagnosis Based on Supervised Prototypical Contrastive Network | 2023 Global Reliability and Prognostics and Health Managemen | MET | DIS | STA | IOV | 10.1109/phm-hangzhou58797.2023.10482577 |
| 23 | 2024 | Yan et al. | Meta learning-based few-shot intrusion detection for 5G-enabled industrial internet | Complex & Intelligent Systems | MET | DIS | STA | IOV | 10.1007/s40747-024-01388-1 |
| 24 | 2024 | Lang Du | Research on Turnout Fault Diagnosis Model Based on GADF-CNN-MAML | 2024 5th International Conference on Artificial Intelligence | OPT | CLS | STA | IOV | 10.1109/icaice63571.2024.10863959 |
| 25 | 2024 | Wang Danfeng | Model-Agnostic Meta-Learning-based Fault Classification for Industrial Processes with Small Sample | 2024 39th Youth Academic Annual Conference of Chinese Associ | OPT | CLS | STA | IOV | 10.1109/yac63405.2024.10598657 |
| 26 | 2024 | P. Jagdish Kumar | Classifying Network Abnormalities Into Faults and Attacks in Iot-Based Cyber-Physical Systems using Machine Learning | 2024 International Conference on Integrated Circuits and Com | MET | DIS | STA | IOV | 10.1109/icicacs60521.2024.10498664 |
| 27 | 2024 | Yi-Cheng Yu | Pruning Quantized Unsupervised Meta-Learning DegradingNet Solution for Industrial Equipment and Semiconductor Process Anomaly Detection and Prediction | Applied Sciences | NS | REC | STA | IOV | 10.3390/app14051708 |
| 28 | 2024 | Yunpu Wu | A Novel Fault Diagnosis Method of High-Speed Train Based on Few-Shot Learning. | Entropy (Basel, Switzerland) | NS | CLS | STA | IOV | 10.3390/e26050428 |
| 29 | 2024 | J. Wu | A Novel Few-Shot Deep Transfer Learning Method for Anomaly Detection: Deep Domain-Adversarial Contrastive Network With Time-Frequency Transferability Analytics | IEEE Internet of Things Journal | NML | CLS | STA | IOV | 10.1109/jiot.2024.3403976 |
| 30 | 2024 | L. A. Jilcha | SaRLog: Semantic-Aware Robust Log Anomaly Detection via BERT-Augmented Contrastive Learning | IEEE Internet of Things Journal | MET | DIS | STA | GEN | 10.1109/jiot.2024.3386183 |
| 31 | 2024 | Z. Pu | Incrementally Generative Adversarial Diagnostics Using Few-Shot Enabled One-Class Learning | IEEE Transactions on Industrial Informatics | NML | HYB | INC | IOV | 10.1109/tii.2024.3416945 |
| 32 | 2024 | H. Sun | Space Decoupled Prototype Learning for Few-Shot Attack Detection in Cyber–Physical Systems | IEEE Transactions on Industrial Informatics | MET | DIS | STA | IOV | 10.1109/tii.2024.3423327 |
| 33 | 2024 | U. Zukaib | Meta-IDS: Meta-Learning-Based Smart Intrusion Detection System for Internet of Medical Things (IoMT) Network | IEEE Internet of Things Journal | NS | CLS | STA | IOV | 10.1109/jiot.2024.3387294 |
| 34 | 2024 | K. Li | Reweighted Regularized Prototypical Network for Few-Shot Fault Diagnosis | IEEE Transactions on Neural Networks and Learning Systems | MET | DIS | STA | IOV | 10.1109/tnnls.2022.3232394 |
| 35 | 2024 | L. Du | A Few-Shot Class-Incremental Learning Method for Network Intrusion Detection | IEEE Transactions on Network and Service Management | NS | CLS | INC | IOV | 10.1109/tnsm.2023.3332284 |
| 36 | 2025 | Jiaxi Li | An Anomaly Detection Approach for Aerospace Telemetry Data Based on Model-Agnostic Meta-Learning | IFAC-PapersOnLine | OPT | REC | STA | IOV | 10.1016/j.ifacol.2025.11.424 |
| 37 | 2025 | Yutian Wang | Few-Shot Learning for Anomaly Detection in Gas-Fired Power Plants Using Prototypical Networks | Informatica | MET | DIS | STA | IOV | 10.31449/inf.v49i36.12350 |
| 38 | 2025 | N. Ijaz | A Hybrid LATAM and Few-Shot Learning Framework for Fault Diagnosis in Wireless Sensor Networks | IEEE Sensors Journal | MET | HYB | STA | IOV | 10.1109/jsen.2025.3620491 |
| 39 | 2025 | Ming Wan | One-Class Anomaly Detection for Industrial Data Traffic Based on Dual-Characteristic Prototype Points | 2025 IEEE International Symposium on Parallel and Distribute | MET | DIS | STA | IOV | 10.1109/ispa67752.2025.00089 |
| 40 | 2025 | David He | Full Ceramic Bearing Fault Diagnosis with Few-Shot Learning Using GPT-2 | Computer Modeling in Engineering & Sciences | MOD | CLS | STA | IOV | 10.32604/cmes.2025.063975 |
| 41 | 2025 | Ravindra Chopparapu | Implementation of an Optimized Hybrid Machine Learning–Based IDS for Enhanced Threat Detection in IoT Environments | 2025 IEEE 5th International Conference on ICT in Business In | NS | CLS | STA | IOV | 10.1109/ictbig68706.2025.11323664 |
| 42 | 2025 | Ali Pourghoraba | Model-Agnostic Meta-Learning for Fault Diagnosis of Induction Motors in Data-Scarce Environments with Varying Operating Conditions and Electric Drive Noise | IEEE Transactions on Energy Conversion | OPT | CLS | STA | IOV | 10.1109/tec.2025.3556100 |
| 43 | 2025 | Ying Yu | A novel few-shot cross-domain fault diagnosis method enhanced by feature fusion and ReLU-KAN | Engineering Research Express | NS | CLS | STA | IOV | 10.1088/2631-8695/adcc77 |
| 44 | 2025 | Minke Zou | HySAM: A Hybrid Similarity-Enhanced Attention-Driven Network for Multi-Scale Few-Shot Learning in Belt Conveyor Roller Fault Detection | Proceedings of the 4th International Conference on Computer, | MET | DIS | STA | IOV | 10.1145/3727648.3727708 |
| 45 | 2025 | Wei Gao | Metric-Based Meta-Learning Relation Network for Cross-Domain Few-Shot Bearing Fault Diagnosis | IEEE Sensors Journal | MET | DIS | STA | IOV | 10.1109/jsen.2025.3547258 |
| 46 | 2025 | Yuanfa Cen | Integration of Normalizing Flows and Prototypical Networks for Few-Shot Early Fault Detection in Transformer | 2025 5th International Conference on Electrical Engineering  | HYB | HYB | STA | IOV | 10.1109/ic2ecs68700.2025.11362286 |
| 47 | 2025 | Yanfei Liu | A novel temporal classification prototype network for few-shot bearing fault detection. | Scientific reports | MET | DIS | STA | IOV | 10.1038/s41598-025-98963-4 |
| 48 | 2025 | Ji-Min Woo | Meta-Learning-Based LSTM-Autoencoder for Low-Data Anomaly Detection in Retrofitted CNC Machine Using Multi-Machine Datasets | Systems | OPT | REC | STA | IOV | 10.3390/systems13070534 |
| 49 | 2025 | Muyan Yao | Rethinking Discrepancy Analysis: Anomaly Detection via Meta-Learning Powered Dual-Source Representation Differentiation | IEEE Transactions on Automation Science and Engineering | NS | REC | STA | IOV | 10.1109/tase.2024.3486688 |
| 50 | 2025 | S. Zhu | Partially-Supervised Graph Derivation Network With Meta-Learning for Time-Series Anomaly Detection | IEEE Internet of Things Journal | OPT | HYB | STA | GEN | 10.1109/jiot.2025.3558273 |
| 51 | 2025 | O. S. Ogunleye | Hybrid Meta-Deep Learning Approach for Malicious Data Classification in Iot Packet Data Networks | 2025 8th Conference on Cloud and Internet of Things (CIoT) | MET | DIS | STA | IOV | 10.1109/ciot67574.2025.11410126 |
| 52 | 2025 | Y. Wang | Fault Diagnosis for Pneumatic Control Valves Using a Novel Few-shot Learning Method | 2025 CAA Symposium on Fault Detection, Supervision, and Safe | OPT | CLS | STA | IOV | 10.1109/safeprocess67117.2025.11267814 |
| 53 | 2025 | N. Ijaz | Few-Shot Transfer Learning-Based Fault Classification in Wireless Sensor Networks | IEEE Access | NML | CLS | STA | IOV | 10.1109/access.2025.3554748 |
| 54 | 2025 | M. Zabin | Few-Shot Learning-Based Machine Fault Diagnosis Using EMD-Gammatone Spectrogram with Limited Labeled Audio Dataset | 2025 IEEE International Conference on Big Data and Smart Com | NML | CLS | STA | IOV | 10.1109/bigcomp64353.2025.00046 |
| 55 | 2025 | B. Chandrasekaran | Evaluation of Few-Shot Learning with Vision Language Models for Needle Bearing Defect Detection | SoutheastCon 2025 | MOD | CLS | STA | IOV | 10.1109/southeastcon56624.2025.10971495 |
| 56 | 2025 | K. Yi | Pipeline Anomaly Detection Based on KPCA and Cosine Distance Prototypical Network | 2025 IEEE International Conference on Industrial Technology  | MET | DIS | STA | IOV | 10.1109/icit63637.2025.10965214 |
| 57 | 2025 | U. Suleymanov | SSPNet: Semi-Supervised Prototypical Networks for Few-Shot Network Intrusion Detection | MILCOM 2025 - 2025 IEEE Military Communications Conference ( | MET | DIS | STA | IOV | 10.1109/milcom64451.2025.11310333 |
| 58 | 2025 | M. Emadaleslami | Differential Fault Diagnosis in Power Transformers Under Limited Data Condition via Few-Shot Learning | IEEE Transactions on Industrial Informatics | NS | CLS | STA | IOV | 10.1109/tii.2025.3586057 |
| 59 | 2025 | H. Li | A Few-Shot Network Attack Detection Method Based on MAML-L2F Dynamic Parameter Optimization | 2025 China Automation Congress (CAC) | OPT | CLS | STA | IOV | 10.1109/cac67268.2025.11486720 |
| 60 | 2025 | J. Tian | OMLog: Online Log Anomaly Detection for Evolving System With Meta-Learning | IEEE Internet of Things Journal | MOD | PRE | DAW | GEN | 10.1109/jiot.2025.3569628 |
| 61 | 2025 | R. Xu | Cyber Attack Detection for Industrial Control Systems with Few-Shot and Class Imbalance: An Improved DA-LSTM-UNet Scheme | 2025 10th International Conference on Control, Robotics and  | NML | CLS | STA | IIV | 10.1109/crc67523.2025.11288189 |
| 62 | 2025 | W. Xi | MHT: Dual-Layered Meta-Driven Hypernetworks for Unknown Attack Detection | 2025 10th International Conference on Computer and Communica | MOD | CLS | STA | IOV | 10.1109/icccs65393.2025.11069655 |
| 63 | 2025 | D. N. Chi Nam | STRIDE: Spectral-Temporal Representation and Instance-Weighted Domain Expansion | 2025 IEEE International Conference on Data Mining (ICDM) | NML | CLS | STA | IOV | 10.1109/icdm65498.2025.00125 |
| 64 | 2025 | J. Li | MTSNN: A Few-Shot Fine-Grained Diagnosis Framework for Cross-Machine Fault Diagnosis With Heterogeneous Fault Categories | IEEE Transactions on Instrumentation and Measurement | MET | DIS | STA | IOV | 10.1109/tim.2025.3551907 |
| 65 | 2025 | J. Xu | A Novel Approach for Small-Sample Open-Set Fault Diagnosis in Rolling Bearings: Dense-ProtoNet-AE | 2025 CAA Symposium on Fault Detection, Supervision, and Safe | HYB | HYB | STA | IOV | 10.1109/safeprocess67117.2025.11268163 |
| 66 | 2025 | W. Guo | ModelAdaptive Bearing Fault Diagnosis in Small Sample Situations | 2025 CAA Symposium on Fault Detection, Supervision, and Safe | OPT | CLS | STA | IOV | 10.1109/safeprocess67117.2025.11267982 |
