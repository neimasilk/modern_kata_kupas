# tests/test_benchmark.py
"""
Benchmark and performance tests for ModernKataKupas.

These tests measure the performance of key operations and ensure
they complete within acceptable time bounds.
"""
import time
import statistics
from typing import List, Tuple
import pytest

from modern_kata_kupas import ModernKataKupas


# Sample words for benchmarking - covering various morphological patterns
BENCHMARK_WORDS = [
    # Simple root words
    "rumah", "makan", "tulis", "baca", "jalan",
    # Words with prefixes
    "menulis", "membaca", "berlari", "terbang", "dipukul",
    # Words with suffixes
    "makanan", "tulisan", "bacaan", "jalanan", "minuman",
    # Words with prefixes and suffixes
    "menuliskan", "membacakan", "membuatkan", "menjalankan",
    # Complex morphology
    "mempertanyakan", "memperbarui", "memperjuangkan",
    "keberlangsungan", "ketidakadilan", "mempertanggungjawabkan",
    # Reduplication
    "rumah-rumah", "buku-buku", "sayur-mayur", "bolak-balik",
    # Dwipurwa
    "lelaki", "sesama", "tetamu",
    # Loanwords with affixes
    "di-download", "mem-backup",
]

# Extended word list for stress testing
STRESS_TEST_WORDS = BENCHMARK_WORDS * 10  # 270 words


class TestBenchmarkSegmentation:
    """Benchmark tests for segmentation performance."""

    @pytest.fixture(scope="class")
    def mkk(self) -> ModernKataKupas:
        """Create a single ModernKataKupas instance for all tests in this class."""
        return ModernKataKupas()

    def test_single_word_segmentation_speed(self, mkk: ModernKataKupas):
        """Test that single word segmentation completes within acceptable time."""
        max_time_per_word_ms = 100  # Maximum 100ms per word (accounting for cold start)

        # Warmup run to ensure caches are populated
        for word in BENCHMARK_WORDS[:5]:
            mkk.segment(word)

        for word in BENCHMARK_WORDS[:10]:
            start = time.perf_counter()
            mkk.segment(word)
            elapsed_ms = (time.perf_counter() - start) * 1000

            assert elapsed_ms < max_time_per_word_ms, (
                f"Segmentation of '{word}' took {elapsed_ms:.2f}ms, "
                f"exceeding {max_time_per_word_ms}ms limit"
            )

    def test_batch_segmentation_throughput(self, mkk: ModernKataKupas):
        """Test batch segmentation throughput."""
        min_words_per_second = 100  # At least 100 words per second

        start = time.perf_counter()
        for word in STRESS_TEST_WORDS:
            mkk.segment(word)
        elapsed = time.perf_counter() - start

        words_per_second = len(STRESS_TEST_WORDS) / elapsed

        assert words_per_second >= min_words_per_second, (
            f"Throughput {words_per_second:.1f} words/sec is below "
            f"minimum {min_words_per_second} words/sec"
        )

    def test_segmentation_latency_distribution(self, mkk: ModernKataKupas):
        """Test that segmentation latency is consistent (low variance)."""
        latencies: List[float] = []

        for word in BENCHMARK_WORDS:
            start = time.perf_counter()
            mkk.segment(word)
            latencies.append((time.perf_counter() - start) * 1000)

        mean_latency = statistics.mean(latencies)
        stdev_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        max_latency = max(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        # P95 should be less than 3x mean (reasonable consistency)
        assert p95_latency < mean_latency * 3, (
            f"P95 latency ({p95_latency:.2f}ms) is more than 3x mean ({mean_latency:.2f}ms)"
        )

        # Log statistics for reference
        print(f"\nSegmentation Latency Statistics:")
        print(f"  Mean: {mean_latency:.3f}ms")
        print(f"  Stdev: {stdev_latency:.3f}ms")
        print(f"  Max: {max_latency:.3f}ms")
        print(f"  P95: {p95_latency:.3f}ms")


class TestBenchmarkReconstruction:
    """Benchmark tests for reconstruction performance."""

    @pytest.fixture(scope="class")
    def mkk(self) -> ModernKataKupas:
        """Create a single ModernKataKupas instance for all tests in this class."""
        return ModernKataKupas()

    @pytest.fixture(scope="class")
    def segmented_words(self, mkk: ModernKataKupas) -> List[Tuple[str, str]]:
        """Pre-segment words for reconstruction testing."""
        return [(word, mkk.segment(word)) for word in BENCHMARK_WORDS]

    def test_single_reconstruction_speed(
        self, mkk: ModernKataKupas, segmented_words: List[Tuple[str, str]]
    ):
        """Test that single word reconstruction completes within acceptable time."""
        max_time_per_word_ms = 50  # Maximum 50ms per word

        for original, segmented in segmented_words[:10]:
            if segmented != original:  # Only test actual segmented words
                start = time.perf_counter()
                mkk.reconstruct(segmented)
                elapsed_ms = (time.perf_counter() - start) * 1000

                assert elapsed_ms < max_time_per_word_ms, (
                    f"Reconstruction of '{segmented}' took {elapsed_ms:.2f}ms, "
                    f"exceeding {max_time_per_word_ms}ms limit"
                )

    def test_roundtrip_performance(self, mkk: ModernKataKupas):
        """Test segment -> reconstruct roundtrip performance."""
        min_roundtrips_per_second = 50  # At least 50 roundtrips per second

        start = time.perf_counter()
        for word in BENCHMARK_WORDS:
            segmented = mkk.segment(word)
            mkk.reconstruct(segmented)
        elapsed = time.perf_counter() - start

        roundtrips_per_second = len(BENCHMARK_WORDS) / elapsed

        assert roundtrips_per_second >= min_roundtrips_per_second, (
            f"Roundtrip throughput {roundtrips_per_second:.1f}/sec is below "
            f"minimum {min_roundtrips_per_second}/sec"
        )


class TestBenchmarkInitialization:
    """Benchmark tests for initialization performance."""

    def test_initialization_time(self):
        """Test that ModernKataKupas initialization is fast enough."""
        max_init_time_ms = 2000  # Maximum 2 seconds for initialization

        start = time.perf_counter()
        ModernKataKupas()
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < max_init_time_ms, (
            f"Initialization took {elapsed_ms:.2f}ms, exceeding {max_init_time_ms}ms limit"
        )

        print(f"\nInitialization time: {elapsed_ms:.2f}ms")

    def test_multiple_initializations(self):
        """Test that multiple initializations don't have memory leaks or slowdowns."""
        init_times: List[float] = []

        for _ in range(5):
            start = time.perf_counter()
            ModernKataKupas()
            init_times.append((time.perf_counter() - start) * 1000)

        # Later initializations shouldn't be significantly slower
        first_init = init_times[0]
        last_init = init_times[-1]

        assert last_init < first_init * 2, (
            f"Last initialization ({last_init:.2f}ms) is more than 2x "
            f"first initialization ({first_init:.2f}ms)"
        )


class TestBenchmarkDictionary:
    """Benchmark tests for dictionary lookup performance."""

    @pytest.fixture(scope="class")
    def mkk(self) -> ModernKataKupas:
        """Create a single ModernKataKupas instance for all tests in this class."""
        return ModernKataKupas()

    def test_dictionary_lookup_speed(self, mkk: ModernKataKupas):
        """Test that dictionary lookups are fast (O(1) expected for set)."""
        test_words = ["rumah", "makan", "tulis", "baca", "jalan"] * 1000
        max_time_per_1000_lookups_ms = 10  # Max 10ms for 1000 lookups

        start = time.perf_counter()
        for word in test_words:
            mkk.dictionary.is_kata_dasar(word)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < max_time_per_1000_lookups_ms * 5, (
            f"5000 lookups took {elapsed_ms:.2f}ms, too slow"
        )

        lookups_per_second = len(test_words) / (elapsed_ms / 1000)
        print(f"\nDictionary lookup rate: {lookups_per_second:.0f} lookups/sec")


# Pytest benchmark markers for optional detailed benchmarking
# Run with: pytest tests/test_benchmark.py -v -s
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
