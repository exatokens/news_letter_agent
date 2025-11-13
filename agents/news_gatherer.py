from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from datetime import datetime
import os
import logging

from config.settings import settings
from prompts.news_gatherer_prompts import NewsGathererPrompts
from tools.news_tools import NewsTools
from schemas.state_schemas import NewsGathererState


# logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsGathererAgent:
    def __init__(self):
        """Initialize the agent with configuration"""
        self.settings = settings
        self.prompts = NewsGathererPrompts()
        self.tools = [NewsTools.fetch_news]
        self.graph = self._build_graph()

        # Log prompt metadata
        metadata = self.prompts.get_metadata()
        logger.info(f"NewsGathererAgent initialized")
        logger.info(f"Prompt version: {metadata.get('version')}")

    def _create_agent_node(self, state: NewsGathererState) -> NewsGathererState:
        """Main agent node that processes requests and analyzes results"""
        try:
            llm = ChatGroq(
                model=self.settings.LLM_MODEL,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS
            )
            # Bind tools
            llm_with_tools = llm.bind_tools(self.tools)

            # Load system prompt from YAML
            system_prompt = self.prompts.get_system_prompt(
                max_articles=self.settings.MAX_ARTICLES_PER_FETCH,
                top_articles=state["top_articles_count"]
            )
            messages = [SystemMessage(content=system_prompt)] + state["messages"]

            # Get LLM response
            logger.info("Invoking LLM for agent decision")
            # import pdb;pdb.set_trace()
            response = llm_with_tools.invoke(messages)

            # Track tool calls
            if hasattr(response, "tool_calls") and response.tool_calls:
                state["tool_calls_count"] += len(response.tool_calls)
                logger.info(f"Agent made {len(response.tool_calls)} tool call(s)")


        except Exception as e:
            logger.error(f"Error in agent node: {str(e)}")
            state["status"] = "error"
            state["error"] = str(e)

        return state

    def _should_continue(self, state: NewsGathererState) -> str:
        """Determine next step in workflow"""

        last_message = state["messages"][-1]

        # If there are tool calls, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.info("Routing to tool execution")
            return "tools"

        # Otherwise, we're done
        logger.info("Workflow complete")
        return "end"

    def _extract_results(self, state: NewsGathererState) -> NewsGathererState:
        """Extract final results from agent's analysis"""

        try:
            # Find the final AI message (after tool use)
            final_message = None
            for msg in reversed(state["messages"]):
                if isinstance(msg, AIMessage) and not hasattr(msg, "tool_calls"):
                    final_message = msg
                    break

            if final_message:
                state["status"] = "completed"
                logger.info("Results extracted successfully! Cheers..")
            else:
                state["status"] = "incomplete"
                logger.warning("No final message found")

            state["timestamp"] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Error extracting results: {str(e)}")
            state["status"] = "error"
            state["error"] = str(e)

        return state

    def _build_graph(self) -> StateGraph:
        """ BUild the Langgraph workflow"""
        workflow = StateGraph(NewsGathererState)

        # addd nodes
        workflow.add_node("agent", self._create_agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("extract_results", self._extract_results)
        workflow.add_edge("tools", "agent")
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "end": "extract_results"
            }
        )
        workflow.add_edge("tools", "agent")
        workflow.add_edge("extract_results", END)
        # Compile
        logger.info("LangGraph workflow compiled")
        return workflow.compile()
    
    def run(self, user_request: str, top_articles: int = None) -> NewsGathererState:
        """
        Execute the news gathering workflow
        
        Args:
            user_request: Natural language description of news to fetch
            top_articles: Number of articles to select (default: from settings)
        
        Returns:
            Final state with agent's analysis and selections
        """
        
        if top_articles is None:
            top_articles = self.settings.TOP_ARTICLES_TO_SELECT
        
        # Load and format user prompt from YAML
        user_prompt = self.prompts.get_user_prompt(
            user_request=user_request,
            top_articles=top_articles
        )
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=user_prompt)],
            "user_request": user_request,
            "top_articles_count": top_articles,
            "final_articles": None,
            "status": "initialized",
            "timestamp": datetime.now().isoformat(),
            "tool_calls_count": 0,
            "error": None
        }
        
        logger.info(f"Starting workflow for request: {user_request[:100]}...")
        
        # Execute workflow
        final_state = self.graph.invoke(initial_state)
        
        logger.info(f"Workflow completed with status: {final_state['status']}")
        
        return final_state

