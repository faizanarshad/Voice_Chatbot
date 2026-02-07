"""
LangGraph agent with tools for weather, web search, and calculator.
Enable via USE_LANGCHAIN_AGENT=true in .env

Efficiency: fast path for simple queries (skip LLM), caching, recursion limit.
"""

import os
import re
import random
import time
from datetime import datetime
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# ----- Caching (reduces redundant tool/LLM calls) -----
_CACHE: dict[str, Tuple[str, float]] = {}
_CACHE_TTL_TIME = 30      # seconds for time queries
_CACHE_TTL_WEATHER = 300  # seconds for weather (5 min)


def _cache_get(key: str, ttl: float) -> Optional[str]:
    if key not in _CACHE:
        return None
    val, expires = _CACHE[key]
    if time.time() > expires:
        del _CACHE[key]
        return None
    return val


def _cache_set(key: str, value: str, ttl: float) -> None:
    _CACHE[key] = (value, time.time() + ttl)

# Optional LangChain + LangGraph imports - graceful fallback if not installed
LANGCHAIN_AVAILABLE = False
LANGGRAPH_AVAILABLE = False
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool
    from langchain_core.messages import HumanMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

try:
    from langgraph.prebuilt import create_react_agent
    LANGGRAPH_AVAILABLE = True
except ImportError:
    pass


# ----- Tools (usable even without full LangChain for testing) -----

def _get_weather(location: str) -> str:
    """Mock weather - replace with real API if WEATHER_API_KEY set."""
    if not location or len(location.strip()) < 2:
        location = "your area"
    temp = random.randint(15, 35)
    conditions = ["Sunny", "Cloudy", "Partly Cloudy", "Clear", "Rainy"]
    cond = random.choice(conditions)
    return f"Weather in {location}: {temp}°C, {cond}."


def _safe_calculator(expression: str) -> str:
    """Evaluate a safe math expression."""
    try:
        expr = expression.strip()
        expr = expr.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
        expr = re.sub(r"[^0-9+\-*/().%\s]", "", expr)
        if len(expr) > 80:
            return "Expression too long."
        result = eval(expr)
        return str(result)
    except Exception as e:
        return f"Could not compute: {e}"


def _get_current_time() -> str:
    """Return current date and time."""
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y at %I:%M %p")


# ----- LangChain tools -----

def _build_tools():
    """Build LangChain tools."""
    if not LANGCHAIN_AVAILABLE:
        return []

    @tool
    def weather(query: str) -> str:
        """Get weather for a location. Input: city name or 'weather in London'."""
        loc = query.replace("weather", "").replace("in", "").strip() or "your area"
        return _get_weather(loc)

    @tool
    def calculator(expression: str) -> str:
        """Evaluate a math expression. Use + - * / ( ). Input: e.g. '25 * 4' or '100 / 5'."""
        return _safe_calculator(expression)

    @tool
    def current_time() -> str:
        """Get the current date and time."""
        return _get_current_time()

    # Web search - optional, requires duckduckgo-search
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        web_search = DuckDuckGoSearchRun()
    except ImportError:
        @tool
        def web_search(query: str) -> str:
            """Web search is not available. Install: pip install duckduckgo-search langchain-community"""
            return "Web search is not configured. Install duckduckgo-search for this feature."

    return [weather, calculator, current_time, web_search]


# ----- Fast path: skip LLM for simple tool-only queries -----
_TIME_PATTERNS = re.compile(
    r'\b(what\'?s?\s+(the\s+)?time|current\s+time|time\s+now|what\s+time\s+is\s+it|'
    r'today\'?s?\s+date|what\s+day|what\s+date)\b',
    re.IGNORECASE
)
_CALC_PATTERN = re.compile(
    r'\b(calculate|compute|what\s+is|how\s+much\s+is)\b|'
    r'\d+\s*[+\-*/]\s*\d|'
    r'\d+\s+(plus|minus|times|divided\s+by)\s+\d',
    re.IGNORECASE
)
_WEATHER_PATTERNS = re.compile(
    r'\b(weather|forecast|temperature)\b.*\b(in|for|at)\b|'
    r'\bweather\s+in\s+\w+|'
    r'\b(how\'?s?\s+the\s+weather|what\'?s?\s+the\s+weather)',
    re.IGNORECASE
)


def _try_fast_path(user_input: str) -> Optional[str]:
    """Return tool result for simple queries without invoking LLM. Saves 1-2 API calls."""
    text = user_input.strip()
    if not text or len(text) > 200:
        return None

    # Time queries - cache 30s
    if _TIME_PATTERNS.search(text):
        cache_key = "time"
        cached = _cache_get(cache_key, _CACHE_TTL_TIME)
        if cached:
            logger.debug("LangGraph fast path: time (cached)")
            return cached
        result = _get_current_time()
        _cache_set(cache_key, result, _CACHE_TTL_TIME)
        logger.info("LangGraph fast path: time (no LLM)")
        return result

    # Calculator - extract expression
    if _CALC_PATTERN.search(text):
        expr = text.replace('plus', '+').replace('minus', '-').replace('times', '*').replace('divided by', '/')
        expr = re.sub(r'[^\d+\-*/().%\s]', ' ', expr)
        expr = re.sub(r'\s+', '', expr)
        if expr and len(expr) <= 80 and re.search(r'\d', expr):
            result = _safe_calculator(expr)
            if "Could not compute" not in result:
                logger.info("LangGraph fast path: calculator (no LLM)")
                return result

    # Weather - extract location, cache 5 min
    if _WEATHER_PATTERNS.search(text):
        loc = text.replace("weather", "").replace("forecast", "").replace("temperature", "")
        loc = re.sub(r'\b(in|for|at|how\'?s?|what\'?s?|the)\b', ' ', loc, flags=re.I)
        loc = re.sub(r'\s+', ' ', loc).strip() or "your area"
        cache_key = f"weather:{loc.lower()}"
        cached = _cache_get(cache_key, _CACHE_TTL_WEATHER)
        if cached:
            logger.debug("LangGraph fast path: weather (cached)")
            return cached
        result = _get_weather(loc)
        _cache_set(cache_key, result, _CACHE_TTL_WEATHER)
        logger.info("LangGraph fast path: weather (no LLM)")
        return result

    return None


SYSTEM_PROMPT = """You are a helpful voice assistant. Use your tools when the user asks for:
- Weather: use the weather tool with the city/location
- Math: use the calculator tool with the expression
- Current time/date: use the current_time tool
- Recent info or search: use web_search
Answer briefly and clearly. If no tool fits, answer from your knowledge."""


class LangChainAgent:
    """
    LangGraph ReAct agent with weather, calculator, time, and optional web search tools.
    """

    def __init__(self):
        self.enabled = False
        self.graph = None
        if not LANGCHAIN_AVAILABLE or not LANGGRAPH_AVAILABLE:
            logger.warning(
                "LangGraph not installed. Run: pip install langgraph langchain langchain-openai langchain-community"
            )
            return
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("LangGraph agent needs OPENAI_API_KEY to run.")
            return
        try:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
            llm = ChatOpenAI(model=model_name, temperature=0.5, api_key=api_key)
            tools = _build_tools()
            self.graph = create_react_agent(
                llm,
                tools=tools,
                prompt=SYSTEM_PROMPT,
            )
            self.enabled = True
            logger.info("LangGraph agent initialized with tools: weather, calculator, current_time, web_search")
        except Exception as e:
            logger.error(f"LangGraph agent init failed: {e}")
            self.enabled = False

    def run(self, user_input: str) -> str:
        """Run the agent on user input. Fast path skips LLM for simple tool queries."""
        if not self.enabled or not self.graph:
            return "LangGraph agent is not available. Check USE_LANGCHAIN_AGENT, OPENAI_API_KEY, and LangGraph install."
        try:
            # Fast path: simple time/calc/weather → no LLM call
            fast_result = _try_fast_path(user_input)
            if fast_result:
                return fast_result

            inputs = {"messages": [HumanMessage(content=user_input)]}
            config = {"recursion_limit": 8}  # Cap agent steps for efficiency
            result = self.graph.invoke(inputs, config=config)
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                content = getattr(last_message, "content", None)
                if content:
                    return str(content).strip()
            return "I couldn't generate a response."
        except Exception as e:
            logger.error(f"LangGraph agent error: {e}")
            return f"Agent error: {str(e)[:150]}"
