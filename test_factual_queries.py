"""Quick test of factual queries"""
import subprocess
import sys

queries = [
    "What is exit load for SBI multicap fund?",
    "What is the ELSS lock in for SBI large cap fund?",
    "What is the sharpe ratio for SBI hybrid equity fund?"
]

print("\n" + "="*80)
print("TESTING FACTUAL QUERIES")
print("="*80 + "\n")

for i, query in enumerate(queries, 1):
    print(f"\n{i}. Testing: {query}")
    print("-" * 80)
    
    result = subprocess.run(
        [sys.executable, "scripts/debug_query_pipeline.py", query],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    # Extract key information
    lines = result.stdout.split('\n')
    for line in lines:
        if 'Generated response:' in line:
            # Extract just the response part
            response = line.split('Generated response:', 1)[1].strip()
            print(f"   Response: {response[:150]}...")
        elif '[OK]' in line or '[FAIL]' in line:
            print(f"   {line.strip()}")
    
    # Check if successful
    if '[OK]' in result.stdout or 'Status: SUCCESS' in result.stdout:
        print("   ✓ SUCCESS")
    else:
        print("   ✗ FAILED")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

