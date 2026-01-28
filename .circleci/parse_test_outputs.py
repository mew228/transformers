import argparse
import re
import os
import sys

def _parse_file(file_path, pattern, status_label):
    """Helper to parse file based on a specific regex pattern."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    results = {}
    total_count = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(pattern, line)
            if match:
                total_count += 1
                # Extracting reason and identifiers based on groups
                groups = match.groups()
                # Assuming the last group is always the 'reason'
                reason = groups[-1]
                identifier = groups[1] if len(groups) > 1 else "Unknown"
                results[reason] = results.get(reason, []) + [identifier]

    # Print results sorted by count
    for reason, identifiers in sorted(results.items(), key=lambda x: len(x[1])):
        count = len(identifiers)
        example = identifiers[0]
        print(f"{count:4} {status_label} because: {reason} (e.g., {example})")
    
    print(f"Total {status_label} tests: {total_count}")
    return total_count

def parse_pytest_skipped(file_path):
    # Pattern for: SKIPPED [1] tests/test_file.py: reason
    pattern = r'^SKIPPED \[(\d+)\] (.*?): (.*)$'
    _parse_file(file_path, pattern, "skipped")

def parse_pytest_failed(file_path):
    # Pattern for: FAILED tests/test_file.py - Error: reason
    pattern = r'^FAILED (.*?) - (.*?): (.*)$'
    count = _parse_file(file_path, pattern, "failed")
    if count and count > 0:
        sys.exit(1)

def parse_pytest_errors(file_path):
    # Pattern for: ERROR tests/test_file.py - Error: reason
    pattern = r'^ERROR (.*?) - (.*?): (.*)$'
    count = _parse_file(file_path, pattern, "errored")
    if count and count > 0:
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Pytest Output Parser")
    parser.add_argument("--file", required=True, help="Path to the pytest output file")
    parser.add_argument("--skip", action="store_true", help="Parse skipped tests")
    parser.add_argument("--fail", action="store_true", help="Parse failed tests")
    parser.add_argument("--errors", action="store_true", help="Parse error tests")
    args = parser.parse_args()

    if args.skip:
        parse_pytest_skipped(args.file)
    if args.fail:
        parse_pytest_failed(args.file)
    if args.errors:
        parse_pytest_errors(args.file)

if __name__ == "__main__":
    main()
