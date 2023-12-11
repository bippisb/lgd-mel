from fastapi import FastAPI
from bipp.lgd.types import MatchItem
from bipp.lgd.logic import get_matches, get_levels

app = FastAPI()

LevelNameToLevelIdMapping = {
    level.name: level.id
    for level in get_levels()
}
LevelIdToLevelNameMapping = {
    val: key
    for key, val in LevelNameToLevelIdMapping.items()
}


@app.get("/levels")
def levels():
    return get_levels()


@app.post("/match/entity/")
def lgd_match(item: MatchItem):
    name = item.name.strip().lower()
    if item.level:
        level_id = LevelNameToLevelIdMapping[item.level.name]
        matches = get_matches(name=name, level_id=level_id)
    else:
        matches = get_matches(name=name)
    if not matches:
        return []
    return [
        dict(
            ** match,
            level=LevelIdToLevelNameMapping[match["level_id"]],
        )
        for match in matches
    ]
