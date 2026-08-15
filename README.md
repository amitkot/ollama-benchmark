# Ollama Benchmark

[![CI](https://github.com/amitkot/ollama-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/amitkot/ollama-benchmark/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
[![License](https://img.shields.io/github/license/amitkot/ollama-benchmark)](LICENSE)
![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Types: ty](https://img.shields.io/badge/types-ty-purple)
![Package manager: uv](https://img.shields.io/badge/package%20manager-uv-blueviolet)

A lightweight, high-performance benchmarking tool for local LLMs running via [Ollama](https://ollama.com/). Designed specifically for macOS and Linux users who want to measure the true performance of their hardware with "Scientific Fairness."

## 🚀 Features

*   **Interactive TUI Selection:** Use a beautiful checkbox interface (via `questionary`) to select multiple models from your Ollama library without typing them manually.
*   **Memory-Awareness (The Fairness Protocol):** Automatically unloads previous models using the `keep_alive=0` parameter between runs. This prevents "memory contention" where an old model stays in RAM and slows down the next benchmark.
*   **Dual-Phase Performance Metrics:** Evaluates two critical stages of inference:
    *   **Prompt Ingestion (Reader):** How fast the model processes existing context.
    *   **Token Generation (Writer):** How fast the model generates new tokens.
*   **Modern Python Workflow:** No need for `pip install` or manual virtual environment setup—just use `uv`.

## 🛠️ Prerequisites

1.  **[Ollama](https://ollama.com/):** Must be installed and running as a background service.
2.  **[uv](https://astral.sh/uv):** The fast Python package manager. [Installation guide here](https://astral.sh/uv/).

## 🚀 Quick Start

```bash
uvx --from git+https://github.com/amitkot/ollama-benchmark ollama-benchmark
```

No cloning, no installing — just run.

## 📦 Installation (optional)

```bash
git clone https://github.com/amitkot/ollama-benchmark.git
cd ollama-benchmark
```

## 🚀 Usage

The tool offers two modes of operation:

### 1. Interactive Mode (Recommended)
If you don't provide any arguments, the tool will fetch your local Ollama models and present an interactive checkbox menu.

```bash
uv run ollama-benchmark
```

### 2. Direct/Scripted Mode
Pass specific model names directly for quick testing or CI/CD automation.

```bash
# Using a space-separated list
uv run ollama-benchmark --models gemma4:12b-it phi4

# Using a quoted string (handles spaces automatically)
uv run ollama-benchmark --models "gemma4:26b-mlx phi4"
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
