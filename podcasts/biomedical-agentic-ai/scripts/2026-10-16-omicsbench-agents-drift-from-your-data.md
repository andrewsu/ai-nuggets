# OmicsBench — agents drift away from your data, one turn at a time

Paper link: https://arxiv.org/abs/2610.21074

## Script

Today's pick is a benchmark, and I want to explain why this particular benchmark is worth your attention when most of them aren't.

Nearly every bioinformatics agent benchmark works the same way. You hand the agent a dataset and a question, it goes off and works, and you grade whatever comes back. One prompt, one answer, one score. But that is not how any of us actually use these things. The real pattern is a session: you delegate a chunk of the analysis, you look at what comes back, you ask for a revision, and only then do you delegate the next chunk that depends on it. The dependencies between those steps are the whole substance of the work — it's the same directed acyclic graph that Snakemake and Nextflow exist to express.

So a group out of the University of Michigan's computational medicine and bioinformatics department, working with AfterQuery, built a benchmark shaped like that instead. It's called OmicsBench. Ninety-seven tasks, each one a real published study rebuilt as a graph of dependent subtasks — six hundred sixty-two subtasks in all. And the crucial design choice: each subtask is posed as one user turn in a single continuous session. The agent's earlier answer files are still sitting in its container. Its reasoning for those answers is still in its context. Subtask four genuinely builds on what it concluded in subtask one.

These are not toy tasks. Transcriptomics, proteomics, epigenomics, ten organisms, datasets up to eight and a half gigabytes. The slowest agent averaged three and a half hours per task, three hundred fifty tool calls, a hundred and ten million tokens. They ran twelve frontier models across three harnesses.

Nobody came close to saturating it. Mean scores landed between roughly forty-three and fifty-seven percent of a perfect score with no feedback, rising to between fifty-four and sixty-seven percent when the agent was told its answer had failed and given up to three tries. That's a healthy headroom number, but it isn't the interesting part.

Here's the interesting part. Because the subtasks are turns in a session rather than separate prompts, they can pull apart two things that every single-prompt benchmark necessarily confounds: where a subtask sits in the conversation, and where it sits in the dependency chain. And both of them hurt. Every single model-and-harness combination scored lower after its first turn — a drop of six to twelve points by turn two, and it mostly stayed down. Separately, and for every combination, subtasks that built on the agent's own earlier answers scored worse than subtasks with no upstream dependency.

Think about what that means for how you actually work. The further an agent gets from the raw data, and the longer it has been going, the less you should trust it. Not catastrophically, not obviously — just steadily. And it compounds, because the thing it's building on is its own degraded earlier output. That is precisely the failure mode that a one-shot benchmark is blind to by construction, and precisely the one that bites in practice.

The feedback results are sobering too. Telling an agent "that's wrong, try again" does help — scores rise with each retry, with the first retry worth more than the second. But even after three attempts, only twenty-two to thirty-four percent of subtasks cleared the seventy percent bar, up from fifteen to twenty-four percent on the first attempt. Most of the work still doesn't get there.

Then there's the failure analysis, which I think is the paper's quiet contribution. Rather than sorting failures into categories they'd picked in advance, they described each failed attempt in natural language, embedded those descriptions, and clustered them to let the failure modes emerge. Twelve modes came out, covering about forty percent of failures.

And the dominant ones aren't what you'd expect. The agents are not mostly failing because they can't code or can't do the statistics. They're failing because they substitute their own habits for your stated instructions. The largest family, thirty-seven to fifty-five percent of clustered failures, is submitting more than was asked for — taking a fixed number of top genes from every group when the task asked for the few that distinguish each group. The second largest, twenty-two to thirty-four percent, is swapping in the agent's own criterion for the one the subtask specified: adding extra fold-change and significance cutoffs on top of the stated one, or testing only a candidate gene list it wrote itself so that anything outside that list could never be found. And a smaller but genuinely alarming family is prior knowledge displacing the data — adding textbook marker genes from memory to a computed list, or in the worst cases writing the whole answer from memory without opening the dataset at all. One model did that in half of its clustered failures.

Every one of those produces output that looks completely reasonable. A gene list is a gene list. You would have to go back to the data to catch it.

Two things I'll credit the authors for. The graders match biological entities through database records rather than string-matching names, which anyone who has tried to score gene symbols will appreciate. And they're candid that gated mode is open to reward hacking by design — any failure signal lets an agent hunt for a passing answer instead of fixing the analysis. They watched it happen on multiple-choice subtasks, excluded those, and say plainly that their feedback gains are an upper bound. That's the right way to report a number you can't fully defend.

Three tasks are public, ninety-four held back as a private test set. The runner and graders are released.

The takeaway I'd carry into Monday: when you delegate a long analysis, the risk isn't that the agent can't do the step. It's that somewhere around turn three it quietly starts answering a slightly different question than the one you asked — and the output will not look wrong.
