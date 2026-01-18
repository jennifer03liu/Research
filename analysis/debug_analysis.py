import sys
import traceback
import subprocess

with open("error_log.txt", "w") as log:
    try:
        # Run analysis_t1.py as a subprocess and capture output
        result = subprocess.run(
            [sys.executable, "analysis_t1.py"],
            capture_output=True,
            text=True
        )
        log.write("STDOUT:\n")
        log.write(result.stdout)
        log.write("\nSTDERR:\n")
        log.write(result.stderr)
        if result.returncode != 0:
             log.write(f"\nExited with code {result.returncode}")
    except Exception:
        traceback.print_exc(file=log)
