# OIH: An Autonomous LLM Agent Platform for Antibody-Drug Conjugate Design

Paper link: https://www.biorxiv.org/content/10.64898/2026.04.21.719907v1

## Summary

A fresh bioRxiv preprint introduces Open Intelligence Hub, an LLM-agnostic agent platform that dynamically plans and runs 32 containerized computational biology tools to design protein binders and prioritize antibody-drug conjugates. Across five oncology targets, the agent classified all five correctly and only needed human intervention for hotspot selection in one case, producing high-quality binders for Nectin-4 and HER2. The novel piece is "failure-to-knowledge distillation" from 265 curated cases plus tier-based decision routing — meaning the agent learns from past pipeline failures rather than just retrying. It is one of the more concrete demonstrations that agentic systems can stitch together structure prediction, binder design, and conjugation-aware ranking without manual handholding.

Paper: https://www.biorxiv.org/content/10.64898/2026.04.21.719907v1

## Script

Welcome to AI Nuggets. Today we're looking at a fresh preprint that landed on bioRxiv this week, and it's a nice concrete example of where agentic AI is actually showing teeth in drug discovery. The paper, from a group at Suzhou Kai Zhi Yuan Technology, introduces the Open Intelligence Hub, or OIH — an autonomous large language model agent platform built specifically for designing protein binders and prioritizing antibody-drug conjugates.

If you've been watching this space, you know the pattern. Everyone keeps demoing LLM agents that do chemistry tool use, but when you try to apply that to a real computational biology workflow — structure prediction, binder design, hotspot selection, then conjugation chemistry on top — it usually falls apart. The pipelines are long, the tools are heterogeneous, and small failures compound. OIH tries to attack that messy middle directly.

Here is what they built. A single LLM-agnostic agent dynamically plans and executes thirty-two containerized tools. So the same orchestrator can drive open weights models or commercial frontier models without changing the pipeline. The agent introduces a few interesting tricks. First, tier-based decision routing — instead of letting the LLM pick any tool at any time, the agent routes through structured tiers based on what stage of the design problem it is in. Second, ipSAE-guided interface filtering — they use the protein-protein interaction confidence signal to prune bad designs early. And third, the part I think is most interesting, what they call failure-to-knowledge distillation. They took two hundred and sixty-five curated cases where the pipeline failed, distilled the failure modes into structured guidance for the agent, and used that to keep it from repeating the same dumb mistakes.

The benchmark is small but real. They ran the agent on five oncology targets — including Nectin-4 and HER2, both clinically important for ADC programs. The agent correctly classified all five evaluated targets. It only needed human correction once, for hotspot selection on a single target. And the binders it produced ranked competitively, with HER2 hitting an ipTM of zero point eight five and Nectin-4 hitting zero point eight seven. Those are respectable AlphaFold-Multimer style scores for de novo binders.

Why does this matter? Two reasons. First, antibody-drug conjugates are one of the hottest modalities in oncology right now, and the design space — picking targets, designing binders, choosing linkers, choosing payloads, predicting conjugation behavior — is exactly the kind of multi-step problem where agents could actually outperform humans, because no single human holds all that expertise at once. Second, the failure-to-knowledge distillation idea is something the broader agent community should pay attention to. Right now most agent benchmarks reward systems that succeed on novel tasks, but the harder engineering problem is preventing the same failure twice across a long pipeline. OIH's curated failure corpus is small, but it points at a useful pattern.

A few honest caveats. All the binder results are still computational predictions — they have not been experimentally validated yet. The benchmark is only five targets. And the LLM-agnostic claim needs to be tested with weaker open models before we know how much of the lift comes from the orchestration versus from a strong frontier model under the hood. But as a snapshot of where agentic computational biology is in April twenty twenty six, this paper is a useful one to read.

A couple more headlines worth knowing about this week. Google launched Deep Research and Deep Research Max, autonomous research agents built on Gemini three point one Pro, with Axiom Bio reporting they unlocked unprecedented depth in biomedical literature review for drug toxicity prediction. CROssBARv2 came out on bioRxiv, a unified biomedical knowledge graph framework with an LLM-driven natural language question answering layer on top — directly relevant to anyone building knowledge graph products. And Pipette, also on bioRxiv this month, encodes over twenty thousand peer-reviewed publications into an executable Skill Graph that constrains a multi-agent bioinformatics workflow to only biologically valid analytical transitions.

That's your nugget for today. Stay curious.
