from thespian.actors import Actor
import random

class EditorialActor(Actor):
    def receiveMessage(self, message, sender):
        if message.get("cmd") == "generate":
            topic = random.choice([
                "AI Policy", "Drug Discovery", "Quantum Tech"
            ])
            summary = f"Generated editorial on {topic}."
            self.send(sender, {"topic": topic, "summary": summary})
