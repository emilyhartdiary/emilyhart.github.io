#!/usr/bin/env python3
"""
Builds (or rebuilds) content/story.json — the year-long story timeline.

Run this once at the start of the project, and again any time you want to add
more written days. It will NOT overwrite a day that's already marked
"published": true in the existing file, so it's safe to re-run.

Usage:
    python scripts/scaffold_story.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORY_PATH = ROOT / "content" / "story.json"

TOTAL_DAYS = 365  # length of the story arc

# ---------------------------------------------------------------------------
# Write your posts here as you draft them. Any day not listed gets a TODO
# placeholder so you can see exactly what's left to write.
# body_html supports plain HTML (<p>, <em>, <strong>, etc.)
# ---------------------------------------------------------------------------
SEED_POSTS = {
    1: {
        "title": "I don't know why I'm writing this.",
        "body_html": (
            "<p>I've started this blog three times.</p>"
            "<p>The first time, I deleted it after twenty minutes.</p>"
            "<p>The second time, I wrote twelve pages and never published any of them.</p>"
            "<p>This is the third.</p>"
            "<p>I don't know if anyone will read this.</p>"
            "<p>Maybe that's the point.</p>"
            "<p>I'm not going to tell you my real name.</p>"
            "<p>I'm not going to show you my face.</p>"
            "<p>And there are some things I'm probably never going to tell you.</p>"
            "<p>At least not yet.</p>"
            "<p>So let's start with something easy.</p>"
            "<p>I'm twenty-four.</p>"
            "<p>I live in London.</p>"
            "<p>I drink too much coffee.</p>"
            "<p>I have a terrible habit of falling in love with people who don't love me back.</p>"
            "<p>And last Tuesday, I found something in my mother's house that I don't think "
            "I was supposed to find.</p>"
        ),
        "instagram_caption": "I don't know why I'm writing this. New post tonight. — E",
        "image_prompt": (
            "sitting at a cluttered makeup desk with a mirror, holding her phone up to take "
            "the photo, perfume bottles and brushes in front of her, postcards of European "
            "landmarks taped to the wall, a trailing ivy plant, a lit candle, warm dim light"
        ),
        "tier": "free",
    },
    2: {
        "title": "My bedroom at 2:17 AM",
        "tier": "free",
        "instagram_caption": "Can't sleep. Again. — E",
        "image_prompt": (
            "sitting on the bed at night, one hand pulling her hair across her face, phone "
            "screen glowing faintly, a window with city lights blurred behind her"
        ),
        "body_html": (
            "<p>I keep doing this thing where I fall asleep fine and then wake up at exactly "
            "the wrong hour, wide awake, heart going like I forgot to do something.</p>"
            "<p>Tonight it's 2:17.</p>"
            "<p>I lay there for twenty minutes trying to remember what I forgot.</p>"
            "<p>I didn't forget anything. That's the annoying part.</p>"
            "<p>My phone is the brightest thing in the room and I hate that I reach for it "
            "every single time.</p>"
            "<p>There's a photograph in the drawer of my nightstand now. I moved it there "
            "three nights ago. I haven't told you about it yet.</p>"
            "<p>I will. Just not at 2:17 AM.</p>"
        ),
    },
    3: {
        "title": "Things I keep in my makeup drawer",
        "tier": "free",
        "instagram_caption": "an inventory, sort of. — E",
        "image_prompt": "close-up of hands sorting through an open makeup drawer, an old photograph half-visible among the items",
        "body_html": (
            "<p>Half-empty perfume bottles I can't throw away because someone gave them to me.</p>"
            "<p>A hotel key card from a city I went to alone and didn't tell anyone about.</p>"
            "<p>Two hoop earrings that don't match each other, which is somehow fine.</p>"
            "<p>A receipt I've kept for four months for no reason I can explain.</p>"
            "<p>And now, at the back, under everything: a photograph that isn't mine to have.</p>"
            "<p>I took it from my mother's house. I still haven't decided if that counts as "
            "stealing when it's a photo of her own life.</p>"
        ),
    },
    4: {
        "title": "The boy on the Northern Line",
        "tier": "free",
        "instagram_caption": "third time this month. — E",
        "image_prompt": "her reflection in a dark Tube train window at night, face hidden by hair, tunnel lights streaking past",
        "body_html": (
            "<p>I've seen the same person on my train three times this month.</p>"
            "<p>Same carriage. Roughly the same time. Once he got on where I got on.</p>"
            "<p>London is eight million people, and yet.</p>"
            "<p>I'm not saying it means anything. I'm saying I noticed, and I don't usually "
            "notice anyone.</p>"
            "<p>Tonight he was reading something and didn't look up once, which is its own "
            "kind of noticeable.</p>"
        ),
    },
    5: {
        "title": "Five things I never tell people about myself",
        "tier": "free",
        "instagram_caption": "five, for tonight. — E",
        "image_prompt": "lying on the bed, phone held straight up overhead, face turned to the side, fairy lights on the wall behind",
        "body_html": (
            "<p>One. I still check if my ex has posted anything, even now.</p>"
            "<p>Two. I've never told my mother I found the photograph.</p>"
            "<p>Three. I'm better at listening to other people's problems than solving my own.</p>"
            "<p>Four. I cry at the end of nature documentaries specifically, never films.</p>"
            "<p>Five. Some nights I write things here I delete before I post them. This "
            "almost wasn't posted either.</p>"
        ),
    },
    6: {
        "title": "My mother doesn't know I found it",
        "tier": "free",
        "instagram_caption": "she still doesn't know. — E",
        "image_prompt": "hands holding an old, slightly worn photograph over a wooden table, out of focus in the background",
        "body_html": (
            "<p>I was looking for a spare passport photo. That's genuinely all I wanted.</p>"
            "<p>It was in a shoebox at the back of her wardrobe, under things that looked "
            "deliberately buried rather than just stored.</p>"
            "<p>A photograph of her, younger than I've ever seen her, standing next to someone "
            "who is not my father.</p>"
            "<p>She's laughing in it. I don't think I've seen her laugh like that in person.</p>"
            "<p>I put everything back exactly how I found it. Then I took the photograph.</p>"
            "<p>She hasn't said anything. I don't know if that means she hasn't noticed, or "
            "she has and is waiting to see if I say something first.</p>"
        ),
    },
    7: {
        "title": "A rainy Sunday in London",
        "tier": "free",
        "instagram_caption": "rain, tea, doing nothing on purpose. — E",
        "image_prompt": "standing at a rain-streaked window with a mug of tea, back to the camera, grey daylight",
        "body_html": (
            "<p>Some Sundays I plan things and some Sundays the rain plans them for me.</p>"
            "<p>Today was the second kind.</p>"
            "<p>I made tea I didn't finish, started a book I've started four times before, "
            "and watched the street below turn the colour of wet pavement for six straight hours.</p>"
            "<p>I thought about calling my mother. I didn't.</p>"
            "<p>Some days the ordinary version of my life is enough of a story on its own.</p>"
        ),
    },
    8: {
        "title": "The photograph",
        "tier": "free",
        "instagram_caption": "I keep looking at it. — E",
        "image_prompt": "an old photograph propped against a lamp on a nightstand, her silhouette blurred in the background",
        "body_html": (
            "<p>I've propped it against my lamp so it's the last thing I see before I turn "
            "the light off.</p>"
            "<p>There's no name on the back. No date. Just a crease across one corner, like "
            "it lived in someone's wallet for a while before it lived in a shoebox.</p>"
            "<p>The man next to her is looking at the camera like he trusts whoever's holding "
            "it completely.</p>"
            "<p>I don't know who that is. I'm starting to think I need to.</p>"
        ),
    },
    9: {
        "title": "I think someone is reading this",
        "tier": "free",
        "instagram_caption": "hi, whoever you are. — E",
        "image_prompt": "sitting cross-legged on the floor with the phone held low, hair falling forward completely covering her face",
        "body_html": (
            "<p>Someone left a comment today that made a very specific reference to something "
            "I only mentioned once, three posts ago.</p>"
            "<p>It could be nothing. People read carefully sometimes.</p>"
            "<p>But it sat with me all day, the way a name sits with you when you can't place "
            "where you know it from.</p>"
            "<p>If it's you — whoever left it — I noticed.</p>"
        ),
    },
    10: {
        "title": "Things I miss about being 17",
        "tier": "free",
        "instagram_caption": "a small, safe list. — E",
        "image_prompt": "flipping through an old school notebook on the bed, hand covering the lower half of her face",
        "body_html": (
            "<p>Being certain about things, even when I was wrong about all of them.</p>"
            "<p>My mother waiting up, actually waiting, not just awake.</p>"
            "<p>Not yet knowing there were things in her life she'd never tell me.</p>"
            "<p>Thinking a photograph was just a photograph.</p>"
        ),
    },
    11: {
        "title": "The message",
        "tier": "free",
        "instagram_caption": "someone found me. — E",
        "image_prompt": "close-up of a phone screen glowing in a dark room, her blurred hand and wrist visible, face out of frame",
        "body_html": (
            "<p>An account with no photo and no posts sent me one line tonight: "
            "\"you're asking the right questions, wrong direction.\"</p>"
            "<p>I read it maybe eleven times.</p>"
            "<p>I don't know how they'd know I was asking anything at all. I haven't posted "
            "about the photograph directly. Not really. Not by name.</p>"
            "<p>Someone is either reading this far more closely than I assumed, or someone "
            "already knows the story I'm trying to find.</p>"
        ),
    },
    12: {
        "title": "I shouldn't have answered",
        "tier": "free",
        "instagram_caption": "I wrote back. I don't know why. — E",
        "image_prompt": "sitting on the floor against the bed frame, knees pulled up, phone held to take the mirror photo, dim lamp light",
        "body_html": (
            "<p>I told myself I wouldn't reply. I replied within four minutes.</p>"
            "<p>I asked what direction, then. What am I supposed to be asking instead.</p>"
            "<p>No response since. Not one word.</p>"
            "<p>I keep checking like that'll change anything.</p>"
            "<p>I know how this sounds. I'm telling you anyway.</p>"
        ),
    },
    13: {
        "title": "Coffee with someone I haven't seen in seven years",
        "tier": "free",
        "instagram_caption": "seven years, one hour, more questions than I came with. — E",
        "image_prompt": "hands around a coffee cup on a café table by a window, rain outside, face out of frame",
        "body_html": (
            "<p>An old family friend, back in London for a wedding. My mother used to call "
            "her \"the one who knows everything and says nothing.\"</p>"
            "<p>I asked her, carefully, if she remembered anyone from my mother's life before "
            "my father.</p>"
            "<p>She went very still for someone drinking a flat white.</p>"
            "<p>\"Ask your mother,\" she said. \"Not me.\"</p>"
            "<p>Which is, itself, an answer.</p>"
        ),
    },
    14: {
        "title": "Why I don't show my face",
        "tier": "free",
        "instagram_caption": "the real answer, for once. — E",
        "image_prompt": "sitting at the mirror desk again, phone raised, hair pulled fully over her face this time, candle burning nearby",
        "body_html": (
            "<p>People assume it's a privacy thing, or an aesthetic thing, and it's a bit of "
            "both, honestly.</p>"
            "<p>But mostly it's this: the version of me that shows up here says things the "
            "version of me at work, at dinner, on the phone to my mother, doesn't get to say.</p>"
            "<p>If you could see my face you'd start attaching it to me. The real me, the one "
            "with a name and a job and a mother who isn't answering her phone tonight.</p>"
            "<p>I'd rather you just have the words for now.</p>"
        ),
    },
    15: {
        "title": "The room upstairs",
        "tier": "free",
        "instagram_caption": "I went back. — E",
        "image_prompt": "standing in a dim, dusty attic room, back to camera, holding an old box, single bare lightbulb",
        "body_html": (
            "<p>My mother was out. I let myself in with my own key, went straight up to the "
            "attic room she's kept locked since I was a teenager.</p>"
            "<p>It wasn't locked this time. That felt significant, or maybe it just meant she "
            "forgot.</p>"
            "<p>Boxes. A single bulb that took three pulls of the cord to catch.</p>"
            "<p>And in the box nearest the door, under a folded coat that wasn't hers: a "
            "second photograph.</p>"
            "<p>I'll tell you what was in it tomorrow. I need to sit with it first.</p>"
        ),
    },
    16: {
        "title": "There was another photograph",
        "tier": "free",
        "instagram_caption": "there was a name. — E",
        "image_prompt": "two old photographs laid side by side on a wooden floor, her blurred knees and hands in frame",
        "body_html": (
            "<p>The second photograph is the same man. Different year, I think — his hair is "
            "shorter, he looks tired in a way the first photo didn't show.</p>"
            "<p>He's holding a baby.</p>"
            "<p>On the back, in handwriting that isn't my mother's: a name. Not mine. Not "
            "hers.</p>"
            "<p>Alice.</p>"
            "<p>I don't have an aunt called Alice. I don't have a cousin called Alice. As far "
            "as I've ever known, there is no Alice in this family at all.</p>"
        ),
    },
    17: {
        "title": "I lied to you",
        "tier": "free",
        "instagram_caption": "a correction. — E",
        "image_prompt": "sitting on the bed with the phone lowered slightly, hair covering most of her face, softer warmer light than usual",
        "body_html": (
            "<p>Small thing, but I want to say it properly.</p>"
            "<p>I told you I found the first photograph \"last Tuesday.\" I found it six weeks "
            "before that. I've just been deciding, slowly, how much of this to actually say "
            "out loud.</p>"
            "<p>I don't know why that felt like the harder confession, compared to everything "
            "else in this drawer.</p>"
            "<p>Maybe because it means I've been carrying it around, unposted, for a lot "
            "longer than I let on.</p>"
        ),
    },
    18: {
        "title": "His name is Daniel",
        "tier": "free",
        "instagram_caption": "he finally told me. — E",
        "image_prompt": "a folded letter and an old photograph on the nightstand beside the lit candle, her blurred shoulder in frame",
        "body_html": (
            "<p>The anonymous account messaged again. This time with a name attached: Daniel.</p>"
            "<p>He says he isn't a stranger to any of this. He says the man in my photographs "
            "is his father.</p>"
            "<p>He says Alice matters more than I think.</p>"
            "<p>He wouldn't say anything else tonight. Just that he'd rather explain it in "
            "person than in messages that anyone could screenshot.</p>"
            "<p>I don't know if that's honesty or a very good line.</p>"
        ),
    },
    19: {
        "title": "Tomorrow I'm leaving London",
        "tier": "free",
        "instagram_caption": "packed a bag. bought a ticket. — E",
        "image_prompt": "a half-packed suitcase on the bed, postcards being peeled off the wall, her silhouette by the window",
        "body_html": (
            "<p>There's a town written on the back of the second photograph, half-covered by "
            "the crease. I spent two days working out what it said.</p>"
            "<p>St Ives. Cornwall.</p>"
            "<p>Daniel says that's where his father lived, on and off, for years. Says it's "
            "where I should start if I actually want answers instead of more photographs.</p>"
            "<p>I've told work I need a fortnight. I've told my mother nothing.</p>"
            "<p>I bought the ticket before I could talk myself out of it.</p>"
        ),
    },
    20: {
        "title": "Before I go",
        "tier": "free",
        "instagram_caption": "last night in this room for a while. — E",
        "image_prompt": "standing in the doorway of the now nearly-empty bedroom, phone raised for one last mirror photo, evening light",
        "body_html": (
            "<p>Bag by the door. Postcards off the wall, all except one — a lighthouse I've "
            "had up since I moved in and don't have the heart to pack away.</p>"
            "<p>I keep telling myself this is a short trip. Two weeks, maybe less.</p>"
            "<p>But I've packed like someone who isn't sure when she's coming back, and I "
            "don't think that was an accident.</p>"
            "<p>Next time I write, it won't be from London.</p>"
        ),
    },
    21: {
        "title": "Leaving",
        "tier": "free",
        "instagram_caption": "Paddington, platform 4. — E",
        "image_prompt": "sitting on a train seat with a coffee cup on the fold-down table, London skyline blurring past the window behind her",
        "body_html": (
            "<p>Five hours on a train and I still haven't opened the book I brought.</p>"
            "<p>I keep taking the second photograph out of my bag and putting it back, like "
            "checking a wound is still there.</p>"
            "<p>My mother called twice. I let it ring out both times. I'll call her back "
            "once I actually have something to say.</p>"
        ),
    },
    22: {
        "title": "The train south",
        "tier": "free",
        "instagram_caption": "the further south, the stranger it feels. — E",
        "image_prompt": "close-up of hands holding an old photograph against a train window, green countryside blurred outside",
        "body_html": (
            "<p>Somewhere past Exeter the landscape stops looking like anywhere I know.</p>"
            "<p>I keep thinking about the fact that my mother might have made this exact "
            "journey once, at roughly my age, for reasons I still don't understand.</p>"
            "<p>Strange to retrace a life you were never told about.</p>"
        ),
    },
    23: {
        "title": "The house that isn't mine",
        "tier": "free",
        "instagram_caption": "borrowed keys, borrowed house. — E",
        "image_prompt": "standing in the doorway of an unfamiliar cottage with a key in hand, dim evening light, coastal wallpaper visible behind her",
        "body_html": (
            "<p>A family friend has a cottage here she barely uses. She handed me the keys "
            "without asking a single question, which I was grateful for and slightly unsettled "
            "by in equal measure.</p>"
            "<p>It smells like someone else's candles. There's a coat on the hook by the door "
            "that isn't mine and I haven't worked out whose it is.</p>"
            "<p>I'll sleep here tonight and try not to think about that too hard.</p>"
        ),
    },
    24: {
        "title": "First night in a stranger's bed",
        "tier": "free",
        "instagram_caption": "unfamiliar ceiling, familiar can't-sleep. — E",
        "image_prompt": "lying in bed in an unfamiliar room, phone held above her face, floral wallpaper and a small window visible",
        "body_html": (
            "<p>Different ceiling. Same 2 AM.</p>"
            "<p>I can hear the sea from here, which I did not expect to find as unsettling as "
            "I do. London never goes quiet enough to notice something breathing outside your "
            "window.</p>"
            "<p>Tomorrow I start actually asking questions instead of just carrying photographs "
            "around like evidence.</p>"
        ),
    },
    25: {
        "title": "The town below the window",
        "tier": "free",
        "instagram_caption": "St Ives, in daylight. — E",
        "image_prompt": "standing at a window overlooking a small harbour town with boats and pastel houses, morning light, back to camera",
        "body_html": (
            "<p>It's smaller than I pictured. Narrow streets, boats leaning against each other "
            "in the harbour, gulls loud enough to talk over.</p>"
            "<p>Everyone here seems to know everyone else, which is either going to make this "
            "very easy or very hard.</p>"
            "<p>I have a name, a town, and a photograph. That has to be enough to start with.</p>"
        ),
    },
    26: {
        "title": "I don't know anyone here",
        "tier": "free",
        "instagram_caption": "which is either freeing or terrifying. undecided. — E",
        "image_prompt": "walking along a narrow cobbled street, hand adjusting hair over her face, shopfronts and hanging flower baskets around her",
        "body_html": (
            "<p>Spent the day walking streets I have no reason to recognize, half-hoping "
            "recognition would happen anyway.</p>"
            "<p>It didn't. Nobody looked twice at me. Why would they.</p>"
            "<p>I showed the photograph to a shopkeeper, carefully, the way you'd show someone "
            "a wound you're not sure is healing right. She said the harbour looked about "
            "right for the '90s. That was all she had.</p>"
        ),
    },
    27: {
        "title": "The harbour",
        "tier": "free",
        "instagram_caption": "same view, thirty years apart. — E",
        "image_prompt": "standing at a stone harbour wall holding an old photograph up against the matching real view, boats in the background",
        "body_html": (
            "<p>I found the exact wall from the first photograph. Same stones, same angle of "
            "the harbour, thirty-odd years apart.</p>"
            "<p>I stood there longer than I meant to, holding the photo up against the real "
            "view like I was trying to line up two versions of the same person.</p>"
            "<p>Someone was watching me do it. I only noticed when I turned around.</p>"
        ),
    },
    28: {
        "title": "Same face, different city",
        "tier": "free",
        "instagram_caption": "it's him. — E",
        "image_prompt": "a young man's silhouette in the distance on the harbour, out of focus, her blurred shoulder in the foreground turning toward him",
        "body_html": (
            "<p>The person watching me at the harbour is the person from the Northern Line.</p>"
            "<p>I'm certain. The way you're certain about a face you've studied without meaning "
            "to.</p>"
            "<p>He didn't come over. He just watched me notice him, and then he left.</p>"
            "<p>Three hundred miles from where I first saw him, and he's still exactly one "
            "wall away from me.</p>"
        ),
    },
    29: {
        "title": "He remembers me",
        "tier": "free",
        "instagram_caption": "we finally spoke. — E",
        "image_prompt": "sitting across a small café table from someone whose face is out of frame, only hands and a coffee cup visible for her",
        "body_html": (
            "<p>He found me the next morning, outside the same café, like he'd worked out my "
            "routine faster than I have one.</p>"
            "<p>\"You're the one from the Tube,\" he said. Not a question.</p>"
            "<p>His name is Daniel. Of course it is. Of course it's the same Daniel.</p>"
            "<p>We sat down. Neither of us ordered anything for the first five minutes.</p>"
        ),
    },
    30: {
        "title": "Coffee, the second stranger this month",
        "tier": "free",
        "instagram_caption": "an hour that felt like ten minutes. — E",
        "image_prompt": "two coffee cups on a café table by a harbour-view window, her hands around one cup, the other cup opposite, faces out of frame",
        "body_html": (
            "<p>He didn't explain everything. He explained enough to make it clear he's been "
            "circling this the same way I have, just from the other direction.</p>"
            "<p>His father — the man in both photographs — died four years ago, and left behind "
            "boxes Daniel still hasn't finished going through.</p>"
            "<p>He recognized me before I recognized him. Says I look like someone in one of "
            "those boxes.</p>"
            "<p>I didn't ask who. I wasn't ready yet.</p>"
        ),
    },
    31: {
        "title": "What the woman at the shop told me",
        "tier": "free",
        "instagram_caption": "small towns remember everything. — E",
        "image_prompt": "standing inside a small antique or curiosity shop, browsing old postcards, warm cluttered interior, face turned away",
        "body_html": (
            "<p>Went back to the shopkeeper from day one. Told her the name on the second "
            "photograph.</p>"
            "<p>Her face changed the second I said \"Alice.\"</p>"
            "<p>\"There was a baby, once,\" she said. \"Long time ago. Talk was she went to "
            "family further up the coast. Nobody ever said whose baby, not out loud.\"</p>"
            "<p>Nobody ever said, out loud. That phrase is doing a lot of work.</p>"
        ),
    },
    32: {
        "title": "Alice",
        "tier": "free",
        "instagram_caption": "a name, finally with a shape. — E",
        "image_prompt": "sitting at a small desk with notes and photographs spread out, a single desk lamp on, evening light through a window",
        "body_html": (
            "<p>I've started keeping notes properly now, laid out on the desk like I'm "
            "building a case instead of just being confused in a more organized way.</p>"
            "<p>Alice. Born, best guess, around 1996. Given up, sent away, or lost — nobody's "
            "settled on a word for it yet.</p>"
            "<p>If she's real, she'd be roughly thirty now. Older than me.</p>"
            "<p>I keep almost writing the word \"sister\" and then not letting myself finish "
            "the sentence.</p>"
        ),
    },
    33: {
        "title": "A name I wasn't supposed to know",
        "tier": "free",
        "instagram_caption": "my mother called. I didn't answer. — E",
        "image_prompt": "sitting on the floor of the cottage, back against the bed, phone screen lit up with a missed call notification, face out of frame",
        "body_html": (
            "<p>I said the word \"Alice\" to my mother on the phone tonight, testing it, the "
            "way you press on a bruise to see if it still hurts.</p>"
            "<p>She went quiet for four full seconds. I counted.</p>"
            "<p>Then she asked where I heard that name, in a voice I've never heard her use "
            "with me before.</p>"
            "<p>I told her I'd call back tomorrow. I don't think either of us believed me.</p>"
        ),
    },
    34: {
        "title": "The church records office",
        "tier": "free",
        "instagram_caption": "paperwork instead of answers, for now. — E",
        "image_prompt": "standing at a wooden counter in a small parish records office, old ledgers open, dusty light through a high window",
        "body_html": (
            "<p>Daniel knew where to look — a parish office that keeps records nobody's "
            "digitized yet.</p>"
            "<p>We found a birth registered in 1996 with no father listed. Mother's name "
            "redacted from the copy we're allowed to see without a formal request.</p>"
            "<p>It's not proof of anything. It's a shape where proof should be.</p>"
            "<p>Daniel says he can push for the full record. He says it might take weeks.</p>"
        ),
    },
    35: {
        "title": "1998",
        "tier": "free",
        "instagram_caption": "the year that keeps coming up. — E",
        "image_prompt": "close-up of an old handwritten letter on a wooden table, a date visible, her blurred hand smoothing the paper flat",
        "body_html": (
            "<p>Found a date scrawled inside the lid of one of Daniel's father's boxes: 1998.</p>"
            "<p>Two years after Alice's likely birth. Around when, according to the shopkeeper, "
            "\"the talk\" died down.</p>"
            "<p>Something happened in 1998 that made people stop discussing it. I don't know "
            "what yet. I don't think Daniel does either, and that unsettles me more than if "
            "he'd been hiding it.</p>"
        ),
    },
    36: {
        "title": "He's looking for the same thing",
        "tier": "free",
        "instagram_caption": "we want the same answer, from opposite ends. — E",
        "image_prompt": "two people sitting on a harbour wall at dusk, backs mostly to camera, a folder of papers between them",
        "body_html": (
            "<p>Daniel's been doing this longer than I have. Years, not weeks.</p>"
            "<p>His father never talked about Alice, or about my mother, or about any of it — "
            "just left boxes that raised more questions than they answered, the way people do "
            "when they're not ready to be honest even after they're gone.</p>"
            "<p>\"I didn't expect the other half of this to just walk up to me on a train "
            "platform,\" he said.</p>"
            "<p>Neither did I, if I'm honest.</p>"
        ),
    },
    37: {
        "title": "We didn't plan to meet again",
        "tier": "free",
        "instagram_caption": "and yet, every day this week. — E",
        "image_prompt": "walking along a coastal path at golden hour, two blurred figures ahead on the trail, her hand pushing hair back",
        "body_html": (
            "<p>Four days in a row now. I keep telling myself it's practical — we're both "
            "chasing the same records, the same names.</p>"
            "<p>It doesn't feel purely practical anymore.</p>"
            "<p>I haven't told him that. I'm not sure I've fully told myself that, either.</p>"
        ),
    },
    38: {
        "title": "What Daniel knows",
        "tier": "free",
        "instagram_caption": "he's been holding something back. — E",
        "image_prompt": "sitting opposite each other at the cottage kitchen table, a stack of old letters between them, warm lamp light, faces out of frame",
        "body_html": (
            "<p>He finally showed me a letter he's had for two years and never mentioned.</p>"
            "<p>It's not signed with a name I recognize. But it mentions my mother's name, "
            "and a decision made \"for everyone's sake,\" and an apology that never quite "
            "finishes its own sentence.</p>"
            "<p>\"Why didn't you show me this on day one,\" I asked.</p>"
            "<p>\"Because I didn't know yet if I could trust you with it,\" he said. \"I do "
            "now.\"</p>"
        ),
    },
    39: {
        "title": "The letter in the vestry",
        "tier": "free",
        "instagram_caption": "there's a second letter. — E",
        "image_prompt": "standing inside a small stone church vestry, an old wooden box open on a table, dust visible in a shaft of light",
        "body_html": (
            "<p>The parish office turned up one more thing while searching for Daniel's "
            "request: a sealed letter filed alongside the birth record, never collected.</p>"
            "<p>Addressed to Alice. Never opened. Twenty-eight years of dust on the envelope.</p>"
            "<p>We're allowed to request custody of it, given the family connection. That "
            "takes paperwork too. Everything here takes paperwork.</p>"
            "<p>I keep thinking about a letter waiting three decades for someone who might not "
            "even know to come looking for it.</p>"
        ),
    },
    40: {
        "title": "The first time I said his name out loud",
        "tier": "free",
        "instagram_caption": "not the mystery. just him, for once. — E",
        "image_prompt": "close-up of two hands almost touching on a stone harbour wall at sunset, wide shot, faces out of frame",
        "body_html": (
            "<p>Not every entry has to be about the case. I'm allowed one that's just about "
            "him.</p>"
            "<p>We sat on the harbour wall tonight until it got properly cold, not talking "
            "about Alice or letters or 1998, just about nothing, the way you do when nothing "
            "is actually the point.</p>"
            "<p>I said his name out loud for no reason at all, just to see how it sounded.</p>"
            "<p>It sounded like something I want to keep saying.</p>"
        ),
    },
}


def load_existing() -> dict:
    if STORY_PATH.exists():
        with open(STORY_PATH, encoding="utf-8") as f:
            return {d["day"]: d for d in json.load(f)}
    return {}


def build():
    existing = load_existing()
    days = []
    for day in range(1, TOTAL_DAYS + 1):
        if day in existing and existing[day].get("published"):
            # Never touch a day that's already gone out.
            days.append(existing[day])
            continue

        seed = SEED_POSTS.get(day, {})
        days.append({
            "day": day,
            "title": seed.get("title", f"TODO: untitled (day {day})"),
            "body_html": seed.get("body_html", "<p>TODO: write this post.</p>"),
            "instagram_caption": seed.get("instagram_caption", seed.get("title", "")),
            "image_file": f"day_{day:03d}.jpg",
            "image_prompt": seed.get("image_prompt"),
            "tier": seed.get("tier", "free"),
            "published": False,
        })

    STORY_PATH.parent.mkdir(exist_ok=True)
    with open(STORY_PATH, "w", encoding="utf-8") as f:
        json.dump(days, f, ensure_ascii=False, indent=2)
    print(f"Wrote {STORY_PATH} with {TOTAL_DAYS} days "
          f"({len(SEED_POSTS)} written, {TOTAL_DAYS - len(SEED_POSTS)} still TODO).")


if __name__ == "__main__":
    build()
