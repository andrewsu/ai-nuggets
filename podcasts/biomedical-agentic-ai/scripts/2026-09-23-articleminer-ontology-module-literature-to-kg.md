# ArticleMiner — ontology-guided knowledge graphs from papers, where the domain knowledge is a bounded module rather than a prompt

Paper link: https://arxiv.org/abs/2609.25607

## Script

Today's pick went up on arXiv yesterday from USC's Information Sciences Institute — Craig Knoblock and Jay Pujara's group. It's called ArticleMiner, and it's about building knowledge graphs out of scientific publications.

The premise is one sentence worth stealing. Recovering the rows and columns of a table is not the same as recovering the scientific fact that table reports.

Here's their example. A cell reads "less than zero point five." The column header says gold, in parts per million. A method label elsewhere on the page says the measurement came off a mass spectrometer. That cell is not a measurement of zero point five. It's a below-detection-limit observation, which is a categorically different kind of thing, and if you write it into a graph as a number you have manufactured a false fact. Same problem with composition percentages, where whether you're reading weight percent or mole percent is stated in a caption and nowhere near the cell. Same with a dash, which in one field means the component is absent and in another means nobody reported it.

So the failure they're aiming at isn't parsing. A number means something only through its header, its caption, its unit, its analytical method, and the conventions of its field — and not one of those lives inside the cell.

Their answer is an architectural split, and this is the part I think is actually the contribution. On one side there's a shared, domain-blind pipeline: parse the paper and its supplementary files with five different PDF backends, have a language model propose records, run a completeness gate that can retry, reconcile the candidates, and serialize. On the other side, per task, there's a small human-authored module that supplies the meaning. The module lists the canonical names the graph is permitted to use, the surface forms that map onto them, a handful of deterministic derivation rules, executable validity constraints, an identity key for merging, and the bindings that write RDF. It defines what the task is allowed to emit. Crucially, it does not try to axiomatize the field. These modules run sixty to two hundred twenty entries — flat vocabularies and shallow hierarchies, validation as plain Python, no reasoner anywhere.

That's the bet. Domain knowledge that would otherwise be smeared across a prompt becomes an inspectable, versionable, testable artifact — and when something goes wrong you can tell whether the evidence was missing from the document, or the model misread the context, or one of your declared rules rejected a good record.

They build four of these, for drug-discovery bioactivity tables, glass compositions, machine learning results tables, and mineral geochemistry, and run them over a hundred sixty-three papers. The geochemistry benchmark is new, with ground truth curated by domain experts at the U.S. Geological Survey.

Against a same-model few-shot baseline, ArticleMiner wins on all four tasks across five different closed models. Good. But look at the absolute numbers, because they're the honest part of this paper. On the drug-discovery tables, strict tuple F-one is thirty-two. Thirty-two. On the machine learning tables, fifty-two. Only the glass compositions clear eighty. This is a well-resourced group, with expert ground truth, five parsers, ontology grounding, and the strongest available models, and on bioactivity tables it recovers roughly a third of the facts correctly and completely.

Two findings from the ablations that I'd want any of us building this kind of pipeline to sit with.

The first is that more machinery is not monotonically better. Removing their "paper intelligence" component raises the drug-discovery score from thirty-two to forty-five under one model — and lowers it under another. Dropping their single strongest parser out of the five-way ensemble collapses the glass benchmark from seventy-one to forty-three — and that same parser running alone, with no ensemble at all, scores seventy-two, which just edges out all five fused. Every extra evidence source proposes more candidates, and some of those candidates are wrong. There is no universal configuration here, and the paper says so.

The second is about what validation can and cannot do for you. Open-weight models on the glass benchmark hit precision of seventy-nine to eighty-eight percent, with recall between ten and forty-three percent. Schema validation is filtering out a strong generator's invalid tuples very effectively — and it cannot recover a single tuple that was never proposed. Validation buys you precision. It buys you nothing on recall. And the error profiles invert by task: on the glass tables, ninety-two percent of their errors are omissions, while on the drug-discovery and machine learning tables, well over half are over-extraction. Those demand opposite interventions.

The honest verdict from all this is that the semantics are increasingly solvable and the acquisition is not. Getting the evidence out of the PDF and its supplements remains the bottleneck, which is a deeply unglamorous conclusion and almost certainly the right one.

One more thing I want to credit. The threats-to-validity section in this paper is unusually candid — they state that the provenance of some historical runs is incomplete, so those comparisons are descriptive and not significance claims. They note they never measured downstream query quality on the resulting graph. They never recorded person-hours to author a module, so they explicitly decline to claim reduced adaptation effort. And they flag training-data contamination as unaudited. That kind of accounting is rarer than it should be, and it makes the numbers more useful, not less.

Cost, since you'll want it: three to ten cents per paper with a small model, ten to thirty cents with a large one, under a minute to three minutes each. Cheap enough that compute was never the constraint. The constraint is a person who knows the field sitting down to write two hundred twenty lines of what the graph is permitted to say.
