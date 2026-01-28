# Main entry point for AML language (uses AMLRuntime)

import sys
import os
import time
import datetime
from aml.aml_runtime import AMLRuntime
import aml_runtime_access

def print_help():
    print("AML - Automation Macro Language")
    print("Usage:")
    print("  aml [options] [script]")
    print("")
    print("Options:")
    print("  -h, --help     Show this help message and exit")
    print("  -i, --interactive  Run in interactive mode")
    print("  --yield-every N    Micro-yield after N statements/evaluations (default 64)")
    print("  --yield-sleep-ms MS  Sleep MS milliseconds per yield (default 0)")
    print("")
    print("If no script is provided, AML will run in interactive mode.")

def run_file(file_path, yield_every=None, yield_sleep_ms=None):
    try:
        runtime = AMLRuntime()
        aml_runtime_access.attach_interpreter(runtime.interpreter)
        # print(runtime.get_env_snapshot())
        # Configure micro-yield if provided
        if yield_every is not None or yield_sleep_ms is not None:
            sleep_seconds = None if yield_sleep_ms is None else (float(yield_sleep_ms) / 1000.0)
            runtime.configure_micro_yield(every=yield_every, sleep_seconds=sleep_seconds)
        # Add script directory and project root to Python search paths
        script_dir = os.path.dirname(os.path.abspath(file_path))
        runtime.add_python_search_path(script_dir)
        runtime.add_python_search_path(os.getcwd()) # Project root
        
        # We DON'T add plugins directory to sys.path to avoid shadowing standard library modules
        # like 'http', 'json', 'datetime'. They should be imported as 'plugins\http' etc.
        
        start_time = time.perf_counter()


        runtime.run_file(file_path)
        end_time = time.perf_counter()  
        print(f"execution time: {end_time - start_time:.6f} seconds")


        #runtime.print_env_snapshot()
    except KeyboardInterrupt:
        print("\nВиконання перервано користувачем (KeyboardInterrupt)")
        sys.exit(130)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def run_interactive(yield_every=None, yield_sleep_ms=None):
    print("AML Interactive Mode (Ctrl+C to exit)")
    print("Type your AML code and press Enter to execute")
    print("Type 'exit' to quit")
    
    runtime = AMLRuntime()
    aml_runtime_access.attach_interpreter(runtime.interpreter)
    # Configure micro-yield if provided
    if yield_every is not None or yield_sleep_ms is not None:
        sleep_seconds = None if yield_sleep_ms is None else (float(yield_sleep_ms) / 1000.0)
        runtime.configure_micro_yield(every=yield_every, sleep_seconds=sleep_seconds)
    
    while True:
        try:
            line = input("aml> ")
            
            if line.lower() == 'exit':
                break
            
            # Skip empty lines
            if not line.strip():
                continue
            
            # Execute via runtime to keep persistent environment
            runtime.run_source(line)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def run(source, yield_every=None, yield_sleep_ms=None):
    try:
        runtime = AMLRuntime()
        aml_runtime_access.attach_interpreter(runtime.interpreter)

        # Configure micro-yield if provided
        if yield_every is not None or yield_sleep_ms is not None:
            sleep_seconds = None if yield_sleep_ms is None else (float(yield_sleep_ms) / 1000.0)
            runtime.configure_micro_yield(every=yield_every, sleep_seconds=sleep_seconds)
        runtime.run_source(source)
    except KeyboardInterrupt:
        print("\nВиконання перервано користувачем (KeyboardInterrupt)")
        return
    except Exception as e:
        print(f"Error: {e}")
        raise

def main():
    # Parse command line arguments
    args = sys.argv[1:]
    # Extract micro-yield options
    yield_every = None
    yield_sleep_ms = None
    def _take_opt(opt_name):
        if opt_name in args:
            idx = args.index(opt_name)
            if idx + 1 < len(args):
                val = args[idx + 1]
                # Remove option and its value from args
                del args[idx:idx+2]
                return val
            else:
                # Remove dangling flag
                del args[idx]
        return None
    ye = _take_opt('--yield-every')
    ys = _take_opt('--yield-sleep-ms')
    if ye is not None:
        try:
            yield_every = int(ye)
        except Exception:
            pass
    if ys is not None:
        try:
            yield_sleep_ms = float(ys)
        except Exception:
            pass
    
    if not args or '-i' in args or '--interactive' in args:
        # Interactive mode
        run_interactive(yield_every=yield_every, yield_sleep_ms=yield_sleep_ms)
    elif '-h' in args or '--help' in args:
        # Help
        print_help()
    else:
        # Run script via runtime
        script_path = args[0]
        run_file(script_path, yield_every=yield_every, yield_sleep_ms=yield_sleep_ms)
def main2():
    run_file("examples/example_main.aml")

if __name__ == "__main__":
    main()