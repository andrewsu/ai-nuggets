# From 17 to 98 — A Rebuttal Preprint Lands the Morning After Stanford's BixBench Number

Paper link: https://www.biorxiv.org/content/10.64898/2026.04.28.721523v1

More headlines:
- Single-cell foundation models reveal context-sensitive cancer programmes under subtype shift — fine-tuned scGPT and Geneformer beat zero-shot baselines on tumour-subtype shift (bioRxiv, May 1, 2026): https://www.biorxiv.org/content/10.64898/2026.04.28.721114v1
- Aiki-GeNano: a three-stage language-model alignment pipeline for epitope-conditioned nanobody generation that bakes developability into training, not post-hoc filtering (bioRxiv, May 1, 2026): https://www.biorxiv.org/content/10.64898/2026.04.28.721526v1
- MetaMuse: a multi-agent system using a SapBERT-backed NormalizerAgent to map free-text biomedical metadata to formal ontology terms — 95%+ accuracy on a manually curated GEO gold standard, with conservative false-negative defaults to block hallucination (bioRxiv, April 20, 2026): https://www.biorxiv.org/content/10.64898/2026.04.12.718044v2

## Summary

A single-author preprint posted to bioRxiv yesterday — Xiaoyu Zhang at California State University San Marcos — directly contests the BixBench number that anchored this morning's Stanford AI Index episode. On BixBench-Verified-50, the curated 50-question subset with ambiguous items removed, three frontier-agent configurations score 88%, 84%, and 98%. The 98% configuration — GPT-5.5 plus Claude's Scientific Skills, bioSkills, and web access — gets 49 out of 50, and the one miss isn't an analytical failure; it's a sign-convention disagreement about how to interpret the CRISPR gene-effect score in the reference answer. Two important caveats: BixBench-Verified-50 is not the same benchmark as the original BixBench that produced the 17%, and the gains come from skills plus external resources, not raw model capability. Read together, this is the Su Lab argument made experimentally — agents stop being remedial at bioinformatics the moment they can call a clean pathway, organism-annotation, BUSCO, or PhyKIT lookup.

## Script

This morning's nugget on this feed was the Stanford AI Index report and the seventeen percent number on BixBench. This afternoon's was Rees and Wilsdon in Nature on agentic AI breaking grant funding. Now here's the third nugget for today, and it landed on bioRxiv yesterday, May first — so it has been public for less than thirty hours, and it directly challenges the morning's headline number.

The paper is "Skill-Augmented Frontier Agents Nearly Saturate BixBench-Verified-50." Single author, Xiaoyu Zhang, California State University San Marcos. Posted to bioRxiv on May first, twenty-twenty-six. DOI ten point six four eight nine eight slash twenty-twenty-six dot zero four dot twenty-eight dot seven two one five two three.

The setup. The original BixBench paper from Future House, the one the Stanford AI Index leaned on, scored frontier agents at seventeen to twenty-one percent on open-answer bioinformatics tasks. That's the sobering number, and that's the number I quoted this morning. After that paper landed, the Future House team, plus other researchers, went back through the benchmark and noticed that some questions were ambiguous — the question wording allowed multiple defensible answers, or the reference answer depended on a sign convention not stated in the prompt. So they curated a fifty-question subset they called BixBench-Verified-50, where the ambiguous items were either dropped or rewritten. That curation is what makes today's number comparable to the morning's.

Now the three configurations Zhang ran. Same local benchmark, same prompt structure, same answer format, same grading pipeline.

Configuration one. GPT-five point four, with Claude's Scientific Skills loaded, no web access. Forty-four out of fifty. Eighty-eight percent.

Configuration two. Claude Opus four point seven, with Claude's Scientific Skills loaded, no web access. Forty-two out of fifty. Eighty-four percent.

Configuration three. GPT-five point five, with Claude's Scientific Skills loaded, plus a separate library called bioSkills, plus web access. Forty-nine out of fifty. Ninety-eight percent.

Read those numbers against the morning's seventeen. Even with the caveat about BixBench-Verified-fifty not being the full benchmark, that is a six-x to thirteen-x improvement on a curated bioinformatics task set, in the span of about eighteen months of model development plus a Skills layer.

The one miss is actually the most instructive part of the paper. On the question Zhang highlights, the agent had to identify the gene whose essentiality was most strongly correlated with a particular cell-line phenotype using the CRISPRGeneEffect dot c-s-v file from the DepMap project. GPT-five point five computed Spearman correlations on the raw values and returned CCND1. The reference answer expected a different gene because, in DepMap's encoding, stronger essentiality is the more negative gene-effect score. Flip the sign, you flip the ranking, you flip the answer. That's not the agent failing to do bioinformatics. That's a question whose correct answer depends on a domain convention that isn't stated in the prompt and that, frankly, working bioinformaticians get wrong all the time when they pull a new dataset for the first time.

The second most instructive passage is Zhang's analysis of the failure modes in the offline configurations — the eighty-eight and eighty-four percent runs without web access. Those failures clustered. They were not random. They were specifically on questions that required pathway data, organism-level annotations, BUSCO completeness assessments, or PhyKIT phylogenetic computations. In other words, the offline agents failed exactly when they needed an external structured resource and didn't have one. Give them web access, the failures go away. Give them a clean pathway database, the failures go away.

That is the Su Lab argument made experimentally. I was making it this morning in the Stanford episode as commentary. Zhang is making it in numbers. Every BixBench-Verified-fifty point that the agents got right because they could pull a Reactome pathway, a BUSCO ortholog set, a NCBI Taxonomy lookup, or a phylogenetic tree from PhyKIT, is a point that does not come from raw model capability. It comes from the curated, structured biomedical resources that this audience builds and maintains for a living. The agent revolution, on real bioinformatics, runs through your databases.

Three things I want to flag before I sign off. First, this is a single-author preprint. It has not been peer-reviewed. The grading pipeline is the same one as the original BixBench, but a careful reader should still want to see independent replication. Second, BixBench-Verified-fifty is not the full BixBench. Saturation here does not mean saturation on real bioinformatics — it means saturation on a fifty-question subset of cleaned-up real bioinformatics. Don't read this as "agents have solved bioinformatics." Read it as "the benchmark gap between agents and PhDs that the Stanford AI Index reported is partly real model improvement, partly partly Skills, and partly artifacts of question wording." Third, the Skills layer matters. Anthropic's Scientific Skills, plus a community bioSkills library — neither of which existed when BixBench was first benchmarked — is doing a lot of the work here. The architecture lesson is that frontier capability on real biology comes from model plus skills plus tools plus structured external data, not from any one of those alone.

Read together, the three nuggets for today actually tell a coherent story. Stanford this morning was the calibration check — seventeen percent on the un-curated benchmark with un-skilled agents. Rees and Wilsdon this afternoon was the political and structural consequence — agents are coming for grant funding whether the system is ready or not. And Zhang yesterday is the methodology pointer — the gap closes when you stack scientific skills on top of frontier models and give them access to the curated resources the field has already built. Three nuggets, one continuous argument.

Link's in the Telegram message. That's your third and final nugget for today.
