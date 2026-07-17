## Script

Welcome back to Scripps Biomedical Brief for Friday, July seventeenth. Four bioRxiv reports today — a Wnt-pathway degrader that finally explains why a decade of tankyrase enzymatic inhibitors underperformed, a generative-A-I framework from the Baker lab for de novo transmembrane beta-barrel nanopores with custom lumens, a paradoxical G-P-C-R agonist strategy that extends survival in an A-L-S mouse model by driving receptor internalization to release an oligodendrocyte differentiation brake, and a digital twin of in vitro pancreatic islet differentiation that surfaces two new causal regulators of endocrine versus exocrine fate.

Story one is from Chen Chen at U-T Southwestern with Yuemao Shay and Larry Lum, and it reframes a longstanding failure of Wnt drug discovery. Enzymatic tankyrase inhibitors like I-W-R-one and X-A-V-nine-three-nine stabilize the beta-catenin destruction complex on paper but have consistently disappointed in cancer models. The authors show why. Catalytic inhibition traps tankyrase inside the destruction complex, and that trapped tankyrase does something the enzymatic model ignored — it uses a scaffolding function to nucleate large A-X-I-N puncta that visibly rigidify the complex. Fluorescence recovery after photobleaching shows beta-catenin turnover slows to a crawl inside those puncta. Catalytically dead tankyrase mutants still form the puncta, so this is genuinely a scaffolding problem, not an enzymatic one. Their PROTAC, I-W-R-one-P-O-M-A, links the I-W-R-one warhead to pomalidomide for cereblon recruitment, degrades tankyrase with a D-C-fifty around sixty nanomolar, and — critically — dissolves the puncta rather than freezing them. Quantitative proteomics finds essentially no off-target hits across the P-A-R-P family or seventy-nine other N-A-D-dependent enzymes, and beta-catenin suppression is much deeper than what the enzymatic inhibitor achieves. In patient-derived colorectal cancer organoids carrying truncating A-P-C mutations, the degrader kills where the inhibitor does nothing. The general lesson is that when an enzymatic inhibitor plateaus at partial pathway suppression, the target's scaffolding function may be doing the residual signaling — and only degradation removes both.

Story two is a David Baker generative pipeline for de novo transmembrane beta-barrel nanopores. Natural nanopores like alpha-hemolysin have symmetric lumens, which caps the spatial resolution you can extract from sensing or filtration. The team trains R-F-diffusion-two on a curated one-hundred-seventeen-thousand-member transmembrane beta-barrel distillation set — orders of magnitude larger than the seven-hundred structures in the P-D-B — and finetunes ProteinMPNN with an expanded ninety-six-neighbor receptive field for barrel sequence design. Forty-eight designs from ten to sixteen strands express, refold, and conduct ions with clean single-channel traces, and two crystal structures agree with the designed models within one angstrom, including deliberately placed glycine twists on specified strands. Motif scaffolding lets them drop a three-histidine copper coordination site straight into the pore lumen, and single-channel recordings show copper-specific gating that goes away when the histidines are mutated. A larger fourteen-strand design supports helicase-driven single-strand D-N-A threading — the first published enzymatic D-N-A threading trace through an asymmetric de novo nanopore with no soluble domain. And a hydrophobic-thickness-aware sequence design mode produces longer barrels that insert into synthetic block-copolymer-lipid hybrid membranes stable at two-hundred millivolt, where standard barrels fail. This is a step change from parametric or expert-tuned membrane protein design — nanopores as programmable devices with custom lumen chemistry, tunable hydrophobic thickness, and scaffold-ready binding sites.

Story three is Stefano Raffaele, Tiziana Bonifacino, Marta Fumagalli, Marta Lecca, and colleagues on oligodendroglial G-P-R-seventeen as a druggable target in A-L-S. G-P-R-seventeen is a G-P-C-R that is transiently expressed as oligodendrocyte precursors mature and must be downregulated for full myelination — persistent G-P-R-seventeen locks cells in an immature state. Post-mortem human A-L-S spinal cord shows exactly this signature — bulk R-N-A-seq elevation of G-P-R-seventeen across cervical, thoracic, and lumbar levels, single-nucleus data showing an expansion of G-P-R-seventeen-positive immature oligodendrocytes, and immunohistochemistry confirming spinal-cord-restricted accumulation. The counterintuitive move is to hit the receptor with an agonist rather than an antagonist, because sustained agonism drives G-P-R-seventeen internalization and functional downregulation, releasing the differentiation block. Their brain-penetrant second-generation agonist galinex — sub-nanomolar potency in G-T-P-gamma-S — delivered by osmotic minipump at ten milligrams per kilogram per day from the early symptomatic stage extends survival, delays weight loss, and improves rotarod, beam-balance, gait, and grip-strength in female S-O-D-one G-ninety-three-A mice, with restored mature oligodendrocyte density, preserved myelin, and better motor-neuron survival. Male mice show almost none of this, so the sex dependence is real and warrants mechanistic work before translation.

Story four is Jeffrey Millman's group with a digital twin of in vitro pancreatic islet differentiation — four-hundred-thousand cells across sixty-one datasets, four cell lines, seven protocols, anchored on a new single-nucleus multi-omic map through thirty-three days. They run over one thousand in silico transcription-factor knockouts and prospectively validate two. S-T-A-T-one, which had never been implicated in pancreatic development, is predicted to push cells toward exocrine fate. CRISPRi knockdown and ruxolitinib both selectively suppress exocrine markers while leaving beta-cell identity and glucose-stimulated insulin secretion intact. Z-E-B-one plays a dynamic role — early on it is required for endocrine specification, but persistent activity later diverts endocrine progenitors toward an off-target serotonergic islet-cell lineage rather than beta cells. A window-specific short-hairpin knockdown on days fifteen to seventeen collapses serotonin content and boosts the beta-cell fraction without touching insulin content. For a stem-cell-derived islet manufacturing program this is directly actionable — model-nominated regulators with defined intervention windows, translated into small-molecule or CRISPRi handles that steer fate at branch points.

That's the briefing for July seventeenth. Talk to you tomorrow.

---

## Show notes

Paper 1 — Wang, Li, You, Wang, Han, Wang, Yao, Addepalli, Lu, Mender, Flusche, Kim, Yarravarapu, Lemoff, Lum, Shay, Yu, Chen: Targeting tankyrase scaffolding in the β-catenin destruction complex by PROTAC overcomes the limitation of catalytic inhibitors in cancer
Paper link: https://www.biorxiv.org/content/10.1101/2025.09.22.677768v3

Paper 2 — Philomin, Sonigra, Majumder, Lin, Li, Xue, Kibler, Baldus, Trapido, Medeiros, Coventry, Bera, Kang, Mendoza, Kumar, Yang, Baker: Generative design of programmable asymmetric β-barrel nanopores
Paper link: https://www.biorxiv.org/content/10.64898/2026.06.04.729630v2

Paper 3 — Raffaele, Bonifacino, Mannella, Nguyen, Torazza, Marangon, Chinosi, Schroder, Hejbol, Madsen, Marchetti, Trincavelli, Milanese, Lecca et al.: Selective targeting of the oligodendroglial GPR17 receptor improves myelin integrity and motor function in female SOD1G93A mice
Paper link: https://www.biorxiv.org/content/10.64898/2026.04.28.721299v2

Paper 4 — Sanchez-Castro, Ishahak, Le, Maestas, Hernandez-Rincon, Mukherjee, Bradley, Lu, Gale, Millman: Predictive control of human pancreatic cell fate using a digital model of in vitro differentiation
Paper link: https://www.biorxiv.org/content/10.64898/2026.04.27.721124v2

---

## Candidate funnel

bioRxiv preprints scanned 2026-07-15 through 2026-07-17 by category. Yesterday's picks (CRBN covalent glue, ALDH1A3, IL-34/IGF-1 KRAS lung, MDMI) excluded. Full-text availability via scripts/fetch_preprint.py (r.jina.ai proxy) treated as eligibility gate — v1 preprints posted 2026-07-16 all returned abstract-only pages (bioRxiv body-rendering lag <36h). All four selections have full-body renders (v2 or v3 revisions posted 2026-07-15/16), so summaries are grounded in body, not abstract.

- biochemistry: 25 scanned, 6 substantive
  - Cho lab site-specific IPM cholesterol depletion via NPC1L1 flippase inhibition for gastric cancer (10.64898/2026.07.15.738777) — v1 2026-07-16, abstract-only, deferred
  - Malatesta/Mattevi L2HGDH-COQ metabolon structure and CoQ biosynthesis link (10.64898/2026.07.16.738879) — v1 2026-07-16, abstract-only, deferred
  - Philomin/Sonigra/Majumder/Baker generative de novo transmembrane β-barrel nanopores (10.64898/2026.06.04.729630 v2) — full body available — CHOSEN
  - Titze/Kuemmel TSC complex GAP activity for Rheb — v1 abstract-only, deferred
  - Kavrakova/Cho (see above)
  - Chen/Qin RNA-dependent thermal proteome profiling atlas (10.64898/2026.07.15.738841) — v1, abstract-only, deferred
- pharmacology and toxicology: 6 scanned, 3 substantive
  - Raffaele/Bonifacino/Fumagalli/Lecca GPR17 agonist galinex in SOD1G93A ALS (10.64898/2026.04.28.721299 v2) — full body — CHOSEN
  - Chen/Roy tioxazafen CYP1A1 bioactivation → proteasome disruption (10.64898/2026.07.10.737828) — v1, abstract-only, deferred
  - AlJamal-Naylor β1 integrin hybrid domain allosteric modulator — considered, murine only
- bioengineering: 20 scanned, 3 substantive
  - Wang/Demirer PseCAST/evoCAST programmable DNA integration in plants (10.64898/2026.07.15.738807) — v1, abstract-only, deferred (also plant scope less Schultz-relevant)
  - HEK293 EV bioreactor (10.64898/2026.07.14.738239 v2) — considered, incremental
- cell biology: 25 scanned, 3 substantive
  - Sanchez-Castro/Ishahak/Millman digital twin of SC-islet differentiation validates STAT1 (exocrine) + ZEB1 (SIC vs β) (10.64898/2026.04.27.721124 v2) — full body — CHOSEN
  - Necroptotic keratinocyte differentiation slowing wound healing (10.64898/2026.07.13.738083) — v1 abstract, considered
  - Sonication-induced fragmentation of IDRs in proteomics — considered, methods paper
- cancer biology: 22 scanned, 6 substantive
  - Wang/Lu/Mender/Lum/Shay/Chen TNKS PROTAC (IWR1-POMA) reveals TNKS scaffolding is the barrier to WNT drug efficacy (10.1101/2025.09.22.677768 v3) — full body — CHOSEN
  - Rihtar/Jerala bioorthogonal tamoxifen-inducible / ARV-471-degradable ER-degron CAR (10.64898/2026.07.15.738628) — v1 abstract-only, deferred (very Schultz — revisit)
  - Suzuki/Bird Tegavivint (TBL1 inhibitor) in Wnt-activated HCC (10.64898/2026.07.14.738585) — v1 abstract-only, deferred
  - Mukherjee/Somasundaram SEZ6 as GSC-specific proangiogenic target via TGFβRII — v1 abstract-only, deferred
  - Ataca Atilla/Green BCMA density trogocytosis attenuates CAR T (10.64898/2026.07.15.738803) — v1 abstract-only, deferred
  - WNT11 suppresses tumor initiation via RAC1 — v1 abstract-only, deferred
- immunology: 8 scanned, 3 substantive
  - Solli/Wei/Li Fas-FADD-CASP8 as cancer cell-intrinsic determinant of CTL killing beyond executioner caspases (10.64898/2026.06.14.732110 v2) — full body — considered runner-up
  - Ibanez Molero/van Kooyk SIGLEC1 macrophage-CD8 T-cell interactions and ICB response — v1 abstract-only, deferred
  - LARP4 B-cell metabolic checkpoint for SLE plasma cells — v1 abstract-only, deferred
- systems biology: 4 scanned, 2 substantive
  - Baugh/Ergun DRUG-seq atlas across primary cell types (10.1101/2025.06.03.657593 v2) — full body — considered runner-up
- microbiology: 12 scanned, 2 substantive
  - Chen/Roy persiathiacin biosynthesis P450 antitubercular intermediate (10.64898/2026.07.09.737402 v2) — considered
- synthetic biology: 2 scanned, 1 substantive
  - Rihtar/Jerala CAR T ON/OFF switch (see cancer above)

No source-side failures on today's run. Selections weight toward papers with body rendered so summaries reflect the paper, not just the abstract. Rihtar/Jerala CAR-T ER-degron switch, Tegavivint HCC Ph3-adjacent preclinical, Baker β-barrel companion Kavrakova/Cho NPC1L1 flippase, and RNA-dependent TPP atlas all worth revisiting on later days once body renders.
