## Script

Good morning. Today's Scripps Biomedical Brief covers four bioRxiv preprints from the past 48 hours: a nanopore sequencing platform that reads heparan sulfate at the single-chain level for the first time, a droplet single-cell CRISPR screen that pairs cytotoxic T cells with their cancer targets and finds a counterintuitive mTORC1 brake on rapid killing, a reprogrammed tracrRNA system that turns Cas9 into a programmable A-to-I RNA editor and trans-splicing machine, and a cryo-EM mechanism for a bacterial antiviral reverse transcriptase that writes tandem-repeat DNA from a single noncoding RNA template.

**Story one: A sequencing-style readout for the heparan sulfate chains that decorate every cell surface.**

Heparan sulfate is among the most consequential biopolymers in extracellular biology — it sequesters and presents growth factors, organizes FGFR and Wnt signaling, gates host-pathogen entry, and shapes coagulation — but it cannot be sequenced. Existing methods cleave the chain to fragments and read aggregate composition. A team led by Ryan Flynn at Boston Children's, with Jeffrey Esko at UC San Diego, Jian Liu, and Miten Jain, now introduce HS-nano-seq, a nanopore platform that resolves intact heparan sulfate chains at single-molecule resolution. The conceptual insight is to treat heparan sulfate as biochemically analogous to a nucleic acid — using rapid nucleic-acid purification and conjugation chemistry to attach DNA adapters and form heparan sulfate to DNA chimeras, then reading individual chains through a pore. Ionic-current fingerprints encode sulfation patterns; synthetic standards classify by length and sulfation, and cell-derived chains reveal heterogeneity in binding motifs that bulk methods cannot see. The broader claim, and the one with the most leverage for drug discovery, is that the same framework extends to other extracellular matrix glycopolymers — bringing a class of molecules that has resisted systematic interrogation onto the same sequencing workflow as nucleic acids.

**Story two: Pairing each T cell with its target reveals that an mTORC1 brake actually accelerates killing.**

Pooled CRISPR screens cannot resolve what happens during the brief cell-cell encounter that decides whether a target dies. Roger Geiger's group in Bellinzona, with Andrew deMello and Stavros Stavrakis at ETH Zurich, built a droplet single-cell CRISPR screen that co-encapsulates a single primary human CD8 T cell with a single cancer cell, measures rapid target-cell death, and recovers the sgRNA from droplets sorted by phenotype. The screen recovered the expected nodes — T cell receptor signaling, synapse formation, granule exocytosis, PTEN, RASA2, FOXO1 — and validated hits across both bispecific engager and TCR-engineered settings. The unexpected finding is that knocking out RPTOR or RHEB — components that should support T cell function through mTORC1-driven anabolism — actually enhanced cytotoxic execution: mTORC1 output dropped, AKT phosphorylation rose, and anabolic programs attenuated. Transient pharmacologic mTORC1 inhibition reproduced this rapid-killing state and improved antitumor activity after adoptive transfer. The therapeutic implication is concrete: a brief mTORC1 inhibitor pulse around the point of CAR-T or TCR-T infusion may shift transferred cells from growth toward execution.

**Story three: Reprogramming the tracrRNA turns Cas9 into a programmable RNA editor and trans-splicing machine.**

RNA editing platforms have largely standardized on Cas13. Adini Arifah, Constantinos Patinios, Rachael Larose, and Chase Beisel now show that Cas9 — when its tracrRNA is reprogrammed to hybridize a cellular RNA, recruiting Cas9 to the RNA-RNA duplex — can be repurposed for both A-to-I RNA editing and trans-splicing. Fusing the ADAR2 deaminase domain to a catalytically dead SpyCas9 and systematically engineering the reprogrammed tracrRNA, which the authors call Rptr, achieved efficient and tunable A-to-I editing with on- and off-target profiles comparable to dCas13. The platform extended to the compact Cje Cas9 after HNH deletion and PAM-interacting domain mutations, and Rptrs that block splicing enabled both 3-prime and 5-prime trans-splicing. The significance is twofold: a second, mechanistically independent RNA-editing chassis built on the most heavily engineered nuclease in biotechnology, and a direct, programmable handle on alternative splicing — which dominates therapeutic axes in neurodegeneration, muscular dystrophy, and cancer.

**Story four: Cryo-EM solves how a bacterial antiviral reverse transcriptase writes tandem-repeat DNA from a single template.**

Sam Sternberg's lab at Columbia, with Israel Fernandez, previously showed that DRT10 — a bacterial defense-associated reverse transcriptase, noncoding RNA, and SLATT effector trio — catalyzes protein-primed, tandem-repeat DNA synthesis in a mechanism strikingly analogous to eukaryotic telomerase. The structural basis was unknown. Cryo-EM of two evolutionarily diverse DRT10 systems now reveals an unanticipated two-to-one architecture: two reverse-transcriptase monomers bind opposite sides of a single pseudo-symmetric noncoding RNA, each templated from its own face, but only one generates the long repetitive product, with repeat length defined by the distance between two flanking stem-loop anchors. Combined with prior work on DRT2, DRT3, and DRT9, the result identifies a conserved mechanistic logic for noncoding-RNA-templated tandem-repeat synthesis across the Class 2 UG antiviral systems. The horizon application is a programmable in-cell DNA writer with a tunable repeat length — potentially a complement to prime editing for inserting repeat-rich sequences that current platforms struggle with.

That's your briefing for June thirtieth. We'll be back tomorrow.

---

**Show notes**

Paper 1 — Hristov, Daneshvar Kakhaki, Tzadikario et al., Flynn lab with Esko (UCSD), Liu, Jain: Intact and single-molecule analysis of heparan sulfate
Paper link: https://www.biorxiv.org/content/10.64898/2026.06.26.734651v1

Paper 2 — Saronio, Antonini, Jain et al., Geiger lab with deMello, Stavrakis (ETH): Droplet single-cell CRISPR screens identify regulators of T cell-mediated target-cell killing
Paper link: https://www.biorxiv.org/content/10.64898/2026.06.23.734054v1

Paper 3 — Arifah, Patinios, Larose, Beisel: RNA editing and trans-splicing with reprogrammed tracrRNAs
Paper link: https://www.biorxiv.org/content/10.64898/2026.06.28.735058v1

Paper 4 — Ramirez, He, Wiegand et al., Sternberg lab with Fernandez (Columbia): Mechanism of tandem-repeat DNA synthesis by an antiviral reverse transcriptase
Paper link: https://www.biorxiv.org/content/10.64898/2026.06.29.735271v1
