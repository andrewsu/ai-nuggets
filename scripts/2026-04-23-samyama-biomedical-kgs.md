# Samyama: Open Biomedical Knowledge Graphs at Scale with Schema-Driven LLM Agent Access

Paper link: https://arxiv.org/abs/2603.15080

## Summary

A two-author arXiv preprint quietly drops three open-source biomedical knowledge graphs — Pathways, Clinical Trials, and Drug Interactions, totaling 7.9 million nodes and 28 million edges — alongside Samyama, a Rust graph database, and the real architectural bet: schema-driven Model Context Protocol servers that auto-generate typed LLM tools from the running database schema. On their 40-question BiomedQA benchmark, MCP-tool access hits 98 percent accuracy versus 85 percent for schema-aware text-to-Cypher and 75 percent for GPT-4o standalone. The takeaway isn't the KGs themselves — it's the pattern: stop asking LLMs to write Cypher, and instead expose validated, parameterized domain tools like pathway-membership and drug-interaction-lookup. For anyone building LLM interfaces over biomedical KGs — Wikidata biomedical subsets included — this is the architecture to study.

## Script

Samyama. Today's nugget is a preprint that didn't make a lot of noise, from two authors — Mandarapu and Kunkunuru — who posted it on arXiv last month. But if you work anywhere near biomedical knowledge graphs, and especially if you've been trying to figure out how to put an LLM agent on top of one, this paper is doing something worth stealing.

Here's what they shipped. Three open-source biomedical knowledge graphs, all on GitHub. A Pathways knowledge graph with about 119 thousand nodes, pulled from Reactome, STRING, Gene Ontology, WikiPathways, and UniProt. A Clinical Trials knowledge graph with 7.7 million nodes, pulled from ClinicalTrials.gov, MeSH, RxNorm, OpenFDA, and PubMed. And a Drug Interactions knowledge graph with about 33 thousand nodes, pulled from DrugBank's CC0 release, DGIdb, and SIDER. Together, almost 8 million nodes and 28 million edges. That alone is a solid open-data contribution.

But that's not the interesting part. The interesting part is what sits in front of the knowledge graphs.

Everything runs on Samyama, a graph database they wrote in Rust. It's performant, fine, most graph databases are. The architectural bet is what they've built on top: every knowledge graph ships with a Model Context Protocol server — an MCP server — that auto-generates typed tools for an LLM agent, based on the running schema of the database. So when an agent connects, it doesn't see a black-box Cypher endpoint. It sees a discrete, validated catalog of operations: pathway-membership-lookup, drug-interaction-query, clinical-trial-by-condition. Each tool has typed parameters, parameterized Cypher templates behind the scenes, and no way for the agent to freestyle a broken query.

Now. Why does that matter? Let's talk about the alternative.

The dominant pattern for LLMs plus knowledge graphs, for the last couple years, has been text-to-Cypher. You give the LLM a schema description, ask it a question in natural language, and it tries to generate a Cypher query that answers the question. It works some of the time. It also hallucinates relationships that don't exist, uses property names that got renamed three schema migrations ago, and writes queries that are syntactically valid but semantically wrong in ways that return plausible-looking garbage. The failure modes are subtle and the debugging story is terrible.

The authors built a benchmark called BiomedQA — forty pharmacology questions spanning seven categories — and ran three conditions. Standalone GPT-4o: 75 percent accuracy. Schema-aware text-to-Cypher: 85 percent. Their MCP-tool approach: 98 percent. Zero schema errors.

The gap between 85 and 98 is where the argument lives. The MCP approach wins because it reframes the problem. Instead of asking the LLM to be a query-writing expert, you ask it to be a tool-selection-and-parameter-extraction expert. Pick the right tool. Fill in the parameters. The database layer handles the rest, and it handles it correctly every time because the Cypher was written by a human who knew the schema.

There's a second clever piece here — federation. Loading all three knowledge graph snapshots into a single Samyama tenant lets you do property-based joins across datasets. The example they walk through is joining Drug Interactions to Pathways by matching gene names to protein names — bridging the two knowledge graphs through a shared identifier at query time, without pre-merging them during loading. For anyone who's ever tried to integrate biomedical KGs that were built independently with different identifier conventions, this matters. It lets each KG evolve on its own schema and refresh cadence, while still being query-able together.

A few honest caveats. Forty questions is a small benchmark, even if it was designed carefully. The KGs are useful but they're not unique — there's meaningful overlap with SPOKE, Hetionet, PrimeKG, the Monarch Initiative, the biomedical slice of Wikidata that Andrew's lab has been curating for years. And MCP-tool approaches have a known ceiling — if the question requires an operation that nobody wrote a tool for, the agent is stuck. Text-to-Cypher is strictly more flexible. You're trading flexibility for reliability.

But here's why I think this paper is worth your time even if you never touch their KGs directly. The pattern is generalizable. If you've got a biomedical knowledge graph — your own curated one, a snapshot of a public one, a Wikidata subset — and you want to let an LLM agent query it usefully, the default instinct is to wire up text-to-Cypher. This paper is a clear argument that you should probably build schema-driven MCP tools instead. You get better accuracy, typed safety, and auditability. And the schema-driven part means you can regenerate the tools automatically when the KG evolves, which is how you keep the agent interface from drifting out of sync with reality.

One last thing. Everything is open-source — the graph database, the three knowledge graphs, the benchmark. That's increasingly rare for this kind of work. A lot of agentic-AI-over-KG papers release a demo and a marketing blog post. This one released a stack you can actually fork and run.

Link's in the Telegram message. That's your nugget.
