"""
State schemas and type definitions
"""
from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime


class NewsGathererState(TypedDict):
    # input
    messages: Annotated[List, "Conversation history between user and agent"]
    user_request: str

    # configuration
    top_articles_count: int

    # Output
    final_articles: Optional[List[Dict]]
    status: str
    timestamp: str

    # Metadata
    tool_calls_count: int
    error: Optional[str]

