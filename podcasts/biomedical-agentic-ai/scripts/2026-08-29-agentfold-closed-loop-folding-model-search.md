# AgentFold — an agent rewrites a protein folding model, eighty variants at a time

Paper link: https://arxiv.org/abs/2608.26747

## Script

Today's pick is a preprint called AgentFold, out of Hunan University with collaborators at Nanjing, the Chinese University of Hong Kong, Zhejiang, Yale and Stanford. It asks a question the agentic-science literature has mostly dodged. Can a language model agent actually improve a serious scientific machine learning system? Not propose ideas about one, not write a benchmark harness — edit the code, retrain, and come back with something measurably better.

They picked protein folding as the test bed, which is a good choice, because a folding model is about as tightly coupled as scientific code gets. Sequence representations feed pair representations, pair representations bias attention inside the structure module, the structure module emits coordinate frames, those frames get recycled, and the whole thing is tied together by a loss defined over three-dimensional geometry. You cannot change one piece and reason locally about what happens downstream. Evaluation is expensive and multi-objective too — local accuracy, global fold quality, backbone geometry and physical plausibility all move independently of each other.

AgentFold wraps that setting in a tree search. Starting from an ESMFold-derived codebase, the system samples a parent variant, proposes an architectural hypothesis, writes and debugs the code until training actually launches, trains it, evaluates the resulting structures, and then writes the entire intervention into a structured memory — the diff, the stability signals, the metric deltas, and an analyst agent's attribution of which change caused which delta. A Monte Carlo tree search controller then reallocates compute toward the promising branches, updating node scores in batches every ten iterations rather than after every rollout, because every rollout here is a training job.

What did it cost? Roughly eighty variants, about five thousand GPU-hours, and around a hundred and seventy million language model tokens.

What did it buy? At a matched budget of thirty-six evaluations, the best variant reaches a local distance difference score of zero point two eight five, against zero point two six five for a Codex baseline that proposes independently with no search tree and no record of previous attempts, and zero point two six zero for a random controller drawing from the same edit space. That gap is the seven-and-a-half-percent headline.

Now, read the limitations section, which to the authors' credit says this plainly. This is not ESMFold. The substrate is a compact one-block derivative with twenty-two and a half million parameters, trained on a thousand protein chains. Its baseline score is zero point two three two. Real ESMFold on real data lives up around zero point seven and above. So the agent is optimizing a deliberately crippled proxy — which is the only way you could afford eighty training runs, but it means the headline reads "an agent improved a toy folding model," and whether any of it transfers to a system anyone would actually run is, in the authors' own words, unverified.

The gains are narrower than the aggregate suggests, as well. When they break the metrics apart, the improvements land almost entirely in local structure — loop regions, medium-range contacts, physical plausibility scores. Global fold quality, measured by template-modeling score, barely moves. The agent found ways to clean up local geometry. It did not find a better way to fold a protein.

So why is this worth five minutes? Because the interesting artifact isn't the model. It's the trace.

By keeping every failure in the tree alongside every success, and by sampling sibling variants from the same parent so that candidates differ by roughly one intervention, the system generates something close to a controlled comparison across eighty design choices. And what falls out is legible. Edits that install soft, learnable priors early — biasing attention before any coordinates exist — tend to help. Edits that gate the magnitude of refinement updates multiplicatively tend to help. Edits that perturb geometry directly, after coordinates are already forming, or that feed geometric signals back into attention, tend to fail catastrophically. And catastrophically is the right word. Several of those variants collapse to scores of essentially zero — not a modest regression, total training failure.

There is a nice negative result on scale in here too. The best variant added about one percent to the parameter count. A near-best variant added fifteen thousand parameters. Meanwhile a thirty-one-million-parameter variant is among the ones that collapsed outright. Placement beat capacity, consistently.

Two things I'd take away. First, the margin over the Codex baseline is the real scientific claim, and it's a claim about memory, not about reasoning. Same models, same edit space, same training pipeline, same evaluator — the only difference is that AgentFold remembers what failed and the baseline doesn't. That's modest but genuine evidence that structured failure memory is where the leverage sits in agentic experimentation.

Second, the cost accounting. Five thousand GPU-hours and a hundred and seventy million tokens produced three design heuristics that a good structural biology methods person might have offered you over coffee. That's not damning — the agent produced them with evidence attached, and with the failure cases documented in a way a coffee conversation never is. But it is exactly the number that agentic-science papers usually leave out, and it's the number that decides whether this becomes a research practice or stays a demonstration.

The code and experimental resources are on GitHub, which, given that the whole value proposition here is the intervention trace, is the part worth actually looking at.
