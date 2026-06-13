# Cell-cycle arrest as a CAR-T exhaustion driver — S-to-G2 stall pinpointed upstream of dysfunction

Paper link: https://www.biorxiv.org/content/10.64898/2026.06.11.731737v1

## Script

Today's pick is a Stanford preprint that posted on bioRxiv yesterday, out of the Bendall and Mackall labs. The title alone should grab anyone working on engineered T cells. "Cell Cycle Sensing Shapes Human T Cell Fate and Exhaustion Programs." For a translational immunologist working on CAR T cells and T cell engagers, the question of why these therapies exhaust is the question. This paper argues that the cell cycle is not just a downstream consequence of exhaustion — it is upstream of it. And the team identifies a specific cell-cycle state, an aberrant S to G2 arrest, as the lever.

The setup is worth grounding. Tonic signaling, where a CAR fires constantly even without antigen, especially with certain scFv designs, is well established as an accelerator of exhaustion. What has been less clear is mechanism. Why does constant low-level signaling tip cells into dysfunction faster than periodic antigen-driven signaling? Prior work has chased transcription factors, epigenetic remodeling, metabolic state. This paper says, look at the cell cycle.

The technical intuition is to measure many things at once on the same cell, then disentangle them. The team uses mass cytometry — CyTOF — to capture cell cycle markers, receptor signaling proteins, T cell differentiation state, and time since activation all in parallel on single cells. With that resolution they can pull apart what would otherwise be tangled — division per se, time since activation, signal strength, and cell-cycle phase. They then perturb the system, pharmacologically blocking specific cell-cycle transitions and using tonic-signaling CAR models of exhaustion.

Two findings come out of this. First, early in activation, G1 to S progression crosstalks with receptor signaling to bias fate. Effector versus memory decisions are made at this checkpoint, not later in differentiation. Second, in tonic-signaling CARs that drive exhaustion, cells accumulate an aberrant S to G2 arrest signature, and that signature sits upstream of the exhaustion program, not downstream of it. Block the cycle in the wrong place and you push cells toward dysfunction.

The part that elevates this beyond an in vitro mechanism paper is the validation. They look for the same S to G2 arrest signature in situ and in vivo across human cancers, and they find it associated with CD8 T cell dysfunction in tumors. So this is not a CAR-engineering artifact. It is a feature of dysfunctional T cells in patient tissue.

The take. If S to G2 arrest is genuinely upstream of exhaustion rather than a passive consequence, then a CAR or T cell engager design that minimizes tonic signaling-driven cell-cycle arrest has a new mechanistic target — scFv tuning, hinge and transmembrane choices, or pharmacological co-treatment that nudges cells through the checkpoint. It also raises the possibility that early cell-cycle biomarkers, read out on the apheresis sample or the post-manufacturing product, could predict downstream exhaustion before it shows up clinically. For a CAR or TCE program, a predictive bench assay at the IND stage is genuinely useful.

One caveat, and I want to be upfront about it. The paper went live on bioRxiv yesterday and the full text was not reachable from where I'm reading, so this read is built from the preprint abstract and the Mackall lab's prior trajectory on tonic-signaling exhaustion. The specific tonic CAR models they used, the rescue experiments demonstrating causality, the cancer datasets they validated against, and the magnitude of effect — those are worth pulling directly from the paper. Especially the rescue piece, because the upstream-versus-downstream claim lives or dies on whether forcing cells through the S to G2 checkpoint rescues exhaustion, or whether blocking it phenocopies tonic signaling. The abstract is suggestive on this point but not definitive.

Paper link is in the show notes.
