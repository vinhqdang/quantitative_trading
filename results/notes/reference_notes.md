# Reference notes

Notes are based only on the abstract text fetched for each entry. Entries without a fetched abstract are marked ABSTRACT NOT FOUND.

## becker1968

- key: becker1968
- citation: Becker, 1968, Journal of Political Economy
- data/setting: not available
- method: not available
- finding: not available
- labels/accounts: not available
- relevance: not available
- abstract_source: ABSTRACT NOT FOUND

## polinsky2000

- key: polinsky2000
- citation: Polinsky, 2000, Journal of Economic Literature
- data/setting: survey of the theory of public enforcement of law (no data stated)
- method: survey of the theory of public enforcement, covering sanctions, probability of imposition and extensions such as marginal deterrence and imperfect knowledge
- finding: The article surveys the theory of public enforcement of law, first presenting its basic elements (probability of imposition of sanctions, magnitude and form of sanctions, rule of liability) and then a variety of extensions.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract describes the theory of using public agents to detect and sanction violators of legal rules, which is the enforcement setting that policy evaluation concerns; it says nothing about manipulation or markets.
- abstract_source: Crossref API https://api.crossref.org/works/10.1257/jel.38.1.45 (field 'abstract')

## aggarwal2006

- key: aggarwal2006
- citation: Aggarwal, 2006, The Journal of Business
- data/setting: data from SEC enforcement actions on stock price manipulation, plus a theory model
- method: theory of manipulators trading alongside information seekers, with empirical evidence
- finding: Manipulation increases volatility, liquidity, and returns, prices rise throughout the manipulation period and fall postmanipulation, and the SEC data show that manipulators typically are plausibly informed parties (insiders, brokers, etc.).
- labels/accounts: labelled cases: yes (SEC enforcement action data); account-level identifiers: not stated
- relevance: The abstract reports empirical and theoretical results on stock price manipulation based on enforcement-action cases, which bears on the study's manipulation setting; it does not address detection or coordination among accounts.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1086/503652 (abstract_inverted_index)

## comerton2014

- key: comerton2014
- citation: Comerton-Forde, 2014, Review of Finance
- data/setting: empirical analysis of closing price manipulation and its detection (data source not stated in abstract)
- method: empirical estimation of prevalence and determinants of closing price manipulation
- finding: The authors estimate that ~1% of closing prices are manipulated, of which only a small fraction is detected and prosecuted, and that government regulatory budget has a strong effect on both manipulation and detection.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract concerns how much manipulation occurs and how little is detected and prosecuted, and links regulatory budget to manipulation and detection, which relates to enforcement and policy; it does not describe account-level or label-free methods.
- abstract_source: Crossref API https://api.crossref.org/works/10.1093/rof/rfs040 (field 'abstract')

## khwaja2005

- key: khwaja2005
- citation: Khwaja, 2005, Journal of Financial Economics
- data/setting: not available
- method: not available
- finding: not available
- labels/accounts: not available
- relevance: not available
- abstract_source: ABSTRACT NOT FOUND

## wang2020

- key: wang2020
- citation: Wang, 2020, Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence
- data/setting: simulated order streams associated with a manipulator and a market-making agent in an agent-based simulator
- method: adversarial learning framework with a generator, a discriminator and an agent-based simulator
- finding: The authors show examples of adapted manipulation order streams that mimic a specified market maker's quoting patterns yet appear qualitatively different from the original manipulation strategy, demonstrating the possibility of automatically generating a diverse set of (unseen) manipulation strategies that can facilitate the training of more robust detection algorithms.
- labels/accounts: labelled cases: not stated (simulated order streams of a manipulator and a market maker); account-level identifiers: not stated
- relevance: The abstract models a game between a regulator developing detection tools and a manipulator evading detection, evaluated with an agent-based simulator, which parallels the study's use of simulation to examine manipulation and detection.
- abstract_source: Crossref API https://api.crossref.org/works/10.24963/ijcai.2020/638 (field 'abstract')

## wang2018

- key: wang2018
- citation: Wang, 2018, Proceedings of the Twenty-Seventh International Joint Conference on Artificial Intelligence
- data/setting: simulated markets with background traders and a spoofing exploiter
- method: cloaking mechanism (concealing price levels in the order book) studied by empirical game-theoretic analysis
- finding: Across parametrically different environments, the authors characterize the conditions under which cloaking mitigates manipulation and benefits market welfare, and find that the effort and risk of sophisticated spoofing strategies that probe to reveal cloaked information exceed the gains.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract evaluates a market-design mechanism against manipulation inside a simulated market, which is comparable to policy evaluation in an agent-based market; it concerns spoofing and not coordination among accounts.
- abstract_source: Crossref API https://api.crossref.org/works/10.24963/ijcai.2018/75 (field 'abstract')

## cartea2020

- key: cartea2020
- citation: Cartea, 2020, Applied Mathematical Finance
- data/setting: model of an investor who spoofs the limit order book to sell a position (no empirical data stated)
- method: stochastic control model of a spoofing strategy trading off spoofing gains against an expected fine
- finding: As the fine increases the investor relies less on spoofing and, if the fine is large, does not spoof, while when the fine is low spoofing considerably increases the revenues from liquidating a position.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract links the size of a fine imposed by authorities to the extent of spoofing in a limit order book, which relates to evaluating penalty policies; it concerns a single spoofer and not coordination among accounts.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1080/1350486X.2020.1726783 (abstract_inverted_index)

## leal2019

- key: leal2019
- citation: Leal, 2019, Journal of Economic Behavior & Organization
- data/setting: agent-based model of a limit order book with low- and high-frequency traders that generates flash crashes
- method: Monte-Carlo simulations of regulatory policies (minimum resting times, circuit breakers, cancellation fees, transaction taxes)
- finding: HFT-targeted policies imply a trade-off between market stability and resilience, since policies able to tackle volatility and flash crashes also hinder the market from quickly recovering after a crash.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract evaluates regulatory policies by simulation in an agent-based limit order book market, which is the same general approach as the study's policy evaluation; it does not address manipulation detection.
- abstract_source: Semantic Scholar API https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.jebo.2017.04.013?fields=abstract

## zhang2016

- key: zhang2016
- citation: Zhang, 2016, PLOS ONE
- data/setting: artificial stock market whose trading mechanisms are the same as China's stock market
- method: agent-based simulations with and without price limits
- finding: Both upper and lower price limits can cause a volatility spillover effect and a trading interference effect, and price discovery is delayed when upper price limits are imposed but not when lower price limits are imposed.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract tests a market policy (price limits) by agent-based simulation of an artificial stock market, which parallels the study's policy evaluation; it does not address manipulation.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1371/journal.pone.0160406 (abstract_inverted_index)

## zhao2020

- key: zhao2020
- citation: Zhao, 2020, Frontiers in Physics
- data/setting: agent-based multiple-order-book stock-market model with small-, medium- and large-cap stocks
- method: agent-based simulation of tick size and market quality
- finding: Small-cap stocks were of the lowest quality, and quality was generally weakened as tick-size value increased, with expanded bid-ask spreads, elevated market volatility, and reduced market efficiency.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract examines a market-structure parameter (tick size) with an agent-based order-book model, which is an example of simulation-based policy evaluation; it does not address manipulation.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.3389/fphy.2020.00135 (abstract_inverted_index)

## byrd2020

- key: byrd2020
- citation: Byrd, 2020, Proceedings of the 2020 ACM SIGSIM Conference on Principles of Advanced Discrete Simulation
- data/setting: ABIDES, an agent-based discrete event simulation of tens of thousands of trading agents interacting with an exchange agent, modelled after NASDAQ's ITCH and OUCH protocols
- method: open source agent-based interactive discrete event market simulator
- finding: The authors introduce ABIDES, validate it with example trading scenarios and illustrate its use for financial research through experiments to develop a market impact model.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract presents an open source high-fidelity multi-agent market simulation environment, so it is a candidate platform for an agent-based market; it says nothing about manipulation or calibration of the kind used in this study.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1145/3384441.3395986 (abstract_inverted_index)

## vyetrenko2019

- key: vyetrenko2019
- citation: Vyetrenko, 2020, Proceedings of the First ACM International Conference on AI in Finance
- data/setting: real limit order book market data compared with five simulated market configurations (market replay and four interactive agent-based simulation configurations)
- method: realism metrics based on stylized facts of limit order book markets
- finding: Markets exhibit more realistic behavior when the fundamental in the agent-based simulation arises from historical market data, and the authors further experimentally illustrate the effectiveness of IABS techniques as opposed to market replay.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract proposes measurable stylized-fact metrics to benchmark how realistic simulated limit order book markets are, which relates to assessing the realism of a calibrated agent-based market.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1145/3383455.3422561 (abstract_inverted_index)

## platt2018

- key: platt2018
- citation: Platt, 2018, Physica A: Statistical Mechanics and its Applications
- data/setting: intraday agent-based models of continuous-time double auction markets (data not detailed in abstract)
- method: calibration of agent-based models rooted in market microstructure
- finding: The parameters of intraday agent-based models rooted in market microstructure can be meaningfully calibrated, but those exclusively related to agent behaviors and incentives remain problematic.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract reports that agent-behaviour parameters of microstructure-based agent-based models remain problematic to calibrate, which is relevant to the calibration limits of an agent-based market used for policy evaluation.
- abstract_source: Semantic Scholar API https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.physa.2018.08.055?fields=abstract

## xu2019

- key: xu2019
- citation: Xu, 2019, 28th USENIX Security Symposium (USENIX Security 19)
- data/setting: 412 pump-and-dump activities organized in Telegram channels from June 17, 2018 to February 26, 2019, in cryptocurrency markets
- method: empirical case study and a model predicting the pump likelihood of coins listed on an exchange before a pump
- finding: The model exhibits high precision and robustness and can be used for a trading strategy that the authors empirically demonstrate can generate a return as high as 60% on small retail investments within a span of two and half months.
- labels/accounts: labelled cases: yes (412 identified pump-and-dump activities used to build a predictive model); account-level identifiers: not stated
- relevance: The abstract concerns coordinated pump-and-dump schemes organized in Telegram channels in cryptocurrency markets and a model predicting pumped coins; it does not state use of account-level identifiers or label-free detection.
- abstract_source: arXiv API https://export.arxiv.org/api/query?id_list=1811.10109 (arXiv version of the paper, used because no abstract was found at Crossref/OpenAlex/Semantic Scholar for the USENIX entry)

## kamps2018

- key: kamps2018
- citation: Kamps, 2018, Crime Science
- data/setting: trading data on cryptocurrency pump-and-dump schemes, with several real-world cases examined
- method: criteria defining a cryptocurrency pump-and-dump plus anomaly detection techniques to flag anomalous trading activity
- finding: The findings suggest that there are some signals in the trading data that might help detect pump-and-dump schemes, and fraudulent activity clusters on specific cryptocurrency exchanges and coins.
- labels/accounts: labelled cases: not stated (detection is demonstrated by examining several real-world cases); account-level identifiers: not stated
- relevance: The abstract applies anomaly detection to trading data to flag pump-and-dump manipulation in cryptocurrency markets, which relates to detecting manipulation from trading-data anomalies; it does not mention accounts.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1186/s40163-018-0093-5 (abstract_inverted_index)

## lamorgia2020

- key: lamorgia2020
- citation: La Morgia, 2020, 2020 29th International Conference on Computer Communications and Networks (ICCCN)
- data/setting: pump and dump schemes organized by communities over the Internet in cryptocurrency markets, with two case studies
- method: in-depth analysis of pump and dump groups and a real-time fraud detection approach
- finding: The authors introduce an approach to detect the fraud in real time that outperforms the current state of the art.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract studies community-organized (coordinated) pump and dump schemes and a real-time detector for them; it states no details on labels or account identifiers.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1109/ICCCN49398.2020.9209660 (abstract_inverted_index)

## lamorgia2023

- key: lamorgia2023
- citation: La Morgia, 2023, ACM Transactions on Internet Technology
- data/setting: groups monitored on Telegram and Discord for more than 3 years (around 900 individual events), plus the Reddit-driven GameStop, DogeCoin and Ripple crowd pumps
- method: machine learning model to detect a pump and dump, plus case studies
- finding: The machine learning model detects a pump and dump in 25 seconds from the moment it starts, achieving 94.5% of F1-score.
- labels/accounts: labelled cases: yes (a unique dataset of verified pump and dumps); account-level identifiers: not stated
- relevance: The abstract concerns highly coordinated groups arranging pump and dumps and a machine learning detector built from a dataset of verified events; it does not state use of account-level identifiers.
- abstract_source: Crossref API https://api.crossref.org/works/10.1145/3561300 (field 'abstract')

## hu2022

- key: hu2022
- citation: Hu, 2023, Proceedings of the ACM on Management of Data
- data/setting: 709 pump-and-dump events organized in Telegram from Jan. 2019 to Jan. 2022
- method: sequence-based neural network (SNN) with positional attention, encoding a channel's pump-and-dump event history, for target coin prediction
- finding: Pumped coins exhibit intra-channel homogeneity and inter-channel heterogeneity, and extensive experiments verify the effectiveness and generalizability of the proposed methods.
- labels/accounts: labelled cases: yes (709 pump-and-dump events used for the prediction task); account-level identifiers: not stated
- relevance: The abstract concerns coordinated pump-and-dump events organized in Telegram channels and a sequence-based neural network; it does not state use of account-level identifiers or label-free detection.
- abstract_source: Crossref API https://api.crossref.org/works/10.1145/3588686 (field 'abstract')

## dhawan2023

- key: dhawan2023
- citation: Dhawan, 2023, Review of Finance
- data/setting: a sample of 355 cryptocurrency pump-and-dump cases over 6 months
- method: simple framework of overconfidence and gambling preferences, with empirical analysis
- finding: Pumps generate extreme price distortions of 65% on average, abnormal trading volumes in the millions of dollars, and large wealth transfers between participants, and the authors find strong empirical support for both overconfidence and gambling preferences as explanations.
- labels/accounts: labelled cases: yes (355 identified pump-and-dump cases); account-level identifiers: not stated
- relevance: The abstract concerns openly declared, coordinated cryptocurrency pump-and-dump schemes and why people participate; it does not address detection methods.
- abstract_source: Crossref API https://api.crossref.org/works/10.1093/rof/rfac051 (field 'abstract')

## cong2023

- key: cong2023
- citation: Cong, 2023, Management Science
- data/setting: 29 centralized cryptocurrency exchanges (regulated and unregulated)
- method: systematic tests based on statistical and behavioral regularities of authentic trading (first significant digit distributions, size rounding, transaction tail distributions)
- finding: The wash trading quantified on each unregulated exchange averaged more than 70% of the reported volume.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract detects fake (wash) transactions through regularities in transaction data rather than through stated labels, which is related to label-free detection; it works at the exchange level and states nothing on accounts.
- abstract_source: Crossref API https://api.crossref.org/works/10.1287/mnsc.2021.02709 (field 'abstract'); the OpenAlex abstract is a shorter variant with the same 70% figure

## victor2021

- key: victor2021
- citation: Victor, 2021, Proceedings of the Web Conference 2021
- data/setting: two limit order book-based decentralized exchanges on the Ethereum blockchain, IDEX and EtherDelta
- method: identification of accounts and trading structures that meet legal definitions of wash trading
- finding: The authors identify a lower bound of accounts and trading structures meeting the legal definitions of wash trading, responsible for a wash trading volume equivalent to 159 million U.S. Dollars, and find that on both exchanges more than 30% of all traded tokens have been subject to wash trading activity.
- labels/accounts: labelled cases: not stated (legal definitions are applied to identify cases); account-level identifiers: yes (accounts and trading structures)
- relevance: The abstract identifies wash trading at the level of accounts and multi-account trading structures on limit order book exchanges, which is closely related to detecting coordination among accounts.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1145/3442381.3449824 (abstract_inverted_index)

## palshikar2008

- key: palshikar2008
- citation: Palshikar, 2008, Data Mining and Knowledge Discovery
- data/setting: a trading database of stock market trades, with detailed simulation experiments
- method: graph clustering algorithms for collusion sets, combined using Dempster-Schafer theory of evidence
- finding: The authors present detailed simulation experiments to demonstrate the effectiveness of the proposed algorithms.
- labels/accounts: labelled cases: not stated; account-level identifiers: yes (sets of traders in the trading database)
- relevance: The abstract detects collusion sets, defined as traders with heavy trading among themselves relative to trading with others, in a trading database, which is directly related to detecting coordinated groups of accounts.
- abstract_source: Springer page https://link.springer.com/article/10.1007/s10618-007-0076-8 (abstract shown on the publisher page; Crossref, OpenAlex and Semantic Scholar had none)

## cao2016

- key: cao2016
- citation: Cao, 2016, IEEE Transactions on Neural Networks and Learning Systems
- data/setting: seven stock data sets from the NASDAQ and the London Stock Exchange
- method: directed graph of traders, with suspiciously matched orders and trader collusions detected by dynamic programming formulated as a simplified knapsack problem
- finding: The experimental results show that the proposed approach can effectively detect all primary wash trade scenarios across the selected data sets.
- labels/accounts: labelled cases: not stated; account-level identifiers: yes (collusions among the traders who submit the matched orders)
- relevance: The abstract detects wash trade collusion among traders from order data using a trader graph, which is related to detecting coordination among accounts.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1109/TNNLS.2015.2480959 (abstract_inverted_index)

## sun2012

- key: sun2012
- citation: Sun, 2012, PLoS ONE
- data/setting: transaction data of eight manipulated stocks and forty-four non-manipulated stocks during a one-year period
- method: trading networks with statistical significance analysis of degree-strength correlation
- finding: The trading networks of manipulated stocks exhibit significantly higher degree-strength correlation than those of non-manipulated stocks and randomized trading networks, and the method outperforms the traditional weight-threshold method at identifying anomalous traders and is difficult to be fooled by colluded traders.
- labels/accounts: labelled cases: yes (stocks classed as manipulated or non-manipulated); account-level identifiers: yes (trading networks and anomalous traders)
- relevance: The abstract identifies colluding anomalous traders from trading networks using a significance test against randomized networks, which is closely related to network-based detection of coordination among accounts.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.1371/journal.pone.0045598 (abstract_inverted_index)

## jaeger2025

- key: jaeger2025
- citation: Jaeger, 2025, arXiv preprint 2512.18918
- data/setting: 2.9 million trades reported to the U.S. Securities and Exchange Commission by company insiders between 2014 and 2024
- method: weighted network of insiders based on temporal similarity of trades, with central nodes and anomalous subgraphs, evaluated against two null models
- finding: The results indicate that the approach can be used to detect pairs or clusters of insiders whose behaviour suggests insider trading and/or market manipulation.
- labels/accounts: labelled cases: no (motivated by the limited availability of labelled data; validity is checked with null models); account-level identifiers: yes (edges between insiders)
- relevance: The abstract proposes a label-free network approach that flags coordinated transactions among insiders using temporal similarity of trades and null-model evaluation, which is closely related to this study's aim.
- abstract_source: arXiv API https://export.arxiv.org/api/query?id_list=2512.18918

## saavedra2011

- key: saavedra2011
- citation: Saavedra, 2011, Proceedings of the National Academy of Sciences
- data/setting: empirical data on day traders' second-to-second trading and instant messaging
- method: measure of individual synchronous trading compared with others' simultaneous activity
- finding: The higher the traders' synchronous trading is, the less likely they are to lose money at the end of the day, and the daily instant messaging patterns of traders are closely associated with their level of synchronous trading.
- labels/accounts: labelled cases: not stated; account-level identifiers: yes (individual traders' activity patterns)
- relevance: The abstract measures the simultaneity of individual traders' activity with that of other traders at second-level resolution; it relates this to performance and messaging and does not address manipulation.
- abstract_source: Crossref API https://api.crossref.org/works/10.1073/pnas.1018462108 (field 'abstract')

## tuccella2021

- key: tuccella2021
- citation: Tuccella, 2021, arXiv preprint 2110.03687
- data/setting: granular order book data from a largely unregulated market with many non-institutional traders
- method: Gated Recurrent Unit (GRU) model for spoofing detection
- finding: The results show that the model performs well in an early detection context, allowing identification of spoofing attempts soon enough to allow investors to react.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract detects spoofing, a market manipulation technique, from order book data with a neural model; it does not state labels or account identifiers.
- abstract_source: arXiv API https://export.arxiv.org/api/query?id_list=2110.03687

## fabre2025

- key: fabre2025
- citation: Fabre, 2025, arXiv preprint 2504.15908
- data/setting: Level-3 limit order book data from a cryptocurrency centralized exchange, with the period 2024-12-04 to 2024-12-07 scanned
- method: neural network predicting the conditional distribution of mid price movements from Hawkes-process order flow variables, used to compute a spoofer's expected gain
- finding: Running the algorithm on all submitted limit orders in the period 2024-12-04 to 2024-12-07, the authors find that 31% of large orders could spoof the market.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract detects spoofing in limit order books from order flow and a probabilistic gain computation, a manipulation form studied in order-book markets; it does not mention account identifiers or coordination.
- abstract_source: arXiv API https://export.arxiv.org/api/query?id_list=2504.15908

## liang2025

- key: liang2025
- citation: Liang, 2025, arXiv preprint 2512.17372
- data/setting: time series coincidence detection, with simulated and real data (applications named include astrophysics and neuroscience)
- method: time-shifting methods, where one data stream's timeline is randomly shifted relative to another
- finding: The theoretical results establish rigorous finite-sample guarantees controlling the probability of false positives under weak assumptions allowing dependence within the time series data.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract provides false-positive guarantees for deciding whether simultaneous events in time series reflect a shared signal or random chance, which is relevant to calibrating coincidence-based detection; it does not mention financial markets.
- abstract_source: arXiv API https://export.arxiv.org/api/query?id_list=2512.17372

## platkiewicz2017

- key: platkiewicz2017
- citation: Platkiewicz, 2017, Neural Computation
- data/setting: spike trains (point processes) in neurophysiology, with explicit examples and numerical illustration
- method: analysis of spike-centered jitter versus interval jitter resampling as hypothesis tests
- finding: For processes with no temporal structure, interval jitter generates an exact hypothesis test guaranteeing valid conclusions, whereas such a guarantee is not available for spike-centered jitter, which can show exaggerated false-positive rates.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract concerns the validity and false-positive rates of jitter resampling tests for temporal structure in point processes; it does not mention financial markets.
- abstract_source: Crossref API https://api.crossref.org/works/10.1162/NECO_a_00927 (field 'abstract')

## amarasingham2012

- key: amarasingham2012
- citation: Amarasingham, 2012, Journal of Neurophysiology
- data/setting: spiking activity of central neurons, with simulation experiments and selected analyses of spike data from motor cortical neurons
- method: review of jitter resampling techniques within a conditional modeling framework
- finding: The authors review a wide range of jitter techniques, including statistical tests for limits on the rate of change of spiking probabilities and exact tests for the significance of repeated fine-temporal patterns of spikes.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract reviews resampling (jitter) methods for statistically valid hypothesis tests of fine-temporal structure and synchrony; it does not mention financial markets.
- abstract_source: Crossref API https://api.crossref.org/works/10.1152/jn.00633.2011 (field 'abstract')

## grun2009

- key: grun2009
- citation: Grün, 2009, Journal of Neurophysiology
- data/setting: simultaneous (parallel) spike trains, illustrated with the Unitary Events method
- method: review of significance estimation for precise spike correlation using surrogate data
- finding: Nonstationarity of firing, spike train structure deviating from Poisson, or a co-occurrence of such features are potent generators of false positives, and problems can be avoided by including these features in the null hypothesis of the significance test.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract concerns building appropriate null hypotheses and surrogate data to avoid false positives when testing for spike coordination, and emphasizes testing and calibration of analysis tools; it does not mention financial markets.
- abstract_source: Crossref API https://api.crossref.org/works/10.1152/jn.00093.2008 (field 'abstract')

## louis2010

- key: louis2010
- citation: Louis, 2010, Frontiers in Computational Neuroscience
- data/setting: spike trains, for detecting excess spike synchrony
- method: surrogate spike train generation through dithering in operational time
- finding: The two proposed surrogate methods conserve both the firing rate and the inter-spike interval statistics with high accuracy and show an improved robustness in detecting excess synchrony compared to earlier approaches.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract proposes surrogate methods that preserve rate and interval statistics for significance testing of synchrony; it does not mention financial markets.
- abstract_source: OpenAlex API https://api.openalex.org/works/doi:10.3389/fncom.2010.00127 (abstract_inverted_index)

## mcmahan2003

- key: mcmahan2003
- citation: McMahan, 2003, Proceedings of the Twentieth International Conference on Machine Learning (ICML-2003)
- data/setting: not available
- method: not available
- finding: not available
- labels/accounts: not available
- relevance: not available
- abstract_source: ABSTRACT NOT FOUND

## lanctot2017

- key: lanctot2017
- citation: Lanctot, 2017, Advances in Neural Information Processing Systems 30 (NeurIPS 2017)
- data/setting: multiagent reinforcement learning, tested in two partially observable settings: gridworld coordination games and poker
- method: algorithm based on approximate best responses to mixtures of policies from deep reinforcement learning, with empirical game-theoretic analysis for meta-strategies
- finding: Policies learned with independent reinforcement learning can overfit to the other agents' policies during training, and the authors introduce a joint-policy correlation metric to quantify this and an algorithm that generalizes InRL, iterated best response, double oracle, and fictitious play.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract concerns multiagent reinforcement learning with empirical game-theoretic analysis; it does not mention markets or manipulation.
- abstract_source: arXiv API https://export.arxiv.org/api/query?id_list=1711.00832 (arXiv version of the paper, used because no abstract was found at Crossref/OpenAlex/Semantic Scholar for the proceedings entry)

## avenhaus2002

- key: avenhaus2002
- citation: Avenhaus, 2002, Handbook of Game Theory with Economic Applications
- data/setting: not available
- method: not available
- finding: not available
- labels/accounts: not available
- relevance: not available
- abstract_source: ABSTRACT NOT FOUND

## nguyen2017

- key: nguyen2017
- citation: Nguyen, 2017, Journal of International Money and Finance
- data/setting: not available
- method: not available
- finding: not available
- labels/accounts: not available
- relevance: not available
- abstract_source: ABSTRACT NOT FOUND

## nguyen2023

- key: nguyen2023
- citation: Nguyen, 2024, Journal of Economic Studies
- data/setting: daily stock closing prices of 425 firms on the Ha Noi and Ho Chi Minh stock exchanges, 2018 to the first half of 2022
- method: herding behavior tests across COVID-19 periods, conditioned on market liquidity and information demand
- finding: The research confirms the existence of herding behavior for the whole period and during and post-COVID periods, robust in both bull and bear markets, with herding more evident at the medium market liquidity level than at high and low levels.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract provides evidence of herding in Vietnam's stock exchanges using daily closing prices; it does not mention manipulation, accounts or detection.
- abstract_source: Crossref API https://api.crossref.org/works/10.1108/JES-01-2023-0031 (field 'abstract')

## vo2023

- key: vo2023
- citation: Vo, 2023, PLOS ONE
- data/setting: intraday trade and quote data of all stocks listed on the Ho Chi Minh Stock Exchange before and after the minimum tick size change of 12 September 2016
- method: before-and-after analysis of a tick size policy change
- finding: The trading cost is reduced following the change to the smallest tick size, although this differs for large trades executed at the stock price associated with a larger tick size.
- labels/accounts: labelled cases: not stated; account-level identifiers: not stated
- relevance: The abstract evaluates a tick size policy change on market quality and trade execution costs in the Vietnamese market using intraday data; it does not mention manipulation.
- abstract_source: Crossref API https://api.crossref.org/works/10.1371/journal.pone.0285821 (field 'abstract')
