# 2026-05-10 — BioMedArena: the per-paper engineering tax and a one-harness arena for biomedical agents

Paper link: https://arxiv.org/abs/2605.06177

## Script

Welcome back. Sunday, May tenth, twenty-twenty-six. Today's nugget is a piece of infrastructure rather than a result, and it lands at exactly the moment this feed has been circling around the same problem from three different angles.

The paper is "BioMedArena: An Open-source Toolkit for Building and Evaluating Biomedical Deep Research Agents." Posted to arXiv on Thursday, May seventh. The corresponding author is David Clifton at Oxford, and the first author is Jinge Wu, with a long author list that includes the Honghan Wu and Fenglin Liu group — these are the people behind several of the biomedical-LLM benchmarking efforts of the past two years, so this is a continuation of a research line they own, not a one-off.

The framing the paper opens with is the most useful part. They call it the per-paper engineering tax. The pitch is this. The same backbone, evaluated on the same benchmark, reports different accuracies in different papers — because the harness differs, the tool registry differs, the context management differs, the scoring differs. And to integrate a new foundation model into a comparable evaluation surface costs weeks of model-specific glue code. So every time a new biomedical agent paper goes up, the field re-pays this tax. The BixBench follow-up two weeks ago illustrated the symptom — seventeen percent in one paper, ninety-eight percent in a rebuttal preprint posted nine months later — and a lot of that gap was harness, not capability. The Open-Rosalind paper yesterday made the same point from the other side, when the in-house eighty-one percent collapsed to eighteen percent on a hold-out the harness wasn't tuned for.

BioMedArena's answer is to decouple six layers and make each one a registerable provider. Benchmark loading is layer one. Tool exposure is layer two — what tools are even visible to the agent. Tool selection is layer three — how the agent picks. Execution mode is layer four — single-turn, multi-turn, with or without re-planning. Context management is layer five — how the trace is summarized, evicted, or carried forward. Scoring is layer six. Once those are separated, you can hold five of them fixed and ablate the sixth, which is what's been missing.

The numbers. One hundred and forty-seven biomedical benchmarks loaded. Seventy-five biomedical tools across nine functional families. Six agent harnesses crossed with six context-management strategies, producing twelve backbones with what they call competitive research capabilities. Adding a new model, benchmark, or tool reduces to registering a few-line provider adapter — which is what makes the whole thing land as infrastructure rather than just another evaluation paper. The headline result is state-of-the-art on eight representative biomedical benchmarks with an average lift of fifteen points over prior best. Take that fifteen-point lift with the usual asterisks — the SOTA bar moves quarterly in this space, and a unified harness will incidentally beat per-paper harnesses on the per-paper numbers because the configurations get tuned together. The more durable claim is the harness, not the leaderboard delta.

Three reasons this is worth your attention even if you do not run agent evaluations yourself.

First, the open-source piece. Everything — toolkit, configurations, per-task traces — is on GitHub under AI-in-Health slash BioMedArena. Per-task traces being public is the unusual move. Most agent papers report final accuracies and keep the traces internal, which is exactly the conditions under which the per-paper tax keeps getting paid. If this catches on, the field gets something closer to what HELM did for general LLM evaluation but in a biomedical-tool-aware shape.

Second, the seventy-five tools across nine functional families is the part that should be interesting to anyone working on tool-using biomedical agents — which on this feed is most of us. The taxonomy is a contribution in itself, because right now every paper picks its own tool subset and calls them whatever it wants. A standardized set of seventy-five tools, nine families, with documented adapters, is the kind of plumbing that prevents tool-set choice from becoming a hidden source of capability inflation.

Third, this paper does not actually run a new claim about what frontier models can do biomedically. It runs an arena. So when the next BixBench-style number comes out, the right move is not to argue about the number — it is to ask which of the six layers explains it. That is the reframe.

One caveat. The toolkit is brand new, and what we have today is the paper plus the repo. We do not yet have the field running on it, we do not have third parties re-grading old claims against it, and we do not have the kind of pull requests adding new models and new benchmarks that would prove it actually reduces the engineering tax in practice. That happens over the next six months or it does not. But the framing — six layers, registerable providers, traces public — is sound, and it is the framing the field has been waiting for.

That is it for today. Back tomorrow.
