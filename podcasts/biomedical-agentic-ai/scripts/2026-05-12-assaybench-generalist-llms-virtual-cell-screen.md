# 2026-05-12 — AssayBench: generalist LLMs beat biology-specialist LLMs on a virtual-cell phenotypic-screen benchmark

Paper link: https://arxiv.org/abs/2605.10876

## Script

Welcome back. Tuesday, May twelfth, twenty-twenty-six. Today's nugget is an arXiv drop from yesterday that lands a benchmark, a counterintuitive headline finding, and a small reframe of the virtual-cell pitch — all in one paper.

The paper is "AssayBench: An Assay-Level Virtual Cell Benchmark for LLMs and Agents." Posted to arXiv on Monday, May eleventh. It is a Genentech-led collaboration with academic and industry co-authors, and the shape of the author list signals this is meant to be the benchmark the field anchors on for this task, not a one-shot eval.

Here is the setup. The virtual-cell idea, which has been gathering momentum for the last two years, is to build a computational model of cellular behavior good enough that you can do phenotypic screens in silico. Predict what happens when you knock out a gene, when you add a compound, when you stress the cell — without actually doing the experiment. The bull case for biomedical AI rests partly on this. If we can do it well, drug discovery accelerates by a couple of orders of magnitude.

But here is the framing problem the AssayBench authors zero in on. Existing virtual-cell benchmarks evaluate models on narrow molecular readouts — gene-expression changes, protein abundance, the kind of thing you can predict from a perturbation embedding. Those readouts are only loosely connected to the endpoint that actually drives drug-discovery decisions, which is phenotype. Does the cell live, die, change shape, change state, secrete something. A model that nails gene expression but cannot rank perturbations by phenotypic impact is not the virtual cell the bull case needs. The endpoint matters.

So AssayBench is a phenotypic-screen prediction benchmark. The authors assemble around two thousand — nineteen hundred and twenty, to be exact — publicly available CRISPR screens that span five broad classes of cellular phenotypes. For each screen, the model has to predict a ranked list of genes — which knockouts will move the readout the most. They evaluate with a continuous adjusted ranking metric that handles the heterogeneity across assays. That last piece is the methodological move that matters, because comparing ranking quality across screens with different signal-to-noise and different list lengths is exactly the kind of thing that has tripped up prior efforts.

Now the headline result, which is the part I want you to remember.

Zero-shot generalist large language models — frontier models, no biology-specific training — outperform the biology-specific LLMs and the trainable baselines on this benchmark.

Stop and sit with that. The biology-specific LLMs are the models the field has been pouring effort into for two years. Trained on tens of millions of single-cell profiles, on perturbation atlases, on protein-protein interaction graphs, on disease ontologies. They are supposed to be the substrate for virtual cell. And on an assay-level phenotypic-screen rank-prediction task, a generalist model with no biology pretraining at all does better.

This is the third or fourth time this pattern has surfaced this year in a serious biomedical benchmark, and at some point it stops being a fluke. Generalist LLMs win when the task requires reading a perturbation description and a cellular context and reasoning across a broad knowledge base. Biology-specific LLMs are presumably winning somewhere — maybe on tasks closer to their pretraining distribution, maybe on tasks where the inductive bias from biological structure pays off — but those tasks need to be named, and the field has not yet named them cleanly. Until then, the default for new biomedical agentic systems should be a strong generalist backbone, not a specialist.

The other useful piece is that prompt optimization, fine-tuning, and ensembling all measurably improve the generalist model's performance on AssayBench. That is the actionable bit. If you are building an agent that has to rank perturbations or rank hypotheses or rank candidates of any kind for an assay, lean on these post-training techniques rather than reaching for a biology-specific backbone.

Two caveats worth flagging.

First, performance is still far from the empirical ceiling. The authors estimate the best a model could do given the noise in the underlying screens, and the best LLMs are nowhere near that ceiling. There is room for the biology-specific models to come back if someone figures out the right pretraining objective. The pattern today is not a verdict, it is a checkpoint.

Second, gene-rank prediction across a screen is one task in the virtual-cell vision. Not the whole vision. The bull case wants models that can simulate cellular state evolution over time, predict morphological changes, condition on patient context, integrate imaging. Phenotypic-screen rank prediction is a measurable proxy, not the destination. Watch for AssayBench-style benchmarks that move toward dynamic and multimodal endpoints — that is where the real test of the virtual cell lives.

One thing I like about this paper independently of the headline number. The taxonomy of broad cellular phenotype classes plus an adjusted ranking metric that works across heterogeneous assays is the kind of methodological scaffolding the field needs. We have benchmarks for benchmarks-sake all over biomedical AI. This one is built around the unit of analysis a drug-discovery group actually cares about, which is the assay, and that grounding is rare enough to call out.

That is it for today. Back tomorrow.
