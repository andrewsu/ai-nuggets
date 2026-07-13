## Script

Welcome back to Scripps Biomedical Brief for Monday, July thirteenth. Four bioRxiv preprints from the last twenty-four to forty-eight hours — a T-cell-directed C-A-R-T strategy for rheumatoid arthritis that wires cytotoxicity to the inflamed synovium and pairs it with local immunomodulatory secretion, cryo-E-M structures of the human sodium-citrate cotransporter that pin down how sodium and substrate arrive together, a rigorous benchmark showing every current AI structure predictor collapses onto a dominant P-D-B state and is nearly blind to small molecules, and an organ-on-chip comparison of voclosporin against cyclosporine A that separates the two calcineurin inhibitors at the mitochondrial-and-proteostatic-stress level.

**Story one: A synovium-restricted armored P-D-1 C-A-R-T reaches the pathogenic T-cell arm of rheumatoid arthritis that B-cell C-A-R-Ts don't touch.**

Gur, Ravkaie, Sharet-Eshed, and colleagues with senior author Ido Amit at the Weizmann Institute apply single-cell multi-omics to human R-A synovium and identify P-D-C-D-1 — the gene for P-D-1 — as a selective marker of the pathogenic disease-associated T-cell state. Anti-C-D-19 C-A-R-Ts have shown striking clinical activity in some autoimmune diseases, but they miss the pathogenic T-cell arm that biology says matters most in R-A. The group builds a P-D-1-directed C-A-R that eliminates these cells in vitro and in vivo, with marked attenuation of synovitis in R-A models. Two engineering choices carry the safety story. First, C-A-R activity is gated by an N-R-4-A-2-driven biosensor that switches the cells on only inside inflamed synovium — a tissue-restriction circuit rather than a target-restriction circuit, which is the right frame because P-D-1 is also expressed on healthy antigen-experienced T cells throughout the body. Second, the cells are armored to secrete soluble T-N-F receptor two locally, absorbing the T-N-F-alpha driving baseline synovial inflammation and dampening the interferon response that C-A-R engagement itself triggers, pushing the tissue myeloid compartment toward a reparative state. This is the plausible T-cell C-A-R-T complement to B-cell-directed autoimmune C-A-R-Ts, and the biosensor-gated tissue restriction is a genuinely different concept from just picking a synovium-specific antigen.

**Story two: Cryo-E-M structures of the human sodium-citrate cotransporter show that sodium and substrate bind simultaneously, not sequentially.**

Sauer, Song, and colleagues with Da-Neng Wang at N-Y-U School of Medicine determine the human NaCT — the S-L-C-13-A-5 sodium-citrate cotransporter — in three states by single-particle cryo-E-M: sodium-free, sodium-bound, and sodium-plus-substrate-bound. NaCT imports tricarboxylate and dicarboxylate T-C-A-cycle intermediates into cells driven by the inward sodium gradient, and it is a genetically validated target — loss-of-function mutations cause an autosomal-recessive epileptic encephalopathy, and pharmacologic inhibition has been pursued for metabolic disease and aging. The mechanistic result that matters is that in human NaCT, sodium and substrate arrive together — a coupling distinct from the sequential-binding, conformational-selection mechanism established for the bacterial D-A-S-S homolog Vc-I-N-D-Y. For a drug-discovery audience that is not a footnote. Orthosteric inhibitor design has to match the actual binding order, and the human-versus-bacterial mechanistic split says the pharmacophore inherited from Vc-I-N-D-Y crystal structures does not necessarily transfer. Three cryo-E-M states of the human protein with and without cargo is what a serious NaCT medicinal-chemistry campaign has been waiting for.

**Story three: Current AI protein structure predictors default to one dominant P-D-B state — and small molecules barely move them.**

Ye, Wang, and colleagues in the James Gumbart lab at Georgia Tech with Jerry Parks at Oak Ridge run a careful head-to-head of AlphaFold-3, Boltz-2, Chai-1, and BioEmu on four textbook multi-state proteins — the transporter Pf-MATE, the lysine-arginine-ornithine binding protein L-A-O, the S-e-c-A translocation A-T-Pase, and the beta-2 adrenergic receptor — and score state-bias and sampling breadth against experimental references. Two findings hit hard. First, all four models collapse toward whichever conformer is best-represented in the P-D-B. Second, small-molecule ligands have weak and inconsistent effects on which state gets predicted, while a large protein binding partner does flip the answer. And the M-S-A-clustering workarounds — AF-Cluster and random subsampling — inherit the same bias, so this isn't a fix that is one architecture away. For a Scripps audience running AI-guided drug discovery, this is a crisp negative result: the current models are still not the right primary tool for choosing which conformational state to dock into, and the field cannot pretend a ligand modulates conformer selection when the models don't behave that way.

**Story four: A perfused proximal-tubule organ-on-chip separates cyclosporine and voclosporin at the mechanism level — mitochondria, proteostasis, and ferroptosis priming.**

Aryeh, Tsang, and Kelly with Himmelfarb at the University of Washington run cyclosporine A against voclosporin — the calcineurin inhibitor F-D-A-approved for lupus nephritis — in both 2-D human proximal-tubule epithelial monolayers and a perfused 3-D kidney microphysiological system. The 2-D readout is silent: neither drug kills the cells outright. The perfused 3-D chip is where they separate. Confocal tomography shows cyclosporine fragments mitochondria while voclosporin preserves reticular architecture; T-M-R-M flow cytometry confirms voclosporin preserves mitochondrial membrane potential relative to cyclosporine. R-N-A sequencing of the 3-D-cultured cells finds cyclosporine enriches for unfolded-protein response and E-R stress, p-21-driven G-2/M checkpoint arrest, and — the striking piece — a transcriptional signature consistent with ferroptosis priming. Voclosporin instead induces adaptive E-R chaperone and E-R-associated degradation programs without tripping the canonical U-P-R sensors, and does not suppress the cell cycle. Two things to take home: an M-P-S with mechanistic readouts catches sublethal tubular injury that 2-D culture and even a K-I-M-1 biomarker miss, and calcineurin inhibitors are not interchangeable at the mitochondrial-and-proteostatic-stress layer.

That's the briefing for July thirteenth. Talk to you tomorrow.

---

## Show notes

Paper 1 — Gur, Ravkaie, Sharet-Eshed, Shalita, Avellino, Rauchbach, Xie, David, Yagel, Zada, Ben Yehuda, Mazuz, Von Locquenghien, Peleg, Naparstek, Atlan, Kfir-Erenfeld, Kuznetsov, Tzemach, Lidar, Balbir-Gurman, Phan, Freitag, Amit: Synovium-Restricted Armored PD-1-Targeted CAR-T Cells Reprogram Immunity and Resolve Experimental Arthritis
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.09.737520v1

Paper 2 — Sauer, Song, Marden, Wang, Sowerby, Sudar, Rice, Wang: Structures of the human sodium-citrate cotransporter NaCT with and without substrates
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.08.737274v1

Paper 3 — Ye, Wang, Brogi, Parks, Kuo, Gumbart: Benchmarking AI Protein Structure Predictors Reveals a Persistent Bias in Multi-State Proteins
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.10.737860v1

Paper 4 — Aryeh, Tsang, Hsu, Yeung, MacDonald, Bammler, Himmelfarb, Rehaume, Kelly: Voclosporin Preserves Mitochondrial Function Compared With Cyclosporine A in Perfused Human Proximal Tubule Microphysiological Systems
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.07.737071v1

---

## Candidate funnel

bioRxiv preprints posted 2026-07-11 to 2026-07-13 scanned by category. Full-text checks used scripts/fetch_preprint.py (r.jina.ai proxy on .full HTML) — all four picks returned abstract-only pages (bioRxiv body-rendering lag on v1s posted <36h ago).

- bioengineering: 1 scanned (biodegradable intra-arterial device, not Scripps-flavored)
- pharmacology and toxicology: 3 scanned, 1 substantive (Kelly voclosporin vs CsA MPS ✓)
- biochemistry: 4 scanned, 1 substantive (Bhattacharya/DeGrado/Beratan/Liu de novo enzyme optimization — v2 update of a May 2026 v1, dropped as not a fresh v1)
- synthetic biology: 1 scanned (Cupriavidus necator protein production, not Scripps-flavored)
- cancer biology: 1 scanned (HLA-E/NKG2A bladder cancer v3, not fresh)
- cell biology: 4 scanned (MT5-MMP AD v3, Zasp52 muscle v2, MASLD hepatic v3, senescence SASP v3 — no fresh v1 with Scripps hook)
- immunology: 10 scanned, 3 substantive (Amit synovium PD-1 CAR-T ✓; Reshef donor TCR R50 metric for aGVHD; Wang/Xie confined-T-cell PD-1 already featured 2026-07-10)
- molecular biology: 0 scanned
- biophysics: 9 scanned, 2 substantive (NaCT NYU structure ✓; Gumbart AI structure predictor multi-state benchmark ✓)
- genetics: 5 scanned (TOP2 hypercleavage, G4 helicase network, vEDS zebrafish, drosophila reporter, myeloid Pck1 — no Scripps hook)
- microbiology: 10 scanned, none Scripps-flavored (plant/soil/veterinary/environmental)

Substantive shortlist after discarding spurious matches (title — full text vs abstract-only):
- Amit synovium-restricted armored PD-1-CAR-T for RA — Gur, Amit (abstract only, complete) ✓ CHOSEN
- NaCT cryo-EM three-state structures — Sauer, Wang (abstract only, complete) ✓ CHOSEN
- AI protein structure predictor multi-state bias benchmark — Ye, Gumbart, Parks (abstract only, complete) ✓ CHOSEN
- Voclosporin vs cyclosporine A in perfused proximal-tubule MPS — Aryeh, Kelly, Himmelfarb (abstract only, complete) ✓ CHOSEN
- Reshef donor TCR structural signature R50 metric predicts aGVHD — Wang, Reshef (abstract only)
- DeGrado/Beratan/Liu de novo enzyme optimization — Bhattacharya (v2 of May 2026 v1; not a fresh v1)

No source-side failures on today's run; four picks all landed on bioRxiv v1 posted 2026-07-11 to 2026-07-12. Abstract-only status reflects the usual v1 rendering delay, not an outage.
