# Mozi: Governed Autonomy for Drug Discovery LLM Agents

## Script

Here's a preprint that tackles one of the hardest unsolved problems in agentic AI for science: what happens when your AI agent makes a mistake early in a long pipeline, and that mistake silently corrupts everything downstream?

The paper is called Mozi, from the International Digital Economy Academy. It's a framework for LLM agents in drug discovery, and its core insight is deceptively simple: the problem isn't that LLMs can't do drug discovery tasks — they actually can, for individual steps. The problem is that when you chain those steps together into a real pharmaceutical pipeline — target identification, hit finding, lead optimization — errors compound multiplicatively. A hallucinated protein isoform in step one means hours of wasted GPU time on meaningless docking simulations in step three.

Mozi's solution is what they call "governed autonomy" — a dual-layer architecture. Layer A is the control plane: a supervisor-worker hierarchy where different agents have different permissions. Your literature search agent can't accidentally trigger an expensive docking simulation. Your computation worker can't overwrite experimental data. This isn't just prompt engineering — it's hard-coded tool filtering with role-based access control, like how a hospital restricts who can prescribe medications.

Layer B is the workflow plane, and this is where it gets interesting. Instead of letting the LLM freestyle its way through drug discovery, Mozi encodes the canonical pipeline stages as "skill graphs" — directed acyclic graphs with strict data contracts between stages. Think of them as scientific standard operating procedures that the agent must follow. The protein structure must be properly prepared before docking can begin. The binding pocket must be validated before virtual screening starts. These aren't suggestions — they're hard gates.

The key design principle they articulate is "free-form reasoning for safe tasks, structured execution for long-horizon pipelines." Let the LLM think creatively when the cost of failure is low — literature search, hypothesis generation. But lock it into verified procedures when you're burning compute or making decisions that cascade forward.

They evaluate on PharmaBench, a curated benchmark for biomedical agents, and show superior orchestration accuracy over existing baselines. But the more compelling evidence comes from end-to-end case studies where Mozi navigates massive chemical spaces, enforces toxicity filters, and generates competitive in silico drug candidates — with a full audit trail of every decision.

Two things make this relevant beyond drug discovery. First, the error propagation problem they formalize — where uncertainty at step T compounds through every subsequent step — applies to any multi-stage scientific pipeline. Genomics, materials science, climate modeling. Second, the human-in-the-loop checkpoints they place at "high-uncertainty decision boundaries" represent a pragmatic middle ground between full automation and full human control. The agent runs autonomously through well-understood steps but stops and asks when the stakes are high.

The honest limitation: their benchmark is still largely in silico. The real test is whether Mozi's governed trajectories actually produce better wet lab outcomes than ungoverned agents. But the architecture itself — separating governance from execution, encoding domain SOPs as executable graphs, and making every decision auditable — feels like the right foundation for deploying LLM agents in any high-stakes scientific domain.

Paper link: arxiv.org/abs/2603.03655
