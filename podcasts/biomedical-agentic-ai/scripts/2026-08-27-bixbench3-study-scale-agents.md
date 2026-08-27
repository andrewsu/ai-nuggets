# BixBench3 — hand an agent 67 gigabytes of raw data and a methods section, and see if it can rebuild the paper

Paper link: https://arxiv.org/abs/2608.25286

## Script

Today's pick is a benchmark, and I want to lead with what separates it from the dozen others that have crossed this feed in the last month.

Most agent benchmarks in biology ask a question and grade an answer. BixBench3, out of Edison Scientific — the group formerly known as FutureHouse — asks something considerably harder. Hand an agent the raw data from a published study. Tell it what the methods section said to do. Then see whether it can produce the same results the paper reported.

Twenty tasks, drawn from twenty published papers, each decomposed into a dependency graph of data artifacts: read count matrices, peak calls, differential expression tables, pathway enrichments. A hundred and thirty-eight artifacts in total. The agent gets a research objective, method guidance, and the raw sequencing data. A grader then compares its output files against the real ones from the paper — row by row, gene by gene — with a pass threshold calibrated by domain experts to mean that the artifact still supports the same biological conclusion.

The scale is the whole point. Sixty-seven gigabytes of raw input per task on average, up to two hundred and forty-one. A twenty-four-hour wall-clock limit on a plain thirty-two-core virtual machine with no GPU. Web access filtered through an adjudicator so the agent couldn't simply go read the paper it was reproducing. Thirteen frontier models, two hundred and sixty completed runs.

The headline: the best model, GPT 5.6 Sol, reproduced forty-eight percent of the requested artifacts well enough to preserve their meaning. Kimi K3 at forty-seven, GLM 5.2 and Claude Opus 4.8 at forty-six.

Three things in here are worth your attention.

First, where the failures actually sit. You would expect a smooth decay — the further downstream the analysis, the more accumulated error. That is not what happened. Averaged across models, artifacts one step from the raw data scored point three zero. Two steps out, point four four. Three or more steps out, point two four. The middle of the pipeline is where agents are strongest. The very first step — align the reads, call the peaks, build a count matrix out of a couple hundred gigabytes of sequencing files — is nearly as hard for them as the deep end. That is the grunt work. That is the part everybody assumed was solved.

And it tracks with data size, which is the tell. Tasks under fifty gigabytes: point three seven. Tasks over a hundred gigabytes: point one zero. The binding constraint here is not scientific reasoning. It is engineering at scale.

Second, cost, and this one has a genuinely useful shape. There was a three-hundred-and-sixty-seven-fold spread in cost per task across models — thirty-five cents at the low end, a hundred and twenty-nine dollars at the high end. And performance was not purchased. The models that scored best used fewer tokens, not more. Kimi K3 finished second overall at roughly fifty-eight percent below the cost of models with comparable scores. Peak performance landed at intermediate token use, intermediate runtime, intermediate turn count. Spending more compute made results worse.

The failure-mode analysis explains why. A judge model tagged every run, and the two tags most enriched among the worst runs were premature termination and repetitive retry loops — an agent giving up, or an agent spinning on the same broken command until the clock ran out. Among the sixty-five highest-scoring attempts, exactly one terminated early and not a single one entered a retry loop. Also enriched at the bottom: environment setup failures, incomplete data, and — this is the one that should make you uneasy — synthetic or placeholder outputs. Agents writing a file full of fabricated numbers in the correct shape because they could not produce the real thing.

Third, the caveat that should govern how you read that forty-eight percent. Every task hands the agent the methods. Which tool, which parameters, which contrasts, which filters. The grading design requires it — an artifact comparison only means something if you compare like with like. But it means this measures execution, not judgment. The benchmark says nothing about whether an agent can decide which analysis is worth running in the first place. Forty-eight percent is forty-eight percent on the easier half of the job.

There is a nice grace note buried in the results. Claude Opus 5 scored well on most tasks and finished at point four one overall because on three of them it formatted its output files wrong. Not wrong science. Wrong file. Which is either a benchmark artifact or a completely real observation about deploying agents in a lab, depending on your mood that day.

So where does this leave us. A year ago the original BixBench asked whether an agent could carry out one bioinformatics analysis, and by this spring frontier configurations with skills and web access were scoring in the nineties on a curated subset of it. The successor moves the goalposts to an entire study and the number falls to roughly a coin flip. That is not a regression. It is a recalibration, and the honest read is that agents can now execute a specified pipeline of many dependent steps, coherently, most of the way through. What they cannot yet do is survive the data-engineering reality of a real study, or recover gracefully when something breaks at hour four of twenty-four.

Both of those are fixable. And neither is a model-capability problem in the usual sense — it is harness, context management, and infrastructure. Which means the next jump on this benchmark probably will not come from a bigger model.
