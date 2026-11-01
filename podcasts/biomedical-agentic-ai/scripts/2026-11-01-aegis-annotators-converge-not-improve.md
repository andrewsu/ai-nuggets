# AEGIS — a randomized study of an agentic curator, where what moved was agreement, not accuracy

Paper link: https://www.nature.com/articles/s43018-026-01264-6

## Script

Today's pick is a Nature Cancer paper that came out Thursday, from Danielle Bitterman's group at Mass General Brigham and Dana-Farber. The system is called AEGIS, and it reads oncology progress notes to pull out immune-related adverse events — the autoimmune toxicities that checkpoint inhibitors cause in up to forty percent of patients. Six conditions: pneumonitis, hepatitis, colitis, myocarditis, thyroiditis, dermatitis. And it doesn't just flag presence. It extracts whether the event is currently active or historical, a severity grade on the standard oncology scale, whether the clinician attributed it to the drug, how confident they sounded, and the specific sentences in the note that support each call.

The architecture is roughly what you'd guess by now. A splitter routes each note into six condition-specific pipelines; detection and grading each run three times with a judge agent reconciling the disagreements; attribution and certainty get a single pass. It runs on a mid-sized OpenAI model at about two cents a note.

But the architecture isn't why this is worth five minutes. It's that they ran three phases, and each phase takes something back from the one before it.

Phase one is retrospective, on two hundred sixty-three held-out expert-annotated notes. Detection comes in at an F-one of zero point nine three. Strong. But in the same paragraph is a baseline that should stop you cold: a hand-written regular expression with seven hundred seventy-nine terms performed comparably to, and in some cases better than, several of the language-model configurations at binary detection. The authors say so plainly, and their defense is correct — a regex can't give you a grade, an attribution, or an evidence span. But it does mean the agentic machinery isn't buying you the detection. It's buying you the attributes. And the attributes are where the numbers soften. Multi-class severity grading lands at zero point six six, with colitis at zero point five one, and the errors pile up at grades two and three — which are exactly the thresholds that decide whether you hold the drug and start steroids.

Phase two: three months of silent prospective deployment inside the live record, eight hundred eighty-four notes. Performance held its shape but lost magnitude. Binary F-one across grade, attribution and certainty fell to zero point seven two for active events. At the note level, the model's grade matched human review sixty-two percent of the time. The authors attribute that to drift — a system tuned on a curated corpus meeting a stream of real documentation written years later on different templates. That is the honest version of a result everyone in this field should expect and almost nobody reports.

Phase three is the one I actually want to talk about. A randomized two-by-two crossover: seventeen clinical research coordinators, twenty notes, each note annotated once manually and once with the agent's labels pre-populated. This is the study design we keep saying clinical AI needs and essentially never get.

Time dropped forty-three percent — median four hundred twenty-eight seconds down to two hundred forty-two. That's the primary endpoint, properly analyzed with clustering by participant, and it's real.

Now look at what happened to quality. The accuracy result is a composite metric requiring all six active-event grade labels to exactly match the gold standard: nineteen percent manual, twenty-six percent assisted, odds ratio one point four five, p equals zero point zero four five. That is one stringent metric scraping past the line. And in the very same figure, the comparison of overall grade accuracy — a paired sign test across participants — comes back at p equals zero point seven nine. Null.

What did move, enormously, was agreement between annotators. Krippendorff's alpha went from zero point two two to zero point eight five in one note set, and from zero point five one to zero point eight two in the other. That is not a subtle effect.

So the honest reading of the randomized phase is this. The agent made the annotators faster, and it made them agree with each other, and it did not demonstrably make them more right. They converged. They converged on the model's suggestion — the authors say so explicitly, call it anchoring, and flag the automation-complacency risk themselves, which I credit them for.

Here's why that matters more than it sounds. The thing the annotators converged on is the grade. The grade is the system's weakest output — zero point six six retrospectively, sixty-two percent agreement with humans in live deployment. So the measured benefit is standardization around the least reliable channel in the pipeline. For a registry or a pharmacovigilance database, consistency genuinely is worth something on its own; it's what makes the downstream statistics tractable. But consistency and correctness are different goods, and this study measured one of them convincingly and the other not at all.

One more thing worth noting. What the coordinators actually praised wasn't the labels. It was the evidence highlighting — the spans in the note supporting each call — because it let them verify without re-reading the whole thing. That's the same lesson this show has landed on from three unrelated directions this month. The durable artifact an agent produces is the trace, not the answer.

Code and prompts are public under an MIT license. And the authors state outright that no phase of this work establishes external validation — every phase ran inside a single health system. That sentence belongs in more papers than it appears in.
