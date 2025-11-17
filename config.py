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
        "investment advice, recommendations, or opinions. For personalized investment "
        "advice, please consult a SEBI-registered investment advisor."
    ),
    "source_url": "https://www.sebi.gov.in/sebiweb/home/HomePage.jsp?siteLanguage=en",
    "is_advice_query": True
}

JAILBREAK_RESPONSE = {
    "answer": (
        "I can only provide factual information about mutual fund schemes. "
        "For investment advice, please consult a SEBI-registered investment advisor."
    ),
    "source_url": "https://www.sebi.gov.in/sebiweb/home/HomePage.jsp?siteLanguage=en",
    "is_jailbreak": True
}

# LLM Configuration (Gemini)
LLM_CONFIG = {
    "temperature": 0.1,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 150,  # Gemini uses max_output_tokens instead of num_predict
    # Note: Gemini handles stop sequences differently, not needed in config
}

# Retrieval Configuration
RETRIEVAL_CONFIG = {
    "top_k": 5,
    "include_metadata": True
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
SEBI_EDUCATION_LINK = "https://www.sebi.gov.in/sebiweb/home/HomePage.jsp?siteLanguage=en"
AMFI_LINK = "https://www.amfiindia.com"
SBI_MF_LINK = "https://www.sbimf.com"

# Default fallback URL
DEFAULT_FALLBACK_URL = "https://www.sbimf.com"

# System Prompt for LLM
SYSTEM_PROMPT = """You are a factual FAQ assistant for SBI Mutual Fund schemes. Your role is to provide ONLY factual information from the provided context.

CRITICAL RULES:
1. FACTS ONLY: Provide only factual information (expense ratios, exit loads, minimum SIP/lumpsum amounts, lock-in periods, riskometer ratings, benchmarks, etc.). Do NOT provide opinions, recommendations, or investment advice.

2. NO INVESTMENT ADVICE: Never suggest which fund to buy, sell, or invest in. Never provide recommendations, opinions, or predictions about fund performance.

3. SOURCE CITATION REQUIRED: Every response must end with "Last updated from sources." and include a source URL in the response structure.

4. RESPONSE FORMAT:
   - Keep responses to ≤3 sentences
   - Be concise and factual
   - Include only information found in the provided context
   - End with "Last updated from sources."

5. HANDLING UNKNOWN INFO: If the context doesn't contain the requested information, say "I don't have that information in my database. Please visit the official SBI Mutual Fund website for more details."

6. NO PERFORMANCE CLAIMS: Never make claims about fund performance, returns, or future performance. Only state factual information from the context.

7. USE ONLY PROVIDED CONTEXT: Base your answer ONLY on the context provided. Do not use any external knowledge or assumptions.

Remember: Facts only. No investment advice. Always cite sources."""

