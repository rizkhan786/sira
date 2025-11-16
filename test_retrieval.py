from src.patterns.storage import PatternStorage
from src.patterns.retrieval import PatternRetriever

s = PatternStorage()
r = PatternRetriever(s)

print(f"Total patterns in storage: {s.get_pattern_count()}")
print()

# Test with no thresholds
patterns = r.retrieve_patterns(
    'What is 15 + 5?',
    n_results=5,
    min_quality=0.0,
    min_similarity=0.0
)

print(f"Retrieved {len(patterns)} patterns:")
for p in patterns:
    print(f"  - {p['pattern_id']}: similarity={p['similarity_score']:.3f}, quality={p['metadata']['quality_score']:.3f}")
    print(f"    Type: {p['metadata']['pattern_type']}, Domain: {p['metadata']['domain']}")
print()

# Test with normal thresholds
patterns2 = r.retrieve_patterns(
    'What is 15 + 5?',
    n_results=3,
    min_quality=0.7,
    min_similarity=0.5
)
print(f"With thresholds (q>=0.7, s>=0.5): {len(patterns2)} patterns")
