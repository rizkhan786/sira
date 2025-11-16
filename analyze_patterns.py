from src.patterns.storage import PatternStorage
from src.patterns.retrieval import PatternRetriever

s = PatternStorage()
r = PatternRetriever(s)

print(f"=== Pattern Storage Analysis ===")
print(f"Total patterns: {s.get_pattern_count()}\n")

# Test math query
test_query = "What is 100 + 50?"
print(f"Test query: '{test_query}'\n")

# Get all patterns (no filters)
all_patterns = r.retrieve_patterns(
    test_query,
    n_results=10,
    min_quality=0.0,
    min_similarity=0.0
)

print(f"All {len(all_patterns)} patterns ranked by similarity:")
for i, p in enumerate(all_patterns, 1):
    meta = p['metadata']
    print(f"{i}. {p['pattern_id']}")
    print(f"   Type: {meta['pattern_type']}, Domain: {meta['domain']}")
    print(f"   Similarity: {p['similarity_score']:.3f}")
    print(f"   Quality: {meta['quality_score']:.3f}")
    print(f"   Ranking Score: {p['ranking_score']:.3f}")
    print()

# With normal filters
filtered = r.retrieve_patterns(
    test_query,
    n_results=3,
    min_quality=0.7,
    min_similarity=0.2
)

print(f"With filters (q>=0.7, s>=0.2, top 3): {len(filtered)} patterns")
for p in filtered:
    print(f"  - {p['pattern_id']}: similarity={p['similarity_score']:.3f}")
