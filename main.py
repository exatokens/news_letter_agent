# main.py
import asyncio
import logging
import traceback
from datetime import datetime
from nicegui import ui
from crew_orchestrator import CrewOrchestrator 

# ---------- CONFIGURE LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ---------- APP STATE ----------
app_state = {
    "topics": {},
    "selected_topic": None,
    "last_updated": None,
    "loading": False,
}

# ---------- HELPERS ----------
def today():
    return datetime.now().strftime("%A, %B %d, %Y")


def select_topic(topic_name: str, title_label, summary_label):
    """When user clicks a topic on sidebar."""
    logger.info(f"📰 Topic selected: {topic_name}")
    app_state["selected_topic"] = topic_name
    title_label.text = topic_name
    summary_label.text = app_state["topics"][topic_name]
    title_label.update()
    summary_label.update()


async def generate_editorials(title_label, summary_label, topics_column, loader):
    logger.info("⚙️ Starting editorial generation via CrewAI...")
    app_state["loading"] = True
    loader.props(remove='hidden')
    await ui.run_on_main(lambda: ui.notify("🧠 Generating fresh editorial...", type="info", position="top"))

    title_label.text = "Generating Editorials..."
    summary_label.text = "⏳ Please wait while the newsroom agents curate this week's stories..."
    title_label.update()
    summary_label.update()

    try:
        orchestrator = CrewOrchestrator()
        result = await asyncio.to_thread(orchestrator.execute_sync)  # ✅ Now valid
        logger.info("✅ CrewAI completed successfully")

        app_state["topics"] = {
            "AI Deepfakes": result["summary"],
            "Quantum Breakthroughs": "Quantum computing firms are crossing from lab to production.",
            "AI in Healthcare": "AI is redefining diagnostics and drug discovery pipelines.",
        }
        app_state["last_updated"] = datetime.now().strftime("%B %d, %Y %H:%M")

        topics_column.clear()
        for topic in app_state["topics"].keys():
            ui.button(
                topic,
                on_click=lambda t=topic: select_topic(t, title_label, summary_label),
            ).classes(
                'w-full text-left mb-2 bg-white hover:bg-gray-100 text-black border border-gray-200 rounded-md px-3 py-2'
            ).parent(topics_column)

        first_topic = list(app_state["topics"].keys())[0]
        select_topic(first_topic, title_label, summary_label)

        await ui.run_on_main(lambda: ui.notify("✅ Editorial generated successfully!", type="positive", position="top"))

    except Exception as e:
        logger.error("❌ Error during editorial generation:")
        traceback.print_exc()
        await ui.run_on_main(lambda: ui.notify(f"Error: {e}", type="negative", position="top"))

    finally:
        app_state["loading"] = False
        loader.props(add='hidden')
        logger.info("⏹️ Generation process ended.")


# ---------- UI ----------
@ui.page('/')
def main_page():
    ui.query('body').style('background-color: #fdfdfd; color: #111; font-family: Georgia, serif;')

    # HEADER
    with ui.row().classes('w-full justify-between items-center border-b border-gray-300 py-3 px-6 shadow-sm bg-white sticky top-0 z-50'):
        ui.label("The AI Editorial Digest").classes('text-3xl font-extrabold text-gray-900')
        with ui.row().classes('items-center space-x-3'):
            loader = ui.icon("hourglass_top").classes('animate-spin text-gray-500 text-2xl').props('hidden')
            ui.button(
                "⚙️ Generate Editorials",
                on_click=lambda: asyncio.create_task(generate_editorials(title_label, summary_label, topics_column, loader)),
            ).classes('bg-black text-white px-5 py-2 rounded-md hover:bg-gray-800')

    # BODY
    with ui.row().classes('w-full h-[calc(100vh-80px)]'):
        # Sidebar
        with ui.column().classes('w-1/5 h-full bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto') as topics_column:
            ui.label("No topics yet.").classes("text-gray-400 italic")

        # Main Content
        with ui.column().classes('w-4/5 p-8 items-center overflow-y-auto'):
            ui.label(today()).classes('text-gray-500 text-sm mb-4 italic text-center')

            global title_label, summary_label
            title_label = ui.label("Welcome to The AI Editorial Digest").classes('text-4xl font-bold mb-6 text-center text-gray-900')
            summary_label = ui.label(
                "Click 'Generate Editorials' to curate this week's AI and Tech stories."
            ).classes('text-lg text-gray-600 leading-relaxed text-center max-w-2xl mb-10')

            ui.label("© 2025 The AI Editorial Digest — Powered by CrewAI × NiceGUI").classes(
                'mt-auto text-sm text-gray-400 italic text-center'
            )


# ---------- START ----------
if __name__ in {"__main__", "__mp_main__"}:
    logger.info("🚀 Starting The AI Editorial Digest (NiceGUI + CrewAI)")
    ui.run(title="AI Editorial Digest", reload=False, port=8080)