# Ollama ML Benchmarker

A lightweight, high-performance benchmarking tool for local LLMs running via [Ollama](https://ollama.com/). Designed specifically for macOS and Linux users who want to measure the true performance of their hardware with "Scientific Fairness."

## 🚀 Features

*   **Interactive TUI Selection:** Use a beautiful checkbox interface (via `questionary`) to select multiple models from your Ollama library without typing them manually.
*   **Memory-Awareness (The Fairness Protocol):** Automatically unloads previous models using the `keep_alive=0` parameter between runs. This prevents "memory contention" where an old model stays in RAM and slows down the next benchmark.
*   **Dual-Phase Performance Metrics:** Evaluates two critical stages of inference: 
    *   **Prompt Ingestion (Reader):** How fast the model processes existing context.
    *   **Token Generation (Writer):** How fast the model generates new tokens.
*   **Modern Python Workflow:** Uses **PEP 723** inline dependency metadata. No need for `pip install` or manual virtual environment setup—just use `uv`.

## 🛠️ Prerequisites

1.  **[Ollama](https://ollama.com/):** Must be installed and running as a background service.
2.  **[uv](https://astral.sh/uv):** The fast Python package manager. [Installation guide here](https://astral.sh/uv/).

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ollama-ml-benchmarker.git
cd ollama-ml-benchmarker
```

## 🚀 Usage

The tool offers two modes of operation:

### 1. Interactive Mode (Recommended)
If you don't provide any arguments, the tool will fetch your local Ollama models and present an interactive checkbox menu.

```bash
uv run benchmark.py
```

### 2. Direct/Scripted Mode
Pass specific model names directly for quick testing or CI/CD automation.

```bash
# Using a space-separated list
uv run benchmark.py --models gemma4:12b-it phi4

# Using a quoted string (handles spaces automatically)
uv run benchmark.py --models "gemma4:26b-mlx phi4"
```

## 📊 Sample Output

Running a comparison between two models yields a clean, high-density summary report:

```text
============================================================
                  BENCHMARK SUMMARY REPORT
============================================================
Model                     | Task     | P-TPS   | D-TPS   | TOKENS
------------------------------------------------------------
gemma4:26b-mlx            | READER    | 137.37  | -       | 346
                          | WRITER    | -       | 50.73   | 1,321
gemma4:26b-a4b-it-qat     | READER    | 263.49  | -       | 347
                          | WRITER    | -       | 68.94   | 1,448
============================================================
Load Times: gemma4:26b-m: 26.95s, gemma4:26b-a: 18.24s
```

## 📜 License
MIT License. Use it, break it, improve it!
