from .event_bus import EventBus
from .prompts.generator import PromptGenerator
from .brainstormer import Brainstormer
from .summarizer import Summarizer


class Orchestrator:
    def __init__(self, bus: EventBus | None = None):
        self.bus = bus or EventBus()
        self.generator = PromptGenerator()
        self.brainstormer = Brainstormer()
        self.summarizer = Summarizer()
        self._register_handlers()

    def _register_handlers(self):
        self.bus.register("generate_prompt", self.handle_generate_prompt)
        self.bus.register("brainstorm", self.handle_brainstorm)
        self.bus.register("summarize", self.handle_summarize)

    def handle_generate_prompt(self, payload):
        print("todo: implement generate_prompt handler")
        prompt = self.generator.generate(payload)
        self.bus.emit_legacy("brainstorm", {"prompt": prompt})

    def handle_brainstorm(self, payload):
        print("todo: implement brainstorm handler")
        ideas = self.brainstormer.brainstorm(payload)
        self.bus.emit_legacy("summarize", {"ideas": ideas})

    def handle_summarize(self, payload):
        print("todo: implement summarize handler")
        summary = self.summarizer.summarize(payload)
        print(summary)
