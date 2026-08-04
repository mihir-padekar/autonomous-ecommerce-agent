import re

FOLLOWUP_WORDS = [
    "summarize",
    "summary",
    "why",
    "explain more",
    "recommend",
    "recommendation",
    "what should",
    "tell me more",
    "insights",
    "next steps",
    "action items",
    "management do"
]

GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "hii",
    "helo"
}

THANKS = {
    "thanks",
    "thank you",
    "thx",
    "ty"
}

GOODBYES = {
    "bye",
    "goodbye",
    "see you",
    "see ya"
}

HELP_WORDS = [
    "help",
    "what can you do",
    "capabilities",
    "features",
    "who are you"
]


def normalize(text: str):
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def intent_agent(query, history):

    query = normalize(query)

    if query in GREETINGS:
        return {"intent": "greeting"}

    if query in THANKS:
        return {"intent": "thanks"}

    if query in GOODBYES:
        return {"intent": "goodbye"}

    for word in HELP_WORDS:
        if word in query:
            return {"intent": "help"}

    for word in FOLLOWUP_WORDS:
        if word in query:
            return {"intent": "followup"}

    return {"intent": "workflow"}