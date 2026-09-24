# CellAudit — the agent's best virtual-cell model never looked at the drug

Paper link: https://arxiv.org/abs/2609.27234

## Script

Today's pick went up on arXiv yesterday, a six-group collaboration led out of Sun Yat-sen University with Tencent AI Lab. It's called CellAudit, and it asks a question the AI-virtual-cell field has been conspicuously not asking: when a language-model agent invents a model that predicts how cells respond to a drug, does the model actually use the drug?

There is now a small industry of agentic model-discovery systems — CellScientist, CellForge, HarmonyCell — where an agent writes executable predictor code, trains it, reads a validation score, and proposes a revision. Loop that a few hundred times, keep the best. The feedback signal is, overwhelmingly, one held-out number.

The authors point out the obvious failure mode, and then go and measure it. On a paired morphology-to-transcriptomics perturbation task built from Cell Painting data, the agent's selected model reaches a held-out Pearson correlation of zero point three one five. A baseline that sees only the untreated control profile — no compound at all, ever — reaches zero point three one four. And when you swap in a different compound, the model's predictions change by exactly zero. Not approximately zero. Zero.

Then the good part. They go read the code. The compound-conditioned cross-attention layer that the model's own design document cites has exactly one key and one value. A softmax over a single element is always one, so the query — the thing carrying compound identity — cannot influence the output. It's a real, findable bug, and score-based selection didn't merely fail to catch it. It promoted the model that had it.

The reflex is to call that one broken layer. It isn't. They audit forty-eight generated candidates. Forty-seven of them do change their predictions when you swap the compound, so they pass the naive dependence test. Only twenty show a real improvement in target loss with confidence intervals above zero on both held-out folds. Depending on an input is not the same as that input helping.

What makes this more than a gotcha is the three-part decomposition, which I think is the durable contribution here. Question one: can the input physically reach the computation the code claims it reaches? That's a static check on the source. Question two: do the fitted predictions change when you replace it? That's a behavioral test on a frozen checkpoint. Question three: does that change actually reduce error against the observed response? Three different questions, and a model can pass any subset of them. Compiling an explicit compound route into the architecture buys you dependence but not contribution. What recovers both is forcing the model to be a residual on top of a fixed control-only baseline, so the perturbation branch either earns its keep or contributes nothing.

The result I keep thinking about is the last one. They take designs selected on the LINCS perturbation resource, freeze them, and refit on an independently acquired cohort. The predictive gain survives. The dose contribution survives. The compound-identity contribution does not — thirty-five of fifty designs cleared the compound criterion on the original data, and zero of fifty clear it on the new cohort. Predictive generalization and claim generalization are different properties, and we have been reporting only the first one.

The authors are honest about the weakest part of the paper, and so should I be. When they wire the audit output back into the agent's prompt and race it against score-only feedback, the means move the right way on every measure, but the paired intervals across five trajectories include zero. Five trajectories is five trajectories. The falsification layer is well demonstrated as a diagnostic; that it makes the search better is still a hypothesis.

Why this matters past virtual cells. Every agentic-science system in this space optimizes a scalar, and a scalar cannot distinguish a model that learned biology from a model that learned the plate. The tests here are deterministic, cheap, and entirely mechanical — replace an input, rerun the frozen checkpoint, diff the predictions — and they belong inside the feedback loop, not in a reviewer's imagination six months later. And the control-only baseline should be a mandatory row in every one of these tables. In this paper, the entire apparent performance of the winning model was reproducible without ever showing it a compound.
