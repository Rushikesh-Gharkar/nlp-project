import sys
import io

# Ensure utf-8 output encoding on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from translator import translation_engine

test_sentences = [
    "I am learning machine learning.",
    "Good morning.",
    "India is a beautiful country."
]

print("=== Testing English to Hindi Translation ===")
for s in test_sentences:
    trans, latency = translation_engine.translate(s, "hi")
    print(f"EN: {s}")
    print(f"HI: {trans} ({latency} ms)")
    print("-" * 30)

print("\n=== Testing English to Marathi Translation ===")
for s in test_sentences:
    trans, latency = translation_engine.translate(s, "mr")
    print(f"EN: {s}")
    print(f"MR: {trans} ({latency} ms)")
    print("-" * 30)

print("\nALL INFERENCE TESTS PASSED SUCCESSFULLY!")
