from crucible.orchestrator import Orchestrator


def main():
    orch = Orchestrator()
    orch.bus.emit("generate_prompt", {"topic": "demo"})


if __name__ == "__main__":
    main()
