import unittest

from src.bedrock_embeddings import cosine_similarity


class CosineSimilarityTest(unittest.TestCase):
    def test_identical_vectors_have_similarity_one(self) -> None:
        self.assertAlmostEqual(1.0, cosine_similarity([1, 2, 3], [1, 2, 3]))

    def test_orthogonal_vectors_have_similarity_zero(self) -> None:
        self.assertAlmostEqual(0.0, cosine_similarity([1, 0], [0, 1]))

    def test_opposite_vectors_have_similarity_negative_one(self) -> None:
        self.assertAlmostEqual(-1.0, cosine_similarity([1, 0], [-1, 0]))

    def test_dimension_mismatch_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cosine_similarity([1, 2], [1])

