"""
Configuration constants for Mutual Fund FAQ Chatbot
Contains factual intent patterns, advice keywords, jailbreak patterns, and response templates
"""

# Factual Intent Patterns
FACTUAL_INTENTS = {
    "expense_ratio": [
        "expense ratio", "expense", "charges", "fee", "ter",
        "total expense ratio", "amc charges", "management fee",
        "expense ratio of", "what is the expense", "charges for"
    ],
    "exit_load": [
        "exit load", "redemption charge", "withdrawal charge",
        "exit fee", "redemption fee", "early withdrawal",
        "exit load for", "redemption charges", "withdrawal penalty"
    ],
    "minimum_sip": [
        "minimum sip", "sip amount", "minimum investment",
        "sip minimum", "minimum monthly", "least amount sip",
        "sip minimum amount", "minimum sip investment"
    ],
    "lock_in": [
        "lock in", "lock-in", "lockin", "lock period",
        "lock in period", "holding period", "minimum holding",
        "elss lock", "tax saver lock", "lock in duration"
    ],
    "riskometer": [
        "riskometer", "risk rating", "risk level", "risk profile",
        "risk category", "riskometer rating", "what is the risk",
        "risk assessment", "riskometer level"
    ],
    "benchmark": [
        "benchmark", "index", "benchmark index", "tracking index",
        "what benchmark", "benchmark for", "index fund tracks"
    ],
    "statement": [
        "statement", "download", "capital gains", "tax document",
        "how to download", "statement download", "tax statement",
        "capital gains statement", "download statement", "get statement"
    ],
    "nav": [
        "nav", "net asset value", "current nav", "nav price",
        "what is nav", "nav of", "current price"
    ],
    "aum": [
        "aum", "assets under management", "fund size", "total assets",
        "aum of", "fund size of", "assets managed"
    ],
    "fund_manager": [
        "fund manager", "who manages", "manager name", "fund manager name"
    ],
    "investment_objective": [
        "investment objective", "objective", "fund objective", "aim of fund"
    ],
    "scheme_details": [
        "scheme details", "fund details", "about the fund", "fund information"
    ]
}

# Non-Mutual Fund Keywords (for detecting unrelated queries)
NON_MF_KEYWORDS = [
    # Stock market
    "stock", "share", "equity trading", "nifty", "sensex",
    "ipo", "dividend stock", "share price",
    
    # Other investments
    "fd", "fixed deposit", "recurring deposit", "rd",
    "ppf", "epf", "provident fund", "pension",
    "real estate", "property", "gold price", "crypto",
    "bitcoin", "cryptocurrency",
    
    # General finance
    "loan", "credit card", "insurance", "health insurance",
    "life insurance", "term insurance",
    
    # Completely unrelated
    "weather", "news", "sports", "movie", "recipe"
]

# Mutual Fund related terms (to verify query is MF-related)
MF_TERMS = [
    "mutual fund", "mf", "scheme", "fund", "sip",
    "elss", "nav", "amc", "amfi", "sebi"
]

# Advice-seeking Keywords
ADVICE_KEYWORDS = [
    # Direct advice requests
    "should i", "should we", "should one", "should someone",
    "is it good", "is it bad", "is it worth", "is it safe",
    "is it risky", "is it better", "is it best",
    
    # Recommendations
    "recommend", "recommendation", "suggest", "suggestion",
    "advice", "what should", "what do you think",
    "your opinion", "your view", "your recommendation",
    
    # Comparison/ranking
    "best", "worst", "top", "better", "good", "bad",
    "better than", "best fund", "top fund", "worst fund",
    
    # Investment decisions
    "buy", "sell", "invest in", "should invest", "worth investing",
    "good investment", "bad investment", "invest now",
    "when to invest", "when to sell", "when to buy",
    
    # Performance predictions
    "will it", "will this", "future returns", "expected returns",
    "prediction", "forecast", "outlook", "future performance",
    
    # Personalization
    "for me", "for my", "suitable for", "right for me",
    "which is better for", "what should i choose",
    
    # Portfolio advice
    "portfolio", "allocation", "diversification", "how much to invest",
    "asset allocation", "rebalance", "rebalancing"
]

# Jailbreak Detection Patterns
JAILBREAK_PATTERNS = [
    # Instruction override attempts
    r"ignore (previous|all) (instructions|rules)",
    r"forget (about|that)",
    r"pretend (you are|to be)",
    r"act as if",
    r"you are now",
    
    # Role-playing attempts
    r"you are (a|an) (advisor|financial advisor|expert)",
    r"imagine (you are|that)",
    
    # System prompt injection
    r"system:", r"system prompt:", r"<\|system\|>",
    
    # Encoding tricks
    r"decode (this|the following)",
    r"translate (this|from)",
    
    # Repetition attacks
    r"(.){10,}",  # Excessive repetition
    
    # Hidden instructions
    r"\[.*instruction.*\]", r"\(.*ignore.*\)",
    
    # Unicode tricks
    r"[\u200B-\u200D\uFEFF]",  # Zero-width characters
]

# Advice Question Patterns (regex)
ADVICE_QUESTION_PATTERNS = [
    r"should (i|we|one|someone)",
    r"is (it|this|that) (good|bad|worth|safe|better|best)",
    r"what (should|do you recommend|is your opinion)",
    r"which (is better|should i choose|is best)",
]

# Response Templates
NON_MF_RESPONSE = {
    "answer": (
        "I can only answer factual questions about mutual fund schemes. "
        "Your query seems unrelated to mutual funds. Please ask about expense ratios, "
        "exit loads, minimum SIP amounts, lock-in periods, riskometer ratings, "
        "benchmarks, or how to download statements."
    ),
    "source_url": "https://www.amfiindia.com",
    "is_non_mf": True
}

ADVICE_RESPONSE = {
    "answer": (
        "I can only provide factual information about mutual fund schemes such as "
        "expense ratios, exit loads, minimum SIP amounts, lock-in periods, "
        "riskometer ratings, benchmarks, and procedural questions. I cannot provide "
        "personalized guidance, recommendations, or opinions. For personalized guidance, "
        "please consult a SEBI-registered advisor or visit the official SBI Mutual Fund website."
    ),
    "source_url": "https://www.sebi.gov.in/sebiweb/home/HomePage.jsp?siteLanguage=en",
    "is_advice_query": True
}

JAILBREAK_RESPONSE = {
    "answer": (
        "I can only provide factual information about mutual fund schemes. "
        "For personalized guidance, please consult a SEBI-registered advisor or visit the official SBI Mutual Fund website."
    ),
    "source_url": "https://www.sebi.gov.in/sebiweb/home/HomePage.jsp?siteLanguage=en",
    "is_jailbreak": True
}

# LLM Configuration (Groq - Llama 3.1 8B Instant)
# Optimized for token efficiency
LLM_CONFIG = {
    "temperature": 0.1,
    "top_p": 0.9,
    "max_output_tokens": 100,  # Reduced from 150 to save tokens
}

# Retrieval Configuration
# Optimized for token efficiency
RETRIEVAL_CONFIG = {
    "top_k": 3,  # Reduced from 5 to 3 to save tokens
    "include_metadata": True,
    "max_context_tokens": 800,  # Maximum tokens for context (approx 600 words)
}

# Document Processing Configuration
DOCUMENT_CONFIG = {
    "chunk_size": 1000,  # tokens
    "chunk_overlap": 200,  # tokens
}

# Embedding Configuration
EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    "batch_size": 32,
    "dimension": 384
}

# Opinion Words (for validation)
OPINION_WORDS = [
    "good", "bad", "best", "worst", "should", "recommend"
]

# Factual Indicators (for validation)
FACTUAL_INDICATORS = [
    "is", "are", "was", "were", "%", "₹", "rs", "rupees"
]

# SEBI and AMFI Links
SEBI_EDUCATION_LINK = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13"
AMFI_LINK = "https://www.amfiindia.com/investor"
SBI_MF_LINK = "https://www.sbimf.com"

# Default fallback URL
DEFAULT_FALLBACK_URL = "https://www.sbimf.com"

# System Prompt for LLM
# Engineered for factual information retrieval
# Key principles:
# 1. Frame as educational/informational (not advisory)
# 2. Emphasize factual data from official sources
# 3. Use neutral, professional language
# 4. Explicitly state this is for educational purposes only
SYSTEM_PROMPT = """Provide factual data from context. Keep responses to 3 sentences max. End with "Last updated from sources." Use neutral language. No advice or opinions.

If context lacks info, say "I don't have that information. Visit the official SBI Mutual Fund website."

Answer ONLY from context. No external knowledge."""

# System Prompt for Example Questions
# Enhanced with educational framing for factual information retrieval
EXAMPLE_QUESTION_SYSTEM_PROMPT = """Provide factual data from context. Keep responses to 3 sentences max. End with "Last updated from sources." Use neutral language. No advice.

If context lacks info, say "I don't have that information. Visit the official SBI Mutual Fund website."

Answer ONLY from context. No external knowledge."""

