# Omics Data Discovery Agents

## Script

Here's a paper that addresses what might be the single biggest waste in biomedical research: all the published omics data that nobody can actually reuse.

The scale of this problem is staggering. In November 2025 alone, over 1,500 proteomics papers were published to PubMed Central. Most of them deposited raw data somewhere — PRIDE, MassIVE, GEO. But actually reusing that data? That requires tracking down processing parameters scattered across the main text, supplementary files, and code repositories. Figuring out which software version was used. Matching filenames to experimental conditions. A previous study found that data availability drops 17% per year after publication. In practice, most published omics data is functionally dead on arrival.

This paper, from Jesse Meyer at Cedars-Sinai, presents an agentic framework that turns static omics publications into executable, queryable research objects. And it does it end-to-end: from fetching articles, to extracting metadata, to downloading raw data, to re-running the actual quantification pipelines, to performing cross-study comparisons.

The architecture has three layers. First, an article ingestion pipeline that uses LLM agents to extract structured metadata from full-text PMC articles — not just keywords, but dataset locations, processing parameters, experimental conditions, code repositories. They achieve 80% precision on identifying standard repository links like PRIDE and MassIVE datasets.

Second — and this is the key innovation — they use MCP servers, Model Context Protocol servers, to expose containerized analysis tools to the agents. The agent doesn't write custom analysis code for each paper. Instead, it selects the right pre-built container — DIA-NN for data-independent acquisition, MaxQuant for data-dependent acquisition — configures it with parameters extracted from the article, and executes it. This is reproducibility by design: same tools, same containers, parameters derived from the publication itself.

Third, cross-study reasoning. The agents can find semantically similar studies using text embeddings, assess whether their datasets are actually compatible, and perform meta-analyses across papers. In their liver fibrosis case study, agents identified three related papers, obtained protein quantities from each — re-quantifying raw data for one, using published processed data for another, and extracting results from nested supplementary archives for the third. They found 11 out of 18 differentially expressed proteins showed consistent upregulation across species. Six proteins were detected across all three experiments.

Here's what's remarkable: most of those consistently-regulated proteins were not highlighted in the main text of any of the three papers. The cross-study signal only emerged when an agent could systematically compare the full datasets — not just read the abstracts.

The honest numbers: when re-quantifying proteomics data, they got protein abundances correlated above 0.95 with published results. Differentially expressed protein overlap was 63% when they matched the original preprocessing — and dropped to 37% when the agent used default latest-version tools instead. That gap is itself an important finding: software version matters, and agents need to be explicitly told to match published methods rather than using whatever's newest.

For anyone who works with BioThings, knowledge graphs, or data integration — this is directly relevant. It's the infrastructure layer that could make the biomedical literature computationally alive rather than a graveyard of PDFs. And the MCP server pattern for exposing containerized bioinformatics tools to LLM agents? That's a design pattern worth stealing for any scientific domain where you need reproducible, agent-driven analysis.

Paper link: arxiv.org/abs/2603.10161
