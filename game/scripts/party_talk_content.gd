extends RefCounted

const TOPICS := [
	{
		"id": "city-liang", "participants": ["liang-xu"], "requires": ["scifi.city"],
		"zh": {"title": "两套准确的记录", "lines": [
			["hero", "两张表都没说谎，却让居民和维修员争起来了。"],
			["liang-xu", "数字只会回答它被要求回答的问题。先问清楚每张表测了什么。"],
			["hero", "那我把两边的原始记录都留着。以后有人能重新核对。"],
		]},
		"en": {"title": "Two accurate records", "lines": [
			["hero", "Neither meter lied, but the residents and crew still ended up arguing."],
			["liang-xu", "Numbers answer the question they were built to answer. Ask what each meter measures first."],
			["hero", "Then I'll keep both original records so someone else can check them."],
		]},
	},
	{
		"id": "outskirts-zhao", "participants": ["zhao-ling"], "requires": ["scifi.outskirts"],
		"zh": {"title": "较弱的好信号", "lines": [
			["zhao-ling", "B 路最不起眼，却把讯息送到了。"],
			["hero", "你之前就看出它比 A 路可靠？"],
			["zhao-ling", "我只知道它稳定。把握不大时，先选能验证的一条路。"],
		]},
		"en": {"title": "The weaker good signal", "lines": [
			["zhao-ling", "B was the least impressive channel, and the message still got through."],
			["hero", "Did you know it would beat A?"],
			["zhao-ling", "I knew it was steady. When you're unsure, choose the route you can test."],
		]},
	},
	{
		"id": "ruins-ji", "participants": ["ji-cheng"], "requires": ["scifi.ruins"],
		"zh": {"title": "留白的记录", "lines": [
			["hero", "那一处标题被擦掉了。我很想知道它原本写什么。"],
			["ji-cheng", "我也是。但替它补字，就会让猜想看起来像证据。"],
			["hero", "那就把空白也记下来。空白本身或许有用。"],
		]},
		"en": {"title": "The blank in the record", "lines": [
			["hero", "I wish I knew what the erased heading said."],
			["ji-cheng", "So do I. Filling it in would make a guess look like evidence."],
			["hero", "Then let's record the blank too. It may matter later."],
		]},
	},
	{
		"id": "city-outskirts-liang-zhao", "participants": ["liang-xu", "zhao-ling"], "requires": ["scifi.city", "scifi.outskirts"],
		"zh": {"title": "维护者的分歧", "lines": [
			["zhao-ling", "城市那条旧线和中继站的 B 路很像：不显眼，但还在干活。"],
			["liang-xu", "也容易被新报表漏掉。‘能用就不拆’需要配上一句‘仍要记清用途’。"],
			["hero", "我会把这句话写在实地日志里。它比争谁对谁错有用。"],
		]},
		"en": {"title": "A maintenance disagreement", "lines": [
			["zhao-ling", "The city's old line reminds me of channel B: easy to overlook, still doing work."],
			["liang-xu", "And easy to omit from a new report. 'Keep what works' still needs 'record what it does.'"],
			["hero", "I'll put that in the field log. It helps more than arguing over who was right."],
		]},
	},
	{
		"id": "outskirts-ruins-zhao-ji", "participants": ["zhao-ling", "ji-cheng"], "requires": ["scifi.outskirts", "scifi.ruins"],
		"zh": {"title": "相同的编号", "lines": [
			["zhao-ling", "中继系统也有‘四七’。要不要沿线追查？"],
			["ji-cheng", "可以追，但别先假设两处编号指向同一种东西。"],
			["zhao-ling", "好。我记位置，你记原文。我们先把能确认的部分合起来。"],
		]},
		"en": {"title": "A matching code", "lines": [
			["zhao-ling", "The relay uses code forty-seven too. Should we trace the line?"],
			["ji-cheng", "Yes, as long as we don't assume the codes mean the same thing."],
			["zhao-ling", "I'll mark the sites. You keep the source text. We can compare what we know."],
		]},
	},
	{
		"id": "city-ruins-liang-ji", "participants": ["liang-xu", "ji-cheng"], "requires": ["scifi.city", "scifi.ruins"],
		"zh": {"title": "标明不知道", "lines": [
			["liang-xu", "城市里有人把‘正常’写成结论，遗址机器却把模糊词译成了‘奉献’。"],
			["ji-cheng", "两处都缺少足够的依据。承认不知道，才给后来的人留下核查的空间。"],
			["hero", "我们能把疑点清楚地留下来；这也是一种进展。"],
		]},
		"en": {"title": "Marking what we don't know", "lines": [
			["liang-xu", "The city wrote 'normal' as a conclusion. A ruin machine rendered a blurred word as 'offering.'"],
			["ji-cheng", "Neither had enough support. Admitting uncertainty gives the next reader something to test."],
			["hero", "Leaving the doubts clearly marked is progress too."],
		]},
	},
]
