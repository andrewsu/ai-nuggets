# 2026-05-13 — ClaroAI-Bench: a benchmark for AI agents reproducing real NIH-funded biomedical papers — and Claude Code clears sixty percent

Paper link: https://www.biorxiv.org/content/10.1101/2026.05.08.723611v1

## Script

Welcome back. Wednesday, May thirteenth, twenty-twenty-six. Today's nugget is a bioRxiv drop that does something I have been waiting for somebody to do for about two years — take agentic AI and point it at the reproducibility crisis as a measured, scored task, on real biomedical papers, end to end.

The paper is "ClaroAI Bench — Evaluating Agentic Scientific Reproducibility on Real Biomedical Papers." Posted to bioRxiv yesterday. Single author, Kyle O'Connell at Deloitte Consulting, which is an unusual address for a benchmark paper in our space. Worth keeping in mind as a caveat, but the design is serious and the result is sharp enough to talk about.

Here is the setup. The benchmark is thirty-five real NIH-funded biomedical papers, picked to span five modalities — genomics, imaging, clinical and electronic health record work, epidemiology, and wet-lab. For each paper, the task is to start from the publication and reproduce the computational results. Find the data, get it, find the code, get it, rebuild the environment, run the analysis, compare the numbers to what the paper claimed.

That full pipeline is scored on a five-dimension rubric. First, can the agent find where the data lives. Second, can it actually access the data. Third, can it find the code. Fourth, can it reconstruct the computational environment — the right Python, the right packages, the right versions, the things that break most reproducibility attempts in real life. And fifth — this is the one that matters — can it actually reproduce the numerical result.

Now the ablation that makes the paper.

The author runs three conditions. An audit-only baseline that scores the first four dimensions from metadata alone and never tries to run anything. A bash-only agent that can call the model and execute shell commands but has nothing else. And a full-capability agent — Claude Code, with the full tool suite, file editing, web fetch, the works.

Audit-only — zero percent reproduction. Predictable, since it never runs the code. Bash-only — also zero percent. That one is more interesting. Just giving the model an API and a shell is not enough. The environment reconstruction, the dependency hunts, the file edits, the iterative debugging — those need a richer surface.

Claude Code with all the tools — twenty out of thirty-three computational papers reproduced. Sixty-point-six percent.

Stop and sit with that number for a second. A general-purpose agentic coding assistant, given no biomedical-specific training and no per-paper hand-holding, walks into thirty-three NIH-funded biomedical papers and gets the published numerical results back on three out of five of them. The papers it fails on are not in some hand-curated easy set — they are real published work with real reproducibility friction. And the comparison point is not "another agent." It is "zero." Audit baselines are zero. Bash-only is zero. The delta is entirely in the tool surface.

There are two downstream findings worth pulling out, because they are the kind of quantitative anchors open-science advocates have been wanting.

First, the four upstream metadata dimensions strongly predict the fifth. Spearman correlation of zero-point-six-eight between the metadata score and whether the agent actually reproduces. So the unglamorous infrastructure — clean data links, public code, version-pinned environments — is not just nice to have. It is what predicts whether an AI agent can pick up your paper and run it.

Second, papers with accessible data and code achieve close to three times the reproduction score of papers with restricted access. That is the quantitative version of an argument open-data folks have been making forever, and now it is measured against an autonomous agent's performance instead of against vibes.

There is also an interesting evaluator-disagreement signal. The author scored each run with three frontier judge models — Claude Opus, the latest GPT, Gemini — and looked at where they agreed. They agree closely on code availability, but disagree much more on environment reconstructability. So even with strong judge models, "did the environment really get rebuilt correctly" is the dimension that needs more careful evaluation design. Useful to know if you are building your own agentic-science benchmarks.

Three caveats before I let you go.

One — single author at a consulting firm, version one preprint, thirty-five papers. The result is striking but the sample is small and the work has not been independently replicated.

Two — the full-capability arm is specifically Claude Code with all tools. We do not yet know how much of the sixty percent is the model, how much is the tooling, and how much is the long-horizon scaffolding inside Claude Code. A clean comparison against a comparably-equipped Gemini agent or an Open Devin–style setup would change how we read the headline.

Three — the bash-only baseline scoring zero is, honestly, a soft straw man. A team building a serious bash-plus-model agent would not stop where this baseline did. The right read of the ablation is "tools matter a lot," not "any non-Claude-Code agent is at zero."

But none of those caveats kill the contribution. This is the first benchmark I have seen that scores agentic reproducibility end to end on real biomedical literature, ties it to upstream open-science practices with a measurable correlation, and gives us an early empirical anchor — sixty percent — for what a frontier agentic coding system can do today. If you care about agentic biomedical AI, this is the kind of evaluation the field is going to be quoting against for at least the next year.

That is it for today. Back tomorrow.
