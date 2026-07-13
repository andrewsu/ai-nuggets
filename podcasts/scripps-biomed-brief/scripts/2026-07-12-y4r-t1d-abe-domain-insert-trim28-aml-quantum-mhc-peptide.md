## Script

Welcome back to Scripps Biomedical Brief for Sunday, July 12th. Four preprints from the last 24 to 48 hours — a new G-protein-coupled receptor target for type-one diabetes that protects beta-cells and calms islet-directed immunity from a single molecule, a base-editor engineering trick that narrows the editing window by stuffing a fluorescent protein inside the deaminase, a chem-biology package that nominates a chromatin adaptor as a differentiation-therapy target in acute myeloid leukemia, and the first end-to-end hybrid quantum-classical generative pipeline for M-H-C-binding peptide design with in vitro validation.

**Story one: Y-four receptor agonism protects beta-cells and calms islet-directed immunity from a single molecule — a G-P-C-R target for type-one diabetes.**

Haq, Toczyska, and colleagues with senior authors Persaud and Bewick at King's College London and Beck-Sickinger at Leipzig report a new candidate target for disease-modifying therapy in type-one diabetes. The current best-in-class approaches — teplizumab, and increasingly the J-A-K-1/2 inhibitor baricitinib — buy time by dampening the immune attack; the field has long wanted a complementary strategy that also makes beta-cells themselves harder to kill. RNAscope, cell sorting, and a TAMRA-labeled ligand identify Y-four, one of four neuropeptide-Y receptor subtypes, as selectively enriched at the beta-cell surface in both mouse and human islets. K-twenty-two, a long-acting selective Y-four agonist, has no effect on baseline insulin secretion or systemic glucose tolerance — the receptor is silent under healthy conditions. Under cytokine, streptozotocin, and lipotoxic insult, K-twenty-two reduces caspase activation, sustains insulin release, and turns on a coordinated resilience program: K-E-A-P-1-N-R-F-2 antioxidative activation, suppression of the E-I-F-2 ER-stress arm, and dampening of C-X-C-L-10, C-C-L-3, C-C-L-4, C-C-L-7, and I-L-6 in the local islet environment, while preserving I-L-2 and Foxp-3 signals. Migration of activated human P-B-M-Cs toward stressed human islets is blocked. In the stringent N-Y eight-point-three C-D-8 T-cell adoptive-transfer model of autoimmune diabetes, systemic K-twenty-two significantly delays disease onset. It's a G-P-C-R target that pairs intrinsic beta-cell cytoprotection with local immunomodulation, and it argues the right complement to teplizumab may not be another immunosuppressant.

**Story two: Insert a bulky, well-folded protein inside an adenine base editor and you narrow the editing window, shut down Cas-independent off-targets, and get a fluorescent editor for free.**

Müller, Southern, and Niopek at Heidelberg address a persistent problem with the high-activity TadA eight-E adenine base editor: its editing window is broad, so nearby bystander adenines get accidentally converted. The prevailing fix — weakening the deaminase with point mutations — trades on-target activity for precision. This group instead asks whether physically constraining the deaminase's spatial reach, by inserting a bulky protein domain inside TadA, can preserve on-target catalysis while sterically blocking access to bystander adenines in the exposed single-stranded D-N-A. Using ProDomino computational prediction plus structure-guided site selection, they find that TadA eight-E tolerates internal domain insertions at multiple surface sites; the position at leucine-sixty-eight is standout, accepting L-O-V-2, a P-D-Z domain, or superfolder-G-F-P with high retained activity. And critically, the identity of the insert barely matters — narrowing is driven by position, not domain. The lead superfolder-G-F-P variant preserves near-wild-type editing at the central target adenine across five loci, collapses the effective editing window from positions two-through-twelve down to four-through-eight, and in an orthogonal R-loop assay nearly eliminates Cas-independent off-target deamination in trans. Because superfolder-G-F-P folds correctly inside the deaminase, you also get a fluorescent, trackable editor for free. Internal domain-insertion is a modular knob for precision plus orthogonal function, cleanly separable from deaminase-mutation approaches — and immediately transferable to other CRISPR effectors.

**Story three: T-R-I-M-28 is a chromatin-adaptor dependency in acute myeloid leukemia, and a small-molecule bromodomain probe phenocopies its knockdown — differentiation therapy with a molecule attached.**

Amos, Chen, and colleagues in the Soto-Feliciano lab at M-I-T with Scott Lowe at Memorial Sloan Kettering and Angela Koehler at the Broad Ludwig Center run a focused CRISPR screen in acute leukemia and land on T-R-I-M-28, a multi-domain chromatin adaptor previously known primarily as a K-R-A-B-zinc-finger co-repressor. Depletion impairs leukemia proliferation in vitro and in vivo and — more strikingly — activates neutrophil differentiation programs, driving leukemia cells toward mature, functionally neutrophil-like states with reduced leukemic potential. Chromatin and transcriptomic profiling place T-R-I-M-28 as a co-repressor of neutrophil-associated loci independently of H-3-K-9 methylation, a departure from its canonical mechanism. The chem-biology payoff, and the reason this preprint is a Scripps-relevant read, is that the group developed a selective small molecule that binds the P-H-D-bromodomain of T-R-I-M-28, phenocopies the genetic knockdown across biochemical and cellular assays, has low-micromolar anti-leukemia activity, induces neutrophil differentiation, and synergizes with menin inhibitors already in the clinic. Target discovery, mechanism of action, and a first-generation chemical probe in one preprint — a differentiation-therapy hypothesis with a molecule attached, filed on a U-S patent application, and immediately opinionable.

**Story four: The first end-to-end hybrid quantum-classical generative pipeline for de novo M-H-C-class-one peptide design, with wet-lab validation.**

Engdal and colleagues from HERVolution Therapeutics with ORCA Computing, Sparrow Quantum, and the Hadrup lab at the Technical University of Denmark couple a generative adversarial network to latent-space priors sampled from a real photonic quantum processor. The idea is that the default factorized-Gaussian prior in classical generative models under-explores sequence space, and structured non-classical distributions from quantum hardware can serve as a different inductive bias — one that helps most where classical training data is thinnest. Across one-hundred-thirty-one H-L-A class-one alleles evaluated in silico, quantum-derived priors increased the yield of predicted strong binders, with the largest relative gains on understudied alleles where classical baselines perform worst — exactly the regime that matters most for personalized immunotherapy and vaccine design in patients whose H-L-A types are under-served by existing training data. On three of those understudied alleles, the team took computational designs into peptide-M-H-C stability ELISAs and confirmed that quantum-designed peptides are potent stabilisers of the class-one complex. This is the first wet-lab validation of quantum-primed generative design on a therapeutic-adjacent task, and the effect concentrates precisely where new inductive biases should matter — the small-data corner where deep generative models tend to memorize rather than explore.

That's the briefing for July 12th. Talk to you tomorrow.

---

## Show notes

Paper 1 — Haq, Toczyska, Islam, Olaniru, Lei, Hu, Zhao, Müller, Mirza, Fine, Hodson, Persaud, Beck-Sickinger, Pearson, Bewick: Neuropeptide Y4 receptor activation delays autoimmune diabetes by reprogramming β-cell stress and immune tolerance
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.03.736290v1

Paper 2 — Müller, Southern, Niopek: Domain Insertion Improves the Precision of a CRISPR Adenine Base Editor
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.03.736350v1

Paper 3 — Amos, Chen, Xiang, Motoyama, Gonzalez-Robles, Narendra, Johnson, Lee, Ho, Celikoyar, Ye, Guo, Glickman, O'Hearn, Sarkar, Arroyo-Ortega, Devine, Pagano, Ruggles, Sanchez-Rivera, Koehler, Lowe, Soto-Feliciano: Epigenetic Reactivation of Lineage Differentiation to Target Leukemia
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.08.737260v1

Paper 4 — Engdal, Funk, Bacarreza, Machado, Johansen, Kemming, Farnsworth, Brasas, Lefevre-Morand, Slysz, Noerregaard, Sandberg, Makarovskiy, Lodahl, Acevedo-Rocha, Kurowski, Hadrup, Clements, Jenkins: Hybrid quantum-classical de novo design of MHC-binding peptides
Paper link: https://www.biorxiv.org/content/10.64898/2026.07.09.736951v1

---

## Candidate funnel

bioRxiv preprints posted 2026-07-10 to 2026-07-12 scanned by category. Full-text checks used scripts/fetch_preprint.py (r.jina.ai proxy on .full HTML).

- bioengineering: 10 scanned, 3 substantive (heparin-mimic disulPAS anticoagulant; GCE-vascularized brain organoids; foldase-condensate chemical boost)
- pharmacology and toxicology: 2 scanned, 1 substantive (voclosporin vs cyclosporine in perfused proximal tubule MPS)
- biochemistry: 14 scanned, 3 substantive (hybrid quantum-classical MHC peptides ✓; Mann spatial proteogenomics; Neel Shah PTP1B substrate photo-crosslinking)
- synthetic biology: 13 scanned, 2 substantive (Niopek ABE domain-insertion ✓; Bertozzi GELYTAC already featured 2026-07-11)
- cancer biology: 30 scanned, 3 substantive (Soto-Feliciano TRIM28 chem-biology probe ✓; Marshall/Cheung UNSW-SC-22 MYC/MYCN degrader; Garcia-Alonso/Barbacid RAF1 scaffold degradation)
- immunology: 15 scanned, 1 substantive (Persaud Y4R T1D ✓ — categorized cell biology; noted here for completeness)
- cell biology: 30 scanned, 3 substantive (Persaud Y4R T1D ✓; Xavier α-syn optical screen harman; Lafontaine mechanosensitive nucleolus)
- biophysics: 17 scanned, 1 substantive (Biswas/Ruiz EV-D68 3D-pol already featured 2026-07-11)

Substantive shortlist after discarding spurious matches (title — full text or abstract-only):
- Y4R T1D — Haq, Persaud, Beck-Sickinger, Bewick (full text) ✓ CHOSEN
- Domain-insertion ABE precision — Müller, Southern, Niopek (full text) ✓ CHOSEN
- TRIM28 chromatin adaptor AML differentiation therapy — Amos, Soto-Feliciano, Lowe, Koehler (abstract only, complete) ✓ CHOSEN
- Hybrid quantum-classical MHC peptide GAN — Engdal, ORCA/Sparrow, Hadrup (abstract only, complete) ✓ CHOSEN
- Foldase condensate chemical boost (pMePySH thiol) — Watabe, Buchner, Okumura (abstract only)
- α-syn optical screen surfaces harman β-carboline — Rothschild, Xavier (full text)
- Neel Shah PTP1B substrate photo-crosslinking (v2) — Johns, Shah (full text via v2 rerender)
- Marshall/Cheung UNSW-SC-22 MYC/MYCN medulloblastoma degrader (abstract only; SE486-11 analog rather than wholly new chemotype)
- Grinstaff/Chaikof regio-selective disulPAS heparin-mimic anticoagulant (abstract only)
- Voclosporin vs cyclosporine A perfused proximal-tubule MPS (Aryeh, Kelly) (abstract only)
- Mann cell-type-resolved spatial proteogenomics (abstract only)

No source-side failures on today's run; bioRxiv abstract-only status for several July-10 v1 posts is the usual rendering delay, not an outage.
