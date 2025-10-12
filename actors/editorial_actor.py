from thespian.actors import Actor, ActorExitRequest
from crew_orchestrator import CrewOrchestrator
from actors.research_actor import ResearchActor
from actors.summarizer_actor import SummarizerActor
import traceback

class EditorialActor(Actor):
    def __init__(self):
        super().__init__()
        self.research_actor = None
        self.summarizer_actor = None
        self.ui_sender = None
        self.topic = None
        self.summary = None

    def receiveMessage(self, message, sender):
        try:
            # 1️⃣ Trigger from UI
            if isinstance(message, dict) and message.get("cmd") == "generate":
                self.ui_sender = sender
                self.research_actor = self.createActor(ResearchActor)
                self.send(self.research_actor, {"cmd": "research"})

            # 2️⃣ Handle research completion → spawn summarizer
            elif message.get("stage") == "research" and message.get("status") == "success":
                self.topic = message["data"]["topic"]
                self.send(self.ui_sender, {"stage": "research_done", "topic": self.topic})

                self.summarizer_actor = self.createActor(SummarizerActor)
                self.send(self.summarizer_actor, {"cmd": "summarize", "topic": self.topic})
                self.send(self.research_actor, ActorExitRequest())

            # 3️⃣ Handle summarizer completion → generate editorial internally
            elif message.get("stage") == "summary" and message.get("status") == "success":
                self.summary = message["summary"]
                self.send(self.ui_sender, {"stage": "summary_done", "summary": self.summary})

                # Generate editorial
                orchestrator = CrewOrchestrator()
                cfg = orchestrator.load_config("prompts/editorial_agent.yaml")
                cfg["task"]["description"] = (
                    cfg["task"]["description"]
                    .replace("{{topic}}", self.topic)
                    .replace("{{summary}}", self.summary)
                )

                agent = orchestrator.create_agent(cfg)
                task = orchestrator.create_task(cfg, agent)
                result = task.execute_sync()

                editorial_text = getattr(result, "raw", "") or getattr(result, "result", "")
                self.send(self.ui_sender, {
                    "stage": "editorial_done",
                    "topic": self.topic,
                    "summary": self.summary,
                    "editorial": editorial_text,
                })
                self.send(self.summarizer_actor, ActorExitRequest())

            # 4️⃣ Error handling
            elif message.get("status") == "error":
                self.send(self.ui_sender, message)

        except Exception as e:
            self.send(sender, {"status": "error", "stage": "editorial", "error": str(e), "trace": traceback.format_exc()})