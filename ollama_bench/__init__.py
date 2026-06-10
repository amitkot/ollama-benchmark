import json
import time
import subprocess
import os
import argparse
import sys

def get_system_memory_usage():
    """Captures current system memory usage via 'top'."""
    try:
        result = subprocess.run(['top', '-l', '1'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if "Phys" in line or "Memory" in line:
                return line.strip()
        return "Unknown"
    except Exception as e:
        return f"Error capturing memory: {e}"

def get_ollama_models():
    """Fetches the list of available models from Ollama."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: Could not connect to Ollama. Is it running?")
            sys.exit(1)
            
        lines = result.stdout.strip().split('\n')
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

def run_benchmark(model_name, task_type, prompt):
    print(f"--- Running {task_type} on model: {model_name} ---")
    import ollama 

    try:
        ollama.show(model_name)
    except Exception:
        return {"error": f"Model '{model_name}' not found locally."}

    mem_before = get_system_memory_usage()
    start_time = time.time()
    
    try:
        response = ollama.generate(model=model_name, prompt=prompt, stream=False)
        end_time = time.time()
        mem_after = get_system_memory_usage()

        prompt_eval_count = response.get('prompt_eval_count', 0)
        prompt_eval_duration = response.get('prompt_eval_duration', 0) / 1e9 
        eval_count = response.get('eval_count', 0) 
        eval_duration = response.get('eval_duration', 0) / 1e9 

        prompt_tps = prompt_eval_count / prompt_eval_duration if prompt_eval_duration > 0 else 0
        decode_tps = eval_count / eval_duration if eval_duration > 0 else 0

        return {
            "status": "success",
            "prompt_tokens": prompt_eval_count,
            "output_tokens": eval_count,
            "prompt_tps": round(prompt_tps, 2),
            "decode_tps": round(decode_tps, 2),
            "mem_after": mem_after.strip(),
            "duration": round(end_time - start_time, 2)
        }

    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Ollama Model Benchmark Tool (Interactive + Cleanup)")
    parser.add_argument("--models", nargs='+', help="List of models to test")
    args = parser.parse_args()

    target_models = []

    if args.models:
        # Handle both space-separated and quoted space-separated strings via shell/argparse logic
        all_model_inputs = []
        for m in args.models:
            if ' ' in m and len(args.models) == 1:
                all_model_inputs.extend(m.split())
            else:
                all_model_inputs.append(m)
        target_models = all_model_inputs
    else:
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
    writer_prompt = "Write a detailed technical summary of the history of LLMs (at least 300 tokens)."

    print(f"\nStarting Benchmark Session: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Unloading previous models between runs to ensure memory fairness...")

    import ollama

    for i, model in enumerate(target_models):
        # --- CLEANUP PHASE ---
        if i > 0:
            prev_model = results[i-1]['model']
            print(f"Cleaning up {prev_model} from memory...")
            try:
                ollama.generate(model=prev_model, prompt="", keep_alive=0)
            except:
                pass

        # --- WARMUP PHASE ---
        print(f"\n{'='*60}")
        print(f"Targeting Model: {model}")
        print(f"{'='*60}")
        
        print("Warming up (Loading model into memory)...")
        t_start = time.time()
        try:
            ollama.generate(model=model, prompt="warmup", keep_alive=-1) 
            load_duration = round(time.time() - t_start, 2)
        except Exception as e:
            print(f"Warmup failed: {e}")
            load_duration = "Error"

        # --- DATA COLLECTION PHASE ---
        r_res = run_benchmark(model, "READER", reader_prompt)
        w_res = run_benchmark(model, "WRITER", writer_prompt)

        results.append({
            "model": model,
            "load_time": load_duration,
            "reader": r_res,
            "writer": w_res
        })

    # --- REPORTING ---
    print("\n\n" + "="*60)
    print("BENCHMARK SUMMARY REPORT".center(60))
    print("="*60)
    print(f"{'Model':<25} | {'Task':<8} | {'P-TPS':<7} | {'D-TPS':<7} | {'TOKENS':<6}")
    print("-" * 60)

    for r in results:
        m = r['model']
        rd = r['reader']
        if 'error' in rd or not isinstance(rd, dict):
            print(f"| {m[:25]:<25} | ERROR      | -       | -       | -      |")
            continue

        # Reader Output
        p_tps = rd.get('prompt_tps', '-')
        o_toks = rd.get('output_tokens', '-')
        print(f"{m[:25]:<25} | READER    | {p_tps:<7} | {'-':<7} | {o_toks:<6}")
        
        # Writer Output
        wd = r['writer']
        if 'error' in wd:
            print(f"{'':<25} | ERROR      | -       | -       | -      |")
        else:
            d_tps = wd.get('decode_tps', '-')
            w_toks = wd.get('output_tokens', '-')
            print(f"{'':<25} | WRITER    | {'-':<7} | {d_tps:<7} | {w_toks:<6}")
    
    print("="*60)
    # Formatted Load Times for cleaner display
    load_times = []
    for r in results:
        lt = r['load_time']
        name = r['model'][:12]
        load_times.append(f"{name}: {lt}s")
    print("Load Times (Warmup): " + ", ".join(load_times))

if __name__ == "__main__":
    main()
