import os, yaml
from crewai import LLM, Agent, Task

class CrewOrchestrator:
    def __init__(self):
        self.llm = LLM(
            model="openai/gpt-4o-mini",
            api_base="https://openrouter.ai/api/v1",
            api_key=os.environ.get("LITELLM_API_KEY"),
        )
        print(f"✅ Using model: {self.llm.model}")

    def load_config(self, yaml_path: str):
        with open(yaml_path, "r") as f:
            return yaml.safe_load(f)

    def create_agent(self, cfg: dict):
        return Agent(
            name=cfg["name"],
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            llm=self.llm,
        )

    def create_task(self, cfg: dict, agent: Agent):
        return Task(
            description=cfg["task"]["description"],
            expected_output=cfg["task"]["expected_output"],
            agent=agent,
        )

    def create_agent_and_task(self, yaml_path: str):
        cfg = self.load_config(yaml_path)
        agent = self.create_agent(cfg)
        task = self.create_task(cfg, agent)
        return agent, task