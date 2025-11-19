"""
Script to verify information coverage in scraped data
Checks for expense ratios, exit loads, minimum SIP, lock-in periods, riskometer ratings, benchmarks
"""

import json
from collections import defaultdict

def check_information_coverage():
    """Check what factual information is available in the chunks"""
    
    # Load chunks
    with open('data/processed/chunks.json', 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print("="*70)
    print("INFORMATION COVERAGE VERIFICATION")
    print("="*70)
    
    # Track coverage by scheme
    scheme_coverage = defaultdict(lambda: {
        'expense_ratio_regular': False,
        'expense_ratio_direct': False,
        'exit_load': False,
        'minimum_sip': False,
        'minimum_lumpsum': False,
        'lock_in_period': False,
        'riskometer': False,
        'benchmark': False,
        'total_chunks': 0
    })
    
    # Track overall coverage
    overall_coverage = {
        'expense_ratio_regular': set(),
        'expense_ratio_direct': set(),
        'exit_load': set(),
        'minimum_sip': set(),
        'minimum_lumpsum': set(),
        'lock_in_period': set(),
        'riskometer': set(),
        'benchmark': set()
    }
    
    # Check each chunk
    for chunk in chunks:
        scheme_name = chunk.get('scheme_name', 'Unknown')
        factual_data = chunk.get('factual_data', {})
        
        scheme_coverage[scheme_name]['total_chunks'] += 1
        
        # Check each information type
        if factual_data.get('expense_ratio_regular'):
            scheme_coverage[scheme_name]['expense_ratio_regular'] = True
            overall_coverage['expense_ratio_regular'].add(scheme_name)
        
        if factual_data.get('expense_ratio_direct'):
            scheme_coverage[scheme_name]['expense_ratio_direct'] = True
            overall_coverage['expense_ratio_direct'].add(scheme_name)
        
        if factual_data.get('exit_load'):
            scheme_coverage[scheme_name]['exit_load'] = True
            overall_coverage['exit_load'].add(scheme_name)
        
        if factual_data.get('minimum_sip'):
            scheme_coverage[scheme_name]['minimum_sip'] = True
            overall_coverage['minimum_sip'].add(scheme_name)
        
        if factual_data.get('minimum_lumpsum'):
            scheme_coverage[scheme_name]['minimum_lumpsum'] = True
            overall_coverage['minimum_lumpsum'].add(scheme_name)
        
        if factual_data.get('lock_in_period'):
            scheme_coverage[scheme_name]['lock_in_period'] = True
            overall_coverage['lock_in_period'].add(scheme_name)
        
        if factual_data.get('riskometer'):
            scheme_coverage[scheme_name]['riskometer'] = True
            overall_coverage['riskometer'].add(scheme_name)
        
        if factual_data.get('benchmark'):
            scheme_coverage[scheme_name]['benchmark'] = True
            overall_coverage['benchmark'].add(scheme_name)
    
    # Print coverage by scheme
    print("\nCOVERAGE BY SCHEME:")
    print("="*70)
    
    info_types = [
        'expense_ratio_regular',
        'expense_ratio_direct',
        'exit_load',
        'minimum_sip',
        'minimum_lumpsum',
        'lock_in_period',
        'riskometer',
        'benchmark'
    ]
    
    for scheme_name in sorted(scheme_coverage.keys()):
        coverage = scheme_coverage[scheme_name]
        print(f"\n{scheme_name} ({coverage['total_chunks']} chunks):")
        
        for info_type in info_types:
            status = "✓" if coverage[info_type] else "✗"
            display_name = info_type.replace('_', ' ').title()
            print(f"  {status} {display_name}")
    
    # Print overall coverage summary
    print("\n" + "="*70)
    print("OVERALL COVERAGE SUMMARY")
    print("="*70)
    
    total_schemes = len(scheme_coverage)
    
    for info_type in info_types:
        schemes_with_info = overall_coverage[info_type]
        count = len(schemes_with_info)
        percentage = (count / total_schemes * 100) if total_schemes > 0 else 0
        display_name = info_type.replace('_', ' ').title()
        
        status = "✓" if count > 0 else "✗"
        print(f"{status} {display_name}: {count}/{total_schemes} schemes ({percentage:.1f}%)")
        if schemes_with_info:
            print(f"    Found in: {', '.join(sorted(schemes_with_info))}")
    
    # Print detailed factual data for each scheme
    print("\n" + "="*70)
    print("DETAILED FACTUAL DATA BY SCHEME")
    print("="*70)
    
    # Get unique schemes and their factual data
    scheme_factual_data = {}
    for chunk in chunks:
        scheme_name = chunk.get('scheme_name', 'Unknown')
        if scheme_name not in scheme_factual_data:
            scheme_factual_data[scheme_name] = {}
        
        factual_data = chunk.get('factual_data', {})
        # Merge factual data (prefer non-None values)
        for key, value in factual_data.items():
            if value and (key not in scheme_factual_data[scheme_name] or not scheme_factual_data[scheme_name][key]):
                scheme_factual_data[scheme_name][key] = value
    
    for scheme_name in sorted(scheme_factual_data.keys()):
        print(f"\n{scheme_name}:")
        factual = scheme_factual_data[scheme_name]
        
        if factual.get('expense_ratio_regular'):
            print(f"  Expense Ratio Regular: {factual['expense_ratio_regular']}%")
        if factual.get('expense_ratio_direct'):
            print(f"  Expense Ratio Direct: {factual['expense_ratio_direct']}%")
        if factual.get('exit_load'):
            print(f"  Exit Load: {factual['exit_load']}%")
        if factual.get('minimum_sip'):
            print(f"  Minimum SIP: ₹{factual['minimum_sip']}")
        if factual.get('minimum_lumpsum'):
            print(f"  Minimum Lumpsum: ₹{factual['minimum_lumpsum']}")
        if factual.get('lock_in_period'):
            print(f"  Lock-in Period: {factual['lock_in_period']}")
        if factual.get('riskometer'):
            print(f"  Riskometer: {factual['riskometer']}")
        if factual.get('benchmark'):
            print(f"  Benchmark: {factual['benchmark']}")
        
        # Check if no data found
        if not any(factual.values()):
            print("  ⚠ No factual data extracted")
    
    print("\n" + "="*70)
    print("VERIFICATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    check_information_coverage()

