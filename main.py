from dotenv import load_dotenv
load_dotenv()  # Loads all variables from .env into os.environ

from nicegui import ui
import asyncio
from crew_orchestrator import NewsletterCrew

crew = NewsletterCrew()
status = ui.label("")
output = ui.markdown("")

async def generate_editorial():
    status.set_text("🧠 Running CrewAI + Thespian pipeline...")
    result = await asyncio.to_thread(crew.run)
    output.set_content(f"### Editorial Crew Result\n{result}")
    status.set_text("✅ Done!")

ui.label("🗞️ ComplexEconomy Newsletter").classes("text-2xl font-bold mt-4")
ui.button("Generate Editorial", on_click=generate_editorial).classes("bg-blue-600 text-white mt-3")
ui.separator()
output
status

ui.run(title="Newsletter Agent Hybrid")