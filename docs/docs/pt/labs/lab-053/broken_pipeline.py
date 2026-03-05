#!/usr/bin/env python3
"""
🐛 Broken AI Pipeline — Lab 053 Bug-Fix Exercise

Mock AI enrichment functions with 3 bugs.
Fix them and run the self-tests to verify.

Usage:
    python lab-053/broken_pipeline.py
"""

import io
import pandas as pd


def classify_sentiment(rating: int) -> str:
    """Classify a review rating into sentiment categories."""
    # 🐛 Bug #1: Threshold for positive is >= 3 instead of >= 4
    #            This incorrectly classifies neutral reviews (rating=3) as positive
    if rating >= 3:
        return "positive"
    elif rating <= 2:
        return "negative"
    return "neutral"


def count_reviews_per_product(reviews: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with product_name and review_count, sorted descending."""
    # 🐛 Bug #2: Groups by review_id instead of product_name
    #            Every row becomes its own group (count=1 for all)
    return (
        reviews.groupby("review_id")
        .size()
        .reset_index(name="review_count")
        .sort_values("review_count", ascending=False)
    )


def avg_rating_by_sentiment(reviews: pd.DataFrame, sentiment: str) -> float:
    """Return the average rating for reviews of a given sentiment."""
    # 🐛 Bug #3: Doesn't filter by sentiment — averages ALL reviews
    return reviews["rating"].mean()


def run_tests() -> bool:
    test_csv = """\
review_id,product_id,product_name,category,rating,review_text
R1,P1,Tent A,Tents,5,Amazing product
R2,P1,Tent A,Tents,4,Good quality
R3,P1,Tent A,Tents,3,Average tent
R4,P2,Boot A,Footwear,2,Disappointing
R5,P3,Pack A,Backpacks,1,Terrible quality"""

    reviews = pd.read_csv(io.StringIO(test_csv))
    reviews["sentiment"] = reviews["rating"].apply(classify_sentiment)

    passed = 0
    failed = 0

    # ── Test 1: Sentiment classification ─────────────────────────────────
    #   Rating 5→positive, 4→positive, 3→neutral, 2→negative, 1→negative
    #   Positive count should be 2 (not 3)
    positive_count = (reviews["sentiment"] == "positive").sum()
    if positive_count == 2:
        print(f"✅ Test 1 PASSED: positive reviews = {positive_count}")
        passed += 1
    else:
        print(f"❌ Test 1 FAILED: positive reviews = {positive_count}  (expected 2)")
        failed += 1

    # ── Test 2: Reviews per product ──────────────────────────────────────
    #   Tent A has 3 reviews → should be in the result with count=3
    per_product = count_reviews_per_product(reviews)
    # The result should have 3 groups (Tent A, Boot A, Pack A)
    if len(per_product) == 3:
        print(f"✅ Test 2 PASSED: product groups = {len(per_product)}")
        passed += 1
    else:
        print(f"❌ Test 2 FAILED: product groups = {len(per_product)}  (expected 3)")
        failed += 1

    # ── Test 3: Average rating for positive reviews ──────────────────────
    #   Positive reviews: R1(5) + R2(4) → avg = 4.5
    avg = avg_rating_by_sentiment(reviews, "positive")
    if abs(avg - 4.5) < 0.01:
        print(f"✅ Test 3 PASSED: avg positive rating = {avg:.1f}")
        passed += 1
    else:
        print(f"❌ Test 3 FAILED: avg positive rating = {avg:.1f}  (expected 4.5)")
        failed += 1

    print()
    if failed == 0:
        print("🎉 All 3 tests passed — great debugging!")
    else:
        print(f"🔧 {failed} test(s) failed — keep debugging!")
    return failed == 0


if __name__ == "__main__":
    print("🧪 Running self-tests for broken_pipeline.py …\n")
    run_tests()
