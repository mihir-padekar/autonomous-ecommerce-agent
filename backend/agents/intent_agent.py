FOLLOWUP_WORDS = [

    "summarize",
    "summary",

    "why",
    "explain",

    "recommend",
    "recommendation",

    "what should",

    "tell me more",

    "insights",

    "next steps",

    "action items",

    "management do"
]


def intent_agent(query, history):

    query = query.lower()

    for word in FOLLOWUP_WORDS:

        if word in query:

            return {
                "intent": "followup"
            }

    return {
        "intent": "new_analysis"
    }