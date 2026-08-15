import argparse
import subprocess
import sys
import time
from typing import Any, Optional, Union


def parse_model_args(models: Optional[list[str]]) -> list[str]:
    """Normalize argparse model input into a flat list of model names."""
    if not models:
        return []

    all_model_inputs: list[str] = []
    for model in models:
        if " " in model and len(models) == 1:
            all_model_inputs.extend(model.split())
        else:
            all_model_inputs.append(model)
    return all_model_inputs


def get_system_memory_usage() -> str:
    """Captures current system memory usage via 'top'."""
    try:
        result = subprocess.run(["top", "-l", "1"], capture_output=True, text=True, check=False)
        lines = result.stdout.split("\n")
        for line in lines:
            if "Phys" in line or "Memory" in line:
                return line.strip()
        return "Unknown"
    except Exception as e:
        return f"Error capturing memory: {e}"


def get_ollama_models() -> list[str]:
    """Fetches the list of available models from Ollama."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print("Error: Could not connect to Ollama. Is it running?")
            sys.exit(1)

        lines = result.stdout.strip().split("\n")
        if len(lines) <= 1:
            return []

        models = []
        for line in lines[1:]:
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        sys.exit(1)


def run_benchmark(model_name: str, task_type: str, prompt: str) -> dict[str, Any]:
    print(f"--- Running {task_type} on model: {model_name} ---")
    import ollama

    try:
        ollama.show(model_name)
    except Exception:
        return {"error": f"Model '{model_name}' not found locally."}

    start_time = time.time()

    try:
        response = ollama.generate(model=model_name, prompt=prompt, stream=False)
        end_time = time.time()
        mem_after = get_system_memory_usage()

        prompt_eval_count = response.get("prompt_eval_count", 0)
        prompt_eval_duration = response.get("prompt_eval_duration", 0) / 1e9
        eval_count = response.get("eval_count", 0)
        eval_duration = response.get("eval_duration", 0) / 1e9

        prompt_tps = prompt_eval_count / prompt_eval_duration if prompt_eval_duration > 0 else 0
        decode_tps = eval_count / eval_duration if eval_duration > 0 else 0

        return {
            "status": "success",
            "prompt_tokens": prompt_eval_count,
            "output_tokens": eval_count,
            "prompt_tps": round(prompt_tps, 2),
            "decode_tps": round(decode_tps, 2),
            "mem_after": mem_after.strip(),
            "duration": round(end_time - start_time, 2),
        }

    except Exception as e:
        return {"error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ollama Model Benchmark Tool (Interactive + Cleanup)"
    )
    parser.add_argument("--models", nargs="+", help="List of models to test")
    args = parser.parse_args()

    target_models = parse_model_args(args.models)

    if not target_models:
        try:
            import questionary
        except ImportError:
            print("Error: 'questionary' not found. Please run via 'uv run ollama-benchmark'")
            sys.exit(1)

        available_models = get_ollama_models()
        if not available_models:
            print("No models found in Ollama! Download one first using 'ollama pull ...'.")
            return

        selected = questionary.checkbox(
            "Select models to benchmark (Space to select, Enter to confirm):",
            choices=available_models,
        ).ask()

        if not selected:
            print("No models selected.")
            return
        target_models = selected

    results = []
    reader_prompt = "Explain the importance of self-attention in Transformers in one sentence."
    writer_prompt = (
        "Write a detailed technical summary of the history of LLMs (at least 300 tokens)."
    )

    print(f"\nStarting Benchmark Session: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Unloading previous models between runs to ensure memory fairness...")

    import ollama

    for i, model in enumerate(target_models):
        # --- CLEANUP PHASE ---
        if i > 0:
            prev_model = str(results[i - 1]["model"])
            print(f"Cleaning up {prev_model} from memory...")
            try:
                ollama.generate(model=prev_model, prompt="", stream=False, keep_alive=0.0)
            except Exception as e:
                print(f"Cleanup warning: {e}")

        # --- WARMUP PHASE ---
        print(f"\n{'=' * 60}")
        print(f"Targeting Model: {model}")
        print(f"{'=' * 60}")

        print("Warming up (Loading model into memory)...")
        t_start = time.time()
        try:
            ollama.generate(model=model, prompt="warmup", stream=False, keep_alive=-1.0)
            load_duration: Union[float, str] = round(time.time() - t_start, 2)
        except Exception as e:
            print(f"Warmup failed: {e}")
            load_duration = "Error"

        # --- DATA COLLECTION PHASE ---
        r_res = run_benchmark(model, "READER", reader_prompt)
        w_res = run_benchmark(model, "WRITER", writer_prompt)

        results.append(
            {
                "model": model,
                "load_time": load_duration,
                "reader": r_res,
                "writer": w_res,
            }
        )

    # --- REPORTING ---
    print("\n\n" + "=" * 60)
    print("BENCHMARK SUMMARY REPORT".center(60))
    print("=" * 60)
    print(f"{'Model':<25} | {'Task':<8} | {'P-TPS':<7} | {'D-TPS':<7} | {'TOKENS':<6}")
    print("-" * 60)

    for r in results:
        model: str = str(r["model"])
        reader_raw = r["reader"]
        if not isinstance(reader_raw, dict) or "error" in reader_raw:
            print(f"| {model[:25]:<25} | ERROR      | -       | -       | -      |")
            continue

        # Reader Output
        reader: dict[str, Any] = reader_raw
        p_tps = reader.get("prompt_tps", "-")
        o_toks = reader.get("output_tokens", "-")
        print(f"{model[:25]:<25} | READER    | {p_tps:<7} | {'-':<7} | {o_toks:<6}")

        # Writer Output
        writer_raw = r["writer"]
        if not isinstance(writer_raw, dict) or "error" in writer_raw:
            print(f"{'':<25} | ERROR      | -       | -       | -      |")
        else:
            writer: dict[str, Any] = writer_raw
            d_tps = writer.get("decode_tps", "-")
            w_toks = writer.get("output_tokens", "-")
            print(f"{'':<25} | WRITER    | {'-':<7} | {d_tps:<7} | {w_toks:<6}")

    print("=" * 60)
    # Formatted Load Times for cleaner display
    load_times = []
    for r in results:
        lt = r["load_time"]
        name = str(r["model"])[:12]
        load_times.append(f"{name}: {lt}s")
    print("Load Times (Warmup): " + ", ".join(load_times))


if __name__ == "__main__":
    main()
