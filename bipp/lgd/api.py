from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bipp.lgd.types import MatchItem
from bipp.lgd.logic import get_matches, get_levels

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
        lvl = item.level.name
        level_id = LevelNameToLevelIdMapping[lvl]
        matches = get_matches(
            name=name,
            level_id=level_id,
            parent_id=item.parent_id,
        )
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
