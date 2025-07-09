# Crucible justfile - Command runner for common tasks

# Default task - show available commands
default:
    @just --list

# Run the blueprint CLI
blueprint *args:
    ./cru blueprint {{args}}

# Run AI integration demo
demo:
    @python demo.py

# Run tests
test:
    python -m pytest tests/

# Run tests with verbose output
test-verbose:
    python -m pytest -v tests/

# Clean up Python cache files
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache/

# Install dependencies (if requirements.txt exists)
install:
    @if [ -f requirements.txt ]; then \
        pip install -r requirements.txt; \
    else \
        echo "No requirements.txt found. Installing openai package..."; \
        pip install openai; \
    fi

# Show git status
status:
    git status

# Run the AI script with custom prompt
ai prompt:
    python run_ai.py "{{prompt}}"