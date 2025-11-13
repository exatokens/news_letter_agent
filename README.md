# news_letter_agent

```

## Graph Structure

┌─────────────────────────────────────────────────────────────────────┐
│                        START: User Request                          │
│                 "Get AI news from the US"                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AGENT NODE                                  │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 1. Receives user request + system prompt from YAML           │ │
│  │ 2. LLM (Claude) analyzes the request                         │ │
│  │ 3. DECIDES: Should I call the fetch_news tool?               │ │
│  │                                                               │ │
│  │ Decision Logic:                                               │ │
│  │  - Parse query: "AI news" → query="artificial intelligence"  │ │
│  │  - Extract params: "from US" → country="us"                  │ │
│  │  - Determine category: "AI" → category="technology"          │ │
│  │  - Generate tool call with optimal parameters                │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  CONDITIONAL   │
                    │  should_continue() │
                    └────────┬───────┘
                             │
                ┏━━━━━━━━━━━━┻━━━━━━━━━━━━┓
                ▼                          ▼
     ┌──────────────────┐      ┌──────────────────┐
     │  Has tool_calls? │      │ No tool_calls?   │
     │      YES         │      │      NO          │
     └────────┬─────────┘      └────────┬─────────┘
              │                         │
              ▼                         ▼
┌─────────────────────────────┐  ┌──────────────────┐
│      TOOLS NODE             │  │ EXTRACT_RESULTS  │
│ ┌─────────────────────────┐ │  │     NODE         │
│ │ Executes fetch_news()   │ │  │ (Skip to end)    │
│ │                         │ │  └────────┬─────────┘
│ │ Input:                  │ │           │
│ │  query="AI"             │ │           ▼
│ │  country="us"           │ │        ┌─────┐
│ │  category="technology"  │ │        │ END │
│ │                         │ │        └─────┘
│ │ Output:                 │ │
│ │  JSON with 10 articles  │ │
│ └─────────────────────────┘ │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT NODE (2nd Call)                            │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Now the agent receives:                                       │ │
│  │  - Original user request                                      │ │
│  │  - System prompt                                              │ │
│  │  - Tool result: JSON with 10 articles                        │ │
│  │                                                               │ │
│  │ Agent's Task:                                                 │ │
│  │  1. Analyze all 10 articles                                   │ │
│  │  2. Evaluate each on:                                         │ │
│  │     - Relevance to query                                      │ │
│  │     - Content quality (has full text?)                        │ │
│  │     - Source credibility                                      │ │
│  │     - Recency                                                 │ │
│  │     - Richness (images, keywords)                             │ │
│  │  3. Select TOP 5 articles                                     │ │
│  │  4. Provide justification for each selection                  │ │
│  │  5. Return structured analysis                                │ │
│  │                                                               │ │
│  │ NO MORE TOOL CALLS - Just analysis                           │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  CONDITIONAL   │
                    │  should_continue() │
                    └────────┬───────┘
                             │
                             ▼
                    No tool_calls this time
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTRACT_RESULTS NODE                              │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ 1. Finds the final AI message (the analysis)                 │ │
│  │ 2. Updates state:                                             │ │
│  │    - status = "completed"                                     │ │
│  │    - timestamp = current time                                 │ │
│  │ 3. Ready to return to user                                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                         ┌───────┐
                         │  END  │
                         └───────┘

```