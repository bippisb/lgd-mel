# %%
from bipp.lgd.algorithms import fuzzy_cosine_match
# %%
def test_amritsar():
    candidates = ["Amritpur", "Amritsar", "Amreli", "Amarpur"]
    assert fuzzy_cosine_match("Ambarsar", candidates) == "Amritsar"

