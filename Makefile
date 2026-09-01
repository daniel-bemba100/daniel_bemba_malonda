.PHONY: all install run build clean test format lint

# Default target
all: run

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .

# Run the application
run:
	@echo "Starting UPC Notepad..."
	python main.py

# Build the executable using PyInstaller
build:
	@echo "Building executable..."
	pyinstaller UPC_Notepad.spec --clean
	@echo "Build complete. Executable is in the dist/ directory."

# Clean generated files and directories
clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete."

# Run tests
test:
	@echo "Running tests..."
	pytest tests/

# Format code (assuming black is installed)
format:
	@echo "Formatting code..."
	black src/ tests/ main.py

# Lint code (assuming flake8 is installed)
lint:
	@echo "Linting code..."
	flake8 src/ tests/ main.py
