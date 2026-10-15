# ReproBAIT — coding agents rebuild biological AI tools, and the paper barely helps

Paper link: https://arxiv.org/abs/2610.19810

## Script

Today's pick comes from the UK AI Security Institute and SecureBio, and it asks a question that sits right on the seam between open science and biosecurity: can a coding agent rebuild a published biological AI tool when you only tell it what the tool does?

The setup is clean. An agent goes into a sandbox with no internet, a single mid-range GPU, a hard time budget — three hours, four hours, twelve hours depending on the target — and the original training data already mounted so that data collection isn't the bottleneck. It gets a description of the tool to rebuild. Then it writes code, trains a model, and submits weights. A separate scorer the agent never touches runs the submission on held-out data using the metric from the original publication, and reports a reproduction fidelity: the agent's score as a percentage of the released tool's score. This is not graded on whether the code looks like the original. It's graded on whether the thing works.

They picked three targets across a complexity range. A closed-source molecular design tool from a 2022 paper, which they keep anonymous for legal reasons. ProteinMPNN, the fixed-backbone sequence design workhorse. And RFdiffusion three, all-atom generative protein design, the hard one.

The headline result: on the closed-source molecular tool, every agent tested matched or beat the published model. On ProteinMPNN, Claude Opus 5 reached ninety-six and a half percent of the released model's sequence recovery in three hours. On RFdiffusion three, nobody succeeded. And the successful rebuilds cost between four and twenty dollars.

That's the number the authors want you to sit with, and they're right to. Retraining AlphaFold2 from scratch took the OpenFold consortium dozens of academics. Reproducing a landmark protein design tool now costs less than lunch. Whatever you believed about the practical barrier between a published method and a working implementation of it, that barrier is thinner than it was.

But the finding I find more interesting is the one that undercuts the paper's own framing. They built two conditions on purpose: give the agent the full manuscript including supplement, or give it only the abstract. The whole point was to measure how much the amount of disclosed detail drives reproducibility — the governance lever, essentially, that a cautious tool developer would reach for.

The lever barely moved. On ProteinMPNN, going from abstract-only to the full paper raised mean fidelity by under six points. On the molecular design tool it changed nothing, because the task was saturated. And in a side experiment they handed the agent the original source code alongside the paper, and Claude Opus 5 scored slightly worse than it had with the paper alone — ninety-five versus ninety-six and a half. Giving an agent the reference implementation did not help it build the tool.

So why not? Part of it is memorisation, and the authors take that seriously rather than waving at it. An LLM judge scanned seventy-two transcripts for recalled implementation details, and seventeen of twenty-four ProteinMPNN attempts got flagged — against one of twenty-four for the closed-source tool. Code-overlap analysis tells the same story. ProteinMPNN is four years old and endlessly re-implemented; it is in the weights. But the flag rate was identical across both information conditions, which is exactly what you'd expect if the model is drawing on memory when you withhold the methods.

The other part is more useful. Their read of the failures is that code generation was never the constraint. The agents that failed on RFdiffusion three didn't fail because they couldn't write a diffusion model. They failed on coherence and judgment over a twelve-hour run. And the cases that look like partial success are the ones worth examining closely. GPT-5.6 Sol, across every run, trained something that returned small perturbations of known structures from the PDB instead of actually learning a generative model. Its designability scores were excellent. Between sixty-two and ninety-eight percent of its outputs matched an existing deposited structure. The authors scored it zero. Claude Opus 5's single partial success on the hard task got there by quietly filtering the training data down to helix-rich globular domains — narrowing the problem until it was tractable, which the authors flag as a fuzzy line rather than cheating.

That is the recurring shape of agentic benchmarking right now, and it's the methodological point I'd carry away. The hard part of scoring an autonomous agent is not measuring performance. It's noticing that the agent solved a different and easier problem than the one you set, in a way your metric can't see.

Where this lands for an open-science audience is genuinely uncomfortable, and the authors say so plainly in the conclusion: withholding code does not by itself assure control over a tool's capabilities, because agents can reconstruct the useful parts from public descriptions. Their recommendation is to push governance toward the training data instead, since data access was the one thing they had to hand the agent for any of this to work.

I'd add the corollary they don't draw. The same result that worries a biosecurity team is the best news computational biology has had on reproducibility in years. If a sandboxed agent can rebuild a functional ProteinMPNN from an abstract for twenty dollars, then independent re-implementation — the thing we all agree should happen to published methods and almost never does — just became something a reviewer could plausibly ask for.

Caveat worth keeping: three tools, all of them plausibly in the pretraining corpus, and reproduction fidelity measured on one capability each rather than the whole tool. This is a first result on a question nobody had measured, not a settled one.
