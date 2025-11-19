"""Quick script to verify chunks have proper metadata"""
import json

with open('data/processed/chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f'Total chunks: {len(chunks)}')
print(f'\nSample chunk metadata:')
sample = chunks[0]
print(f'  - Has text: {bool(sample.get("text"))}')
print(f'  - Has source_url: {bool(sample.get("source_url"))}')
print(f'  - Has scheme_name: {bool(sample.get("scheme_name"))}')
print(f'  - Has document_type: {bool(sample.get("document_type"))}')
print(f'  - Has factual_data: {bool(sample.get("factual_data"))}')

print(f'\nSchemes in chunks:')
schemes = set(c.get('scheme_name') for c in chunks if c.get('scheme_name'))
for s in sorted(schemes):
    count = sum(1 for c in chunks if c.get('scheme_name') == s)
    print(f'  - {s}: {count} chunks')

print(f'\nDocument types:')
doc_types = {}
for c in chunks:
    dt = c.get('document_type', 'Unknown')
    doc_types[dt] = doc_types.get(dt, 0) + 1
for dt, count in sorted(doc_types.items()):
    print(f'  - {dt}: {count} chunks')

print(f'\nSample chunk (first 200 chars):')
print(f'  Text: {sample.get("text", "")[:200]}...')
print(f'  Source URL: {sample.get("source_url", "")}')
print(f'  Scheme: {sample.get("scheme_name", "")}')
print(f'  Document Type: {sample.get("document_type", "")}')

