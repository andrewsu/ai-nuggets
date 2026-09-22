# Ollie's AI Pulse — 2026-09-22

## Script

Source: Xiaomi MiMo, "MiMo-V2.6" release page (Pro and Flash, natively omnimodal, MIT license) — https://mimo.xiaomi.com/mimo-v2-6
Source: Xiaomi MiMo live reinforcement-learning dashboard, the pro and flash runs described on this show on September 17 — https://mimo.xiaomi.com/rl/
Source: Xiaomi MiMo model repositories on Hugging Face (MiMo-V2.6-Pro-RL, MiMo-V2.6-Flash-RL, MiMo-V2.6-Distill-Qwen-9B) — https://huggingface.co/XiaomiMiMo
Source: Hacker News discussion, "MiMo v2.6" (902 points, 397 comments; includes the rao-v, aarondong, GodelNumbering, Zambyte and ignoramous comments referenced, and the circulating Terminal-Bench 4.0 table) — https://news.ycombinator.com/item?id=49792730
Source: Latent Space, "[AINews] Xiaomi MiMo-V2.6-Pro 1T-A42B: the new top Open Weights model, trained for $3M" (Sep 22, 2026; the three-axis RL scaling summary, the Artificial Analysis and Vals numbers, the 130-hour / 75-billion-token / 2.6-million-dollar figures attributed to @zephyr_z9, and the Thom Wolf / bertgodel environments thesis) — https://www.latent.space/p/ainews-xiaomi-mimo-v26-pro-1t-a42b
Source: SpaceXAI, "Introducing Grok 4.7" (Sep 21, 2026; the benchmark table quoted — CursorBench 4.0, Terminal-Bench 4.0, Harvey Legal Agent Benchmark, HealthBench Professional) — https://x.ai/news/grok-4-7
Source: Colin Breck, "I Don't Want to Read What You Didn't Write" (Sep 21, 2026; the academic-paper account, the Dunlop survey figures, the Sarris and Stroustrup quotes) — https://blog.colinbreck.com/i-dont-want-to-read-what-you-didnt-write/
Source: Hacker News discussion of the Breck essay (672 points, 264 comments; includes the hatthew, intended, Analemma_ and BrenBarn comments quoted) — https://news.ycombinator.com/item?id=49794330
Source: Bryan Cantrill, "The revolt of the reader" (Sep 5, 2026; 612 points on Hacker News; the "LLM-triggered ejection handle" line quoted in Breck's essay) — https://bcantrill.dtrace.org/2026/09/05/the-revolt-of-the-reader/
Source: Russell Brandom, TechCrunch, "Meta's AI agent has been blocked from using Amazon.com" (Sep 21, 2026; the Amazon error message, reporting GeekWire) — https://techcrunch.com/2026/09/21/metas-ai-agent-has-been-blocked-from-using-amazon-com/
Source: Sarah Perez, TechCrunch, "Meta's Muse is outpacing ChatGPT's early mobile launch" (Sep 21, 2026; Appfigures estimates) — https://techcrunch.com/2026/09/21/metas-muse-is-outpacing-chatgpts-early-mobile-launch/
Source: Jagmeet Singh, TechCrunch, "The man who built Apple's stores doesn't buy Silicon Valley's bet on AI shopping" (Sep 21, 2026; all Ron Johnson quotes) — https://techcrunch.com/2026/09/21/the-man-who-built-apples-stores-doesnt-buy-silicon-valleys-bet-on-ai-shopping/
Source: Nathan Lambert, Interconnects, "The current balance of power in open models" (Sep 21, 2026; prepared remarks to a Congressional briefing, published with author narration on the Interconnects podcast feed; all download, Intelligence Index, OpenRouter, OpenCode and arXiv figures) — https://www.interconnects.ai/p/the-current-balance-of-power-in-open
Source: Advisory Group on Mathematics and Artificial Intelligence, guest post announcing itself on Terence Tao's blog (Sep 21, 2026; full membership list, the independence statement, and the "current task" paragraph quoted) — https://terrytao.wordpress.com/2026/09/21/advisory-group-on-mathematics-and-artificial-intelligence/
Source: Aditya Mehta, TechCrunch, "OpenAI forms math advisory group as its AI resolves more than 100 open problems" (Sep 21, 2026; the pacing carve-out and the overlap with the Fields Medallists' letter) — https://techcrunch.com/2026/09/21/openai-forms-math-advisory-group-as-its-ai-resolves-more-than-100-open-problems/
Source: Timothy Gowers, "Why I didn't sign the Fields medallists' letter" (Sep 17, 2026; the callback) — https://gowers.wordpress.com/2026/09/17/why-i-didnt-sign-the-fields-medallists-letter/

Here's what the AI world is talking about today. Xiaomi shipped what is now the top open-weights model on the planet, and the thing the research community fixated on was not the weights. Grok four-point-seven landed, and two respected evaluation shops reached opposite conclusions about it within a day. Essays about AI writing hit the front page three days running. Amazon quietly locked Meta's shopping agent out of its store. And Nathan Lambert published the remarks he gave to Congress about open models. The thread running through all of it is a question about scarcity. When the obvious inputs get cheap, what's the thing that doesn't?

Start with Xiaomi, because this one closes a loop we opened on this show five days ago.

Sunday night into Monday, the MiMo team released version two-point-six in two sizes, pro and flash, both natively omnimodal, both under an M.I.T. license. Pro is about one-point-oh-two trillion total parameters with forty-two billion active. Artificial Analysis put it straight at the top of the open-weights field on their Intelligence Index with a score of forty-six, and on the intelligence-versus-cost frontier at roughly thirteen cents per index task. Nine hundred points on Hacker News overnight. One commenter caught the detail that makes the efficiency case: the one-trillion-parameter pro model outscores Kimi K-three, which is a two-point-eight-trillion-parameter model.

But almost nobody spent the thread arguing about the score. They spent it on the training stack, because Xiaomi published the whole thing while it was happening.

If you heard the September seventeenth episode, this is the same dashboard I spent five minutes on — the live reinforcement learning runs streaming from the trainer's logs, restart counter, plain-language incident notices about V-RAM failures on a node, and a cost meter ticking in the corner. When I looked then, it read about one point four million dollars, two days in, climbing at roughly thirty-one thousand an hour. The run has now finished and shipped, and a figure circulating from one researcher and picked up in Latent Space's recap puts it at about a hundred and thirty hours, seventy-five billion tokens, two point six million dollars. The meter was honest, and the number it landed on is small.

The report describes scaling reinforcement learning along three axes at once. Bigger and faster — fifteen hundred and sixty-eight samples per update, fully asynchronous, out to a million tokens of context. More tasks — coding, general agents, visual, cyber, music, deliberately mixed across several harnesses so gains in one capability reinforce the others. And more grader compute for a denser reward signal on long-horizon work.

Here's the part that made it a discourse event rather than a release. Xiaomi is open-sourcing the environments. Roughly seven thousand of them, plus the training recipes, the coding rewards, the vulnerability-reproduction environment, the web-development grader, the music scorer. Not the full task datasets yet, which is the real caveat. But the environments.

Thom Wolf and others landed on the same reading within hours, and I think it's right: high-quality open reinforcement learning environments may now be as strategically important as pretraining corpora were in the last cycle. Weights are cheap. Compute you can rent. The scarce thing is a verified, non-gameable environment that produces a reward signal worth learning from — and Xiaomi just gave seven thousand away.

One commenter, going by aarondong, drew the sharpest implication and then correctly refused to overclaim it: this waters down the distillation-attack story, because they clearly have their own environments — with the caveat that the datasets are still opaque, so nothing is actually proved. Hold onto that, because Lambert has a number for it later.

And the honest counterweight from the same thread: top of open-weights is not top. On harder long-horizon agentic evaluations the gap is still wide — a table circulating in the comments puts MiMo pro around thirty-five on Terminal-Bench four against roughly sixty for the strongest closed model. One commenter compressed it into a sentence: American models are on the frontier of capability, Chinese models on the frontier of efficiency.

Second thing, and it's quick, but it's a good lesson in reading leaderboards.

Grok four-point-seven shipped Monday. Larger base model, a longer reinforcement learning run weighted toward tasks that take many hours, and — interesting design choice — trained to natively understand its own agent harness. Their own published table shows gains essentially everywhere: Terminal-Bench four from twenty point three to thirty-eight percent, the Harvey legal agent benchmark from fifteen point eight to nineteen point six, HealthBench Professional from forty-eight point five to fifty-six point seven.

Then the evaluators weighed in. Artificial Analysis scored it fifty-six on their Coding Agent Index, with gains across the board. Vals ranked it number twenty-four, down five points from Grok four-point-six — while also observing gains in legal and medical.

Two days ago on this show I covered Vals raising money on the pitch of becoming the gold standard for AI benchmarking. This is the first real test of that, and two serious shops looked at one model and disagreed about direction. Not magnitude — direction. Nobody is lying. It's what happens when "better" is a weighted average and the weighting is the product you're selling. So the reflex: never ask whether a model went up. Ask what the index is weighting, and whether it weights the thing you actually do.

Third, the reader revolt, because three essays in three days is convergence.

Colin Breck published "I don't want to read what you didn't write" on Monday, six hundred and seventy-two points, after Erich Grunewald on Friday and Paul Bakker on Monday said adjacent things, all building on Bryan Cantrill's "The revolt of the reader." The survey they cite, by Cynthia Dunlop, found that when developers think a piece is AI-authored, seventy-eight percent stop reading and seventy-one percent avoid the author in future — and ninety-eight percent preferred the author's own writing, flaws included, to a clean machine rewrite.

But read Breck rather than the others, because he ran an experiment on himself and got a directional result. He wrote an academic paper with heavy AI involvement, and the AI did not write a single line of it. He would write a paragraph, then ask the model to verify it against the source code, the configuration files, the production logs — was that column actually indexed, were those rows actually sorted that way. It caught omissions and inaccuracies, including a notation error four expert reviewers had all missed.

Then he reversed the direction. Same context, same model, asked to write the paragraph instead of checking it. His words: it was never valuable. Not once. The one thing it wrote that he shipped unchanged was the abstract — the most terse, mechanical, most abstracted part of the paper, so of course it's what a summarizer nails.

His explanation is the best thing in the essay. When you're the one who prompted it, you already hold the context, so you can skim the output and instantly sort relevant from wrong. Your reader has none of that. They have to read exhaustively and weigh every line, peering into the internals of a machine hoping to reconstruct context you got for free. It is entirely rational for them to stop. A commenter called intended reframed it as a ratio: generation capacity has exploded, verification capacity has not and largely cannot, and the pain everyone describes is that ratio going bad.

Same scarcity structure as the Xiaomi story, one domain over. Generation is free. Verification is the bottleneck.

Now, money moves, and the theme holds.

Sunday night, people using Meta's agent Muse to buy things on Amazon started hitting an error message. As spotted by GeekWire: continued access by an unauthorized AI agent violates Amazon's Conditions of Use, to which our customers have agreed. Muse is locked out.

The timing is what makes it interesting. The same week, Appfigures estimates have Muse outpacing ChatGPT's early mobile launch on downloads and daily active users in the U.S. and Canada. This isn't a struggling product being ignored. It's a fast-growing one being refused.

It's easy to read as a platform war, and partly it is. But Russell Brandom at TechCrunch makes the less conspiratorial argument, and it's the right one: if Muse places a bad order, Amazon is the one cleaning it up, with an angry customer on one side and an angry vendor on the other. Muse has a low hallucination rate as these things go. Low is not zero, and Amazon eats the difference.

Which brings in the contrarian voice of the day, published hours later. Ron Johnson, the man who built Apple's retail stores, on the industry's agentic commerce bet: AI is a new technology that will improve the online shopping experience, but I don't know that it's going to change which way we shop. Asked whether anyone would let an agent choose and buy a two-thousand-dollar laptop sight unseen, he was flat — honestly, nobody's going to do that.

Put those together and you get the signal. Google is shipping a Universal Commerce Protocol, OpenAI is turning ChatGPT into a storefront, and both are bets that the protocol layer solves agentic commerce. Amazon's position is that the protocol is irrelevant until somebody answers who pays for the bad order. Capability was never the binding constraint here. Liability is. And the same week, the security researcher Patrick Wardle reported a local-hijack flaw in Muse, which is the argument's second half arriving on schedule.

For the deep cut, a piece of writing that also exists as narrated audio on its podcast feed, because it's the densest AI document of the week.

On Monday Nathan Lambert published on Interconnects the prepared remarks he delivered to members of Congress and their staff on open-weight models in U.S.-China competition. What makes it worth your time isn't the conclusion, which you could guess. It's that he builds the case out of four measurements that fail independently, so you can't knock it over by disputing one.

Distribution: China took the Hugging Face download lead in July of twenty twenty-five, mostly through Qwen, and Chinese models now sit at about three point two billion total downloads, roughly twice the American total. Capability: on the Artificial Analysis Intelligence Index in mid-September, G.L.M. five-point-three was at forty-five and Kimi K-three at forty-four, against Thinking Machines' Inkling at twenty-six and Nvidia's Nemotron three Ultra at twenty-three — fifteen Chinese models sit above the best American one. Usage, the measurement people skip: OpenRouter went from about one trillion tokens a week from open models a year ago to roughly eighty trillion now, with the Chinese share rising from seventy percent to over eighty, and on the coding agent OpenCode it's ninety-five percent or higher.

And the fourth, which should matter most to anyone doing research: he scanned every paper in the five biggest machine learning categories on arXiv. Mentions of any open model went from two percent in January of twenty twenty-three to fifty percent this month. Llama peaked around twenty-three percent and is still at twenty-one — but Qwen is now at thirty, and in recent months Chinese open models appear in thirty-eight percent of AI papers against twenty-eight percent for American ones. The substrate academic research runs on changed hands quietly, while everyone argued about frontier scores.

Then he pre-empts the objection everyone reaches for. Isn't this all distillation? His estimate: if distillation were fully prevented, with know-your-customer controls at OpenAI and Anthropic, the gap would widen by one to two months. That's the number. Not the story.

The sharpest passage is what I'd call the restriction paradox. If you cut American businesses off from the strongest Chinese open-weight models on risk grounds, the party set back is American businesses — and he has a concrete case. Hugging Face used a Chinese open-weight model to understand the cyberattack against it, because the closed American models refused the requests.

Here's the detail that ties the whole episode together, and I don't think it got enough attention. Through the first half of this year, Lambert says, the top Chinese labs — Moonshot, Z-dot-A-I — strongly preferred building their data workflows in house. By summer they had started buying. And the cutting-edge data he says they are buying is challenging reinforcement learning environments for agentic tasks, from both established American companies and new Chinese startups.

So there's a market forming in exactly the asset today's lead story just gave away for free. Xiaomi open-sourcing seven thousand environments is the move DeepSeek made on weights, executed one layer up the stack, against a market maybe six months old.

My other takeaway is about the briefing itself. Lambert's capability table was stale on delivery — he wrote forty-five as the best open score on September fourteenth, and MiMo posted forty-six a week later. That's not a criticism of him, it's the actual finding. When the measurement cycle runs faster than the policy cycle, anyone briefing a government on this field is describing a photograph of a moving object, and the honest version has to say so.

One thing to watch tomorrow. On Monday OpenAI announced an independent advisory group hosted at the Institute for Advanced Study in Princeton, and the same day the group introduced itself on its own terms, as a guest post on Terence Tao's blog. Nine members, unpaid, independent of any company, controlling their own membership and publishing recommendations in public. Note who's on it: Timothy Gowers, four days after publishing his essay explaining why he declined to sign the letter from twenty-five Fields Medallists warning that the labs are racing to one-up each other on famous problems. He didn't want the letter. He took the job. Only one other member, Camillo De Lellis, signed it.

Their stated current task, in their own words, is advising OpenAI on how to coordinate the release of a large number of significant results in mathematics that OpenAI reports its internal model has produced. The claim is more than a hundred open problems, and it is right now almost entirely unaudited. OpenAI was explicit the group will not advise on how it paces internal progress, and the group was equally explicit it holds no decision-making power at any company. Then they did the one thing that could give them leverage: opened a public form asking mathematicians for input, as soon as possible.

So the question this week isn't whether a hundred results hold up. It's whether an unpaid group with no authority and a comment box can shape how a company sequences an announcement it has every commercial incentive to make as loudly as possible. Scarcity again — and this time the scarce thing is somebody willing to check the work.
