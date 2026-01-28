
import time
import statistics
import os
from aml.aml_runtime import AMLRuntime

def run_aml_benchmark(name, aml_code, iterations=5):
    results_str = f"Running {name} ({iterations} iterations)...\n"
    
    times = []
    for i in range(iterations):
        runtime = AMLRuntime()
        
        start_time = time.perf_counter()
        try:
            runtime.run_source(aml_code)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
            
        except Exception as e:
            return None, f"ERROR in {name} at iteration {i}: {e}\n"
    
    stats = {
        'min': min(times),
        'max': max(times),
        'avg': statistics.mean(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0
    }
    return stats, results_str

# 1. Benchmark WHILE loop
while_code = """
meta { entry: "main" }
func main() {
    var i = 0
    while (i < 100000) {
        i = i + 1
    }
}
"""

# 2. Benchmark FOR loop
for_code = """
meta { entry: "main" }
func main() {
    var sum = 0
    for (i in [1..100000]) {
        sum = sum + 1
    }
}
"""

# 3. Benchmark IF statements inside loop
if_code = """
meta { entry: "main" }
func main() {
    var count = 0
    var i = 0
    while (i < 100000) {
        if (i < 50000) {
            count = count + 1
        } else {
            count = count + 2
        }
        i = i + 1
    }
}
"""

# 4. Benchmark Nested Loops (Stress Test)
nested_code = """
meta { entry: "main" }
func main() {
    var total = 0
    var i = 0
    while (i < 1000) {
        var j = 0
        while (j < 100) {
            total = total + 1
            j = j + 1
        }
        i = i + 1
    }
}
"""

if __name__ == "__main__":
    ITERATIONS = 10
    output_file = "benchmark_report.txt"
    
    header = f"=== AML PERFORMANCE BENCHMARK (N={ITERATIONS}) ===\n"
    print(header, flush=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        
        f.write(header + "\n")
        f.flush() # Ensure it's written
        
        benchmarks = [
            ("While Loop (100k)", while_code),
            ("For Loop (100k)", for_code),
            ("If/Else in Loop (100k)", if_code),
            ("Nested Loops (100k total)", nested_code),
        ]
        
        results = {}
        for name, code in benchmarks:
            print(f"Starting {name}...", flush=True)
            stats, log = run_aml_benchmark(name, code, iterations=ITERATIONS)
            print(log.strip(), flush=True)
            f.write(log)
            f.flush()
            if stats:
                results[name] = stats

        summary_header = "\n" + "="*85 + "\n"
        table_header = f"{'Benchmark Name':<30} | {'Avg (s)':<12} | {'Min (s)':<12} | {'Max (s)':<12} | {'Stdev':<10}\n"
        separator = "-" * 85 + "\n"
        
        print(summary_header, end="")
        print(table_header, end="")
        print(separator, end="")
        
        f.write(summary_header)
        f.write(table_header)
        f.write(separator)
        
        for name, stats in results.items():
            row = f"{name:<30} | {stats['avg']:<12.6f} | {stats['min']:<12.6f} | {stats['max']:<12.6f} | {stats['stdev']:<10.4f}\n"
            print(row, end="")
            f.write(row)
        
        footer = "="*85 + "\n"
        print(footer)
        f.write(footer)
    
    print(f"Benchmark finished. Results also written to {output_file}")
