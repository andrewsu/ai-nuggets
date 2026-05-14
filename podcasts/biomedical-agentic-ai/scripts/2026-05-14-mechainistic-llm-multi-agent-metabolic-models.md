# 2026-05-14 — MechAInistic: an LLM-guided multi-agent system that reasons over genome-scale metabolic models — and finds two repurposing candidates on its first try

Paper link: https://www.biorxiv.org/content/10.64898/2026.05.11.723319v1

## Script

Welcome back. Thursday, May fourteenth, twenty-twenty-six. Today's nugget hits a target the field has been circling for a while — getting an agentic system to actually drive a mechanistic biology workflow, not just summarize one. From bioRxiv yesterday, out of the Helikar lab at the University of Nebraska Lincoln. Title is "Mech-AI-nistic — an L-L-M-guided multi-agent system for reasoning over genome-scale constraint-based metabolic models." Yes, the name is "mechanistic" with A-I sitting inside the word. Cute, and also exactly what the system is trying to be.

Here is the setup. Constraint-based metabolic modeling is one of the workhorses of systems biology — you take a stoichiometric model of every reaction in a cell, drop in some bounds, run flux balance analysis or one of its cousins, and you can ask things like "what happens to flux through the T-C-A cycle if I knock out this reaction." It is powerful. It is also notoriously fiddly. You have to know which model to use, which boundary conditions, which solver, how to interpret the output, how to compare two model states without fooling yourself. It is the kind of analysis where a wet-lab biologist with a real biological question often cannot actually get to the answer without a computational collaborator, even though the math is sitting right there.

What this group did is build an agentic layer on top of all of that. The user types a natural-language question. The system turns it into an executable, model-grounded workflow, runs it, and hands back a structured report. And it can do that across the standard menu of tasks — pathway comparison, perturbation analysis, drug-target exploration, literature-grounded interpretation — and it can do all of those across two paired metabolic models, like disease versus healthy.

The architecture is the part that is worth picking out, because it is a clean version of a pattern I think we are going to see more of. They use an architect-reviewer setup. One agent decomposes the question into a workflow plan — which models to load, which analyses to run in what order, which intermediate results to keep. A reviewer agent looks at that plan and the intermediate outputs and pushes back — challenges assumptions, flags missing steps, asks for clarifications. That back-and-forth runs over the actual mechanistic model, with the language model as the planner and critic but the numerical work delegated to real solvers underneath. That separation matters. It is what keeps the L-L-M from hallucinating fluxes.

Now the receipts.

Test case one — rheumatoid arthritis. They took paired metabolic models of naive B cells from R-A patients versus healthy controls. The system quantified the metabolic rewiring between the two, used topological hub filtering and robustness analysis to prioritize candidate reactions, and surfaced an existing drug — Devimistat — as a repurposing candidate. Mechanism — Devimistat hits two-oxoglutarate dehydrogenase, which sits in the T-C-A cycle and is exactly where the differential analysis pointed.

Test case two — multiple sclerosis. Paired metabolic models of C-D-four-positive T-helper-seventeen cells from M-S patients versus controls. Same workflow, no hand-tuning. The system identified N-A-D-P-dependent isocitrate dehydrogenase as the optimal single target and proposed ivosidenib, which is already F-D-A approved for an I-D-H-mutant cancer, as a repurposing candidate.

Two independent autoimmune diseases. Same agentic pipeline. Two reasoned, mechanism-grounded, druggable hypotheses, both involving drugs that already exist. That is what an agentic system is actually for — not chatting about biology, but coordinating the multi-step analyses a human modeler would do, doing them faithfully, and surfacing the kind of hypothesis that costs a real expert a week.

A few things I want to flag.

One — the integration point is the important contribution, more than the model architecture itself. Architect-reviewer is not new as a pattern. What is new is wiring it cleanly into constraint-based modeling — so the L-L-M plans and critiques but the actual flux math stays in deterministic solvers. That is the right division of labor and it should generalize beyond metabolism. Imagine the same skeleton over signaling network models, over agent-based tissue models, over pharmacokinetic-pharmacodynamic models. The lab clearly knows that — they have been building the Cell Collective and related platforms in this space for years.

Two — the two repurposing hits are not validated. Devimistat famously failed its big phase three pancreatic cancer trial a few years back, but it does hit the target the system claims. Ivosidenib's I-D-H connection is real and approved. Whether these specific compounds work in R-A or M-S is a separate question that needs real experiments. What the paper demonstrates is that the agentic workflow gets you from a fuzzy biological question to a mechanistically defensible, testable proposal, end to end, without a human in the loop pushing each step.

Three — the system is hosted, at mech-AI-nistic-dot-D-T-I-H-dot-org. So this is meant to be used, not just described. That matters. A lot of agentic-biology papers ship as figures-only with no working artifact, which makes the claims hard to stress-test. This one is live, which means somebody outside the authoring lab can throw a hard biological question at it this week.

If you care about agentic biomedical AI, the takeaway is that the field is finally moving past "L-L-M reads the abstract" and into "L-L-M orchestrates the actual mechanistic analysis." This is one of the cleaner instances of that shift I have seen this month.

That is it for today. Back tomorrow.
