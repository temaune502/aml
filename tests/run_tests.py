import os
import sys
import time
import json
import subprocess
import datetime
import glob

# Configuration
TEST_DIRS = ['tests','tests/comprehensive_suite'] # Start with just tests, maybe add specific examples later
EXAMPLES_TO_TEST = [
    'examples/basic.aml',
    'examples/function_skeleton.aml',
    'examples/loops_conditions.aml',
    'examples/v5.aml',
    'examples/v4.aml',
    'examples/v2.aml',
    'examples/v3.aml',
    'examples/nested_ns.aml',
    'examples/meta_parallel_test.aml',
    'examples/exp.aml',
    'examples/example_main.aml',
    'examples/kwargs_demo.aml',
    'examples/hof_test.aml',
    'examples/meta_header.aml',
    'examples/numpy_demo.aml',
    'aml_moduls/namespaces_demo.aml',
    'aml_moduls/parallel_demo.aml',
    'tests/complex_suite/main_test.aml',
    'tests/sdk_demo.aml',
    'tests/test_const.aml',
    'tests/test_args.aml',
    'tests/test_counter.aml',
    'tests/test_system_module.aml',

    # Add more robust examples here
    'all_features_test.aml' 
]
STATS_FILE = 'test_stats.json'

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_stats(stats):
    # Keep only last 50 runs to avoid huge file
    if len(stats) > 50:
        stats = stats[-50:]
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def run_single_test(filepath):
    print(f"Running {filepath}...", end='', flush=True)
    start_time = time.time()
    
    try:
        # Run the AML interpreter as a subprocess
        # Assuming aml.py is in the root directory
        result = subprocess.run(
            [sys.executable, 'aml.py', filepath],
            capture_output=True,
            text=True,
            timeout=10 # 10 seconds timeout per test
        )
        print(result.stdout)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            # Check for "Fail:" in output which might indicate logical failure in test script
            if "Fail:" in result.stdout:
                 print(f" \033[91mFAILED (Logic)\033[0m ({duration:.3f}s)")
                 return {
                    "status": "FAILED",
                    "time": duration,
                    "error": "Logical failure detected in stdout",
                    "stdout": result.stdout
                }
            
            print(f" \033[92mPASSED\033[0m ({duration:.3f}s)")
            return {
                "status": "PASSED",
                "time": duration,
                "error": None
            }
        else:
            print(f" \033[91mFAILED (Crash)\033[0m ({duration:.3f}s)")
            return {
                "status": "ERROR",
                "time": duration,
                "error": result.stderr if result.stderr else result.stdout
            }
            
    except subprocess.TimeoutExpired:
        print(f" \033[91mTIMEOUT\033[0m")
        return {
            "status": "TIMEOUT",
            "time": 10.0,
            "error": "Execution timed out"
        }
    except Exception as e:
        print(f" \033[91mERROR\033[0m")
        return {
            "status": "INTERNAL_ERROR",
            "time": 0,
            "error": str(e)
        }

def main():
    print("=== Starting AML Test Suite ===")
    
    # Gather test files
    test_files = []
    
    # 1. From test dirs
    for d in TEST_DIRS:
        if os.path.exists(d):
            test_files.extend(glob.glob(os.path.join(d, "*.aml")))
            
    # 2. Specific examples
    for ex in EXAMPLES_TO_TEST:
        if os.path.exists(ex):
            test_files.append(ex)
            
    # Remove duplicates
    test_files = sorted(list(set(test_files)))
    
    if not test_files:
        print("No test files found!")
        return

    # Run tests
    current_run_stats = {}
    passed_count = 0
    total_time = 0
    
    for tf in test_files:
        res = run_single_test(tf)
        current_run_stats[tf] = res
        if res['status'] == 'PASSED':
            passed_count += 1
        total_time += res['time']
        
    # Summary
    print("\n=== Test Summary ===")
    print(f"Total: {len(test_files)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {len(test_files) - passed_count}")
    print(f"Total Duration: {total_time:.3f}s")
    
    # Save stats
    all_stats = load_stats()
    
    run_record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "total": len(test_files),
            "passed": passed_count,
            "failed": len(test_files) - passed_count,
            "duration": total_time
        },
        "details": current_run_stats
    }
    
    all_stats.append(run_record)
    save_stats(all_stats)
    print(f"Statistics saved to {STATS_FILE}")

if __name__ == "__main__":
    main()
