# Example Code and Schema Snippets

Below are a few representative snippets showing how pieces of Crucible might look. They are illustrative rather than final.

## Prompt Definition (Python)
```python
# src/crucible/prompts/base.py
from dataclasses import dataclass

@dataclass
class Prompt:
    name: str
    template: str

    def render(self, context: dict) -> str:
        return self.template.format(**context)
```

## Idea Storage Schema (YAML)
```yaml
# data/ideas/sample.yaml
id: idea-001
summary: "Improve onboarding flow"
notes:
  - "Gather existing feedback"
  - "Identify friction points"
status: draft
```

## CLI Entry Point (Python)
```python
# src/cli.py
import click
from crucible.prompts import load_prompt

@click.command()
@click.argument('prompt_name')
@click.option('--context', type=str)
def run(prompt_name: str, context: str):
    prompt = load_prompt(prompt_name)
    print(prompt.render(eval(context)))

if __name__ == '__main__':
    run()
```
