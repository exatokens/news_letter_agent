from crewai import LLM, Agent, Crew, Task

import os
from crewai import LLM

os.environ["LITELLM_API_KEY"] = "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"
os.environ["LITELLM_API_BASE"] = "https://openrouter.ai/api/v1"
os.environ["CREWAI_LLM_PROVIDER"] = "litellm"

# # Optional safety clear to make sure CrewAI never sees old keys
# os.environ.pop("OPENAI_API_KEY", None)
# os.environ.pop("PPLX_API_KEY", None)

llm = LLM(
    model="openai/gpt-4o-mini",
    api_base="https://openrouter.ai/api/v1",   
    api_key=os.environ["LITELLM_API_KEY"]
)

print(f"✅ Using model: {llm.model}")

from thespian.actors import ActorSystem
from actors.editorial_actor import EditorialActor


class NewsletterCrew:
    def __init__(self):
        self.actor_system = ActorSystem('multiprocTCPBase')

    def run(self):
        # 🔹 Shared Perplexity LLM for all agents
        # llm = LLM(model="openai/gpt-4o-mini")

        researcher = Agent(
            name="ResearchAgent",
            role="Tech Research Analyst",
            goal="Collect the top 5–10 latest technology and AI news stories.",
            backstory="A sharp analyst using Perplexity to scan the live web for trending tech topics.",
            llm=llm,
        )

        summarizer = Agent(
            name="SummarizerAgent",
            role="Content Summarizer",
            goal="Summarize collected news into concise bullet summaries.",
            backstory="A concise communicator who distills large chunks of text into crisp insights.",
            llm=llm,
        )

        editorial = Agent(
            name="EditorialAgent",
            role="Chief Editor",
            goal="Craft a readable editorial digest of the summarized news.",
            backstory="An editor who turns summaries into a polished, engaging newsletter editorial.",
            llm=llm,
        )

        crew = Crew(
            agents=[researcher, summarizer, editorial],
            tasks=[
                Task(
                    description="Find 5–10 credible AI and technology news articles.",
                    agent=researcher,
                    expected_output="A list of article headlines with source names and brief descriptions."
                ),
                Task(
                    description="Summarize and condense the gathered articles into key insights.",
                    agent=summarizer,
                    expected_output="Five concise summaries, 2–3 sentences each, highlighting main themes."
                ),
                Task(
                    description="Write an editorial digest summarizing weekly trends in AI and technology.",
                    agent=editorial,
                    expected_output="A 3-paragraph editorial highlighting the week's main technological developments."
                ),
            ],
        )

        result = crew.kickoff()

        # Optional Thespian integration
        actor_ref = self.actor_system.createActor(EditorialActor)
        self.actor_system.tell(actor_ref, {"cmd": "generate"})

        return result