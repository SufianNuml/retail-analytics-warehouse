"""
run_pipeline.py — orchestrates the full pipeline end-to-end.

This is a simple single-machine DAG-like orchestrator.
It manages:
- task ordering
- logging
- failure handling
"""

import sys
import traceback
from datetime import datetime
STEPS = [
    ("Generate data",      "generate_data",      "main"),
    ("Upload raw to S3",   "upload_to_s3",       "upload_raw_files"),
    ("Clean data",         "clean_data",         "main"),
    ("Load to Snowflake",  "load_to_snowflake",  "load_to_snowflake"),
    ("Run audit",          "audit_pipeline",     "run_audit"),
    ("Run anomaly checks", "anomaly_detection",  "run_anomaly_checks"),
]
def run_pipeline():

    print(
        f"=== Pipeline started: {datetime.utcnow().isoformat()} ==="
    )


    for step_name, module_name, func_name in STEPS:

        print("\n" + "-" * 60)
        print(f"Running: {step_name}")
        print("-" * 60)

        try:

            module = __import__(
                module_name,
                fromlist=[func_name]
            )

            func = getattr(
                module,
                func_name
            )

            func()

            print(f"✅ {step_name} completed")


        except Exception as e:

            print(f"❌ {step_name} failed")
            print(e)

            traceback.print_exc()

            print(
                "Pipeline stopped because of failure."
            )

            sys.exit(1)


    print(
        f"\n=== Pipeline completed successfully: {datetime.utcnow().isoformat()} ==="
    )


if __name__ == "__main__":
    run_pipeline()