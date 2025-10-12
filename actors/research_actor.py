from thespian.actors import Actor
from crew_orchestrator import CrewOrchestrator
import json, traceback

class ResearchActor(Actor):
    def receiveMessage(self, message, sender):
        if isinstance(message, dict) and message.get("cmd") == "research":
            try:
                orchestrator = CrewOrchestrator()
                agent, task = orchestrator.create_agent_and_task("prompts/research_agent.yaml")
                result = task.execute_sync()

                raw_output = getattr(result, "raw", "") or getattr(result, "result", "")
                data = json.loads(raw_output) if "{" in raw_output else {
                    "topic": "Unknown",
                    "rationale": raw_output
                }

                self.send(sender, {"status": "success", "stage": "research", "data": data})
            except Exception as e:
                self.send(sender, {"status": "error", "stage": "research", "error": str(e), "trace": traceback.format_exc()})