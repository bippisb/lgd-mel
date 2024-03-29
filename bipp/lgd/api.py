from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bipp.lgd.types import MatchItem, AddVariationPayload

from bipp.lgd.logic import get_matches, get_levels, add_variation

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
def lgd_match(items: MatchItem | list[MatchItem]):
    def get_match_for_one_item(item):
        name = item.name.strip().lower()
        if item.level:
            lvl = item.level.name
            level_id = LevelNameToLevelIdMapping[lvl]
            matches = get_matches(
                name=name,
                level_id=level_id,
                parent_id=item.parent_id,
                with_parents=item.with_parents
            )
        else:
            matches = get_matches(name=name, with_parents=item.with_parents)
        if not matches:
            return []
        return [
            dict(
                ** match,
                level=LevelIdToLevelNameMapping[match["level_id"]],
            )
            for match in matches
        ]
    if isinstance(items, list):
        return [get_match_for_one_item(item) for item in items]
    else:
        return get_match_for_one_item(items)


@app.post("/add/variation/")
def add_variation_endpoint(payload: AddVariationPayload):
    try:
        variation = add_variation(
            variation_name=payload.variation, entity_id=payload.entity_id, email=payload.email)
        return variation
    except ValueError as e:
        return HTTPException(status_code=404, detail=e)
