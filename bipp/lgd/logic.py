# %%
from bipp.lgd.models import Level, Entity, AdminHierarchy, Variation
from sqlmodel import create_engine, Session, select

# %%
engine = create_engine("sqlite:///lgd.db")
gs = Session(engine)


# %%


def get_exact_match(name: str, level_id: int = None) -> list[Entity]:
    with Session(engine) as session:
        name = name.strip().lower()
        query = select(Entity).where(Entity.name == name)
        if level_id:
            query = query.where(Entity.level_id == level_id)
        return session.exec(query).all()

# %%


def get_similar_match(name: str, level_id: int) -> list[Entity]:
    pass


def get_similar_variation(name: str, level_id: int) -> list[Entity]:
    pass

# %%


def get_children(entity_id: int) -> list[Entity]:
    with Session(engine) as session:
        query = select(Entity).from_statement(
            select(AdminHierarchy, Entity)
            .where(AdminHierarchy.entity_id == entity_id)
            .join(Entity, AdminHierarchy.child_id == Entity.id)
        )
        return session.exec(query).all()

# %%


def get_parents(entity_id: int) -> list[Entity]:
    with Session(engine) as session:
        recursive_cte = (
            select(AdminHierarchy)
            .where(AdminHierarchy.child_id == entity_id)
            .cte(recursive=True)
        )

        query = (
            select(AdminHierarchy)
            .from_statement(
                select(recursive_cte)
                .union_all(
                    select(AdminHierarchy)
                    .where(AdminHierarchy.child_id == recursive_cte.c.entity_id)
                )
            )
        )
        links = list(map(lambda x: x[0], session.exec(query).all()))
        entity_ids = list(map(lambda x: x.entity_id, links))

        query = select(Entity).where(Entity.id.in_(entity_ids))
        return session.exec(query).all()
# %%


def get_variations(entity_id: int) -> list[Variation]:
    with Session(engine) as session:
        query = select(Variation).where(Variation.entity_id == entity_id)
        variations = session.exec(query).all()
        return variations

# %%


def get_matches_using_variations(name: str, level_id: int = None) -> list[tuple[Entity, Variation]]:
    name = name.strip().lower()
    with Session(engine) as session:
        query = select(Entity, Variation) \
            .where(Variation.name == name) \
            .join(Entity, Entity.id == Variation.entity_id)
        if level_id:
            query = query.where(Entity.level_id == level_id)
        return session.exec(query).all()

# %%


def get_subtree(entity_id):
    pass


# %%


def find_exact_match_using_hierarchies(name: str, level: int = None) -> list[Entity]:
    pass

# %%


def get_matches(name: str, level_id: int = None, hierarchy: list[tuple[str, int]] = None) -> list[dict]:
    # get exact match
    name = name.strip().lower()
    matches = get_exact_match(name=name, level_id=level_id)

    def prepare_repsonse(match: Entity):
        return dict(
            ** match.model_dump(),
            parents=get_parents(match.id),
        )

    if matches:
        return list(map(prepare_repsonse, matches))

    # match variations
    results = get_matches_using_variations(name=name, level_id=level_id)
    matches = list(map(lambda x: x[0], results))
    if matches:
        return list(map(prepare_repsonse, matches))

    # TODO: filter candidates using admin hierarchy
    
    # TODO: get_similar_match
    # TODO: get_similar_variation

# %%


def get_levels() -> list[Level]:
    with Session(engine) as session:
        query = select(Level)
        return session.exec(query).all()
# %%
