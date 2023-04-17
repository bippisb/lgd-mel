# %%
from fuzzywuzzy import fuzz
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from typing import List

# %%


def fuzzy_cosine_match(input_name: str, candidate_names: List[str], similarity=0.75, fuzzy_match=0.7, errors="ignore"):
    """
    Compares an input name to a list of candidate names
    using both fuzzy search and cosine similarity,
    returning the name with the highest combined score.

    Args:
        input_name (str): The input name for which the best match needs to be found.
        candidate_names (list[str]): A list of candidate names.
        similarity (float, optional): The weightage of cosine similarity score (default 0.75).
        fuzzy_match (float, optional): The weightage of fuzzy matcher (default 0.7).

    Returns:
        str: The best matching name from the candidate set based on the combined fuzzy search and cosine similarity
             scores.
    """

    try:
        # Compute the fuzzy search score
        fuzzy_scores = [fuzz.token_sort_ratio(
            name, input_name) for name in candidate_names]

        # Compute the cosine similarity score
        vectorizer = CountVectorizer().fit_transform(
            [input_name] + candidate_names)
        cosine_similarities = cosine_similarity(
            vectorizer[0:1], vectorizer[1:]).flatten()

        # Combine the fuzzy search and cosine similarity scores
        scores = [fuzzy_match * fuzzy_scores[i] + similarity *
                  cosine_similarities[i] for i in range(len(candidate_names))]

        # Find the best matching name based on the combined score
        best_match = candidate_names[scores.index(max(scores))]

        # Return the best matching name
        return best_match

    except Exception as e:
        if errors == "raise":
            raise e
        else:
            return None

# %%
