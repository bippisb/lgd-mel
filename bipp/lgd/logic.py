# %%
from bipp.lgd.models import Level, Entity, AdminHierarchy, Variation, DiscoveredVariation
from sqlmodel import create_engine, Session, select

# %%
engine = create_engine("sqlite:///./lgd.db")
gs = Session(engine)


# %%


def get_exact_match(name: str, level_id: int = None, parent_id: int = None) -> list[Entity]:
    with Session(engine) as session:
        name = name.strip().lower()
        query = select(Entity).where(Entity.name == name)
        if level_id:
            query = query.where(Entity.level_id == level_id)
        if parent_id:
            query = query \
                .join(AdminHierarchy, AdminHierarchy.child_id == Entity.id) \
                .where(AdminHierarchy.entity_id == parent_id)

        return session.exec(query).unique().all()

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


def get_matches_using_variations(name: str, level_id: int = None, parent_id: int = None, use_community_variations: bool = False) -> list[tuple[Entity, Variation]]:
    name = name.strip().lower()

    def build_query(M: Variation | DiscoveredVariation):
        query = select(Entity, M) \
            .where(M.name == name) \
            .join(Entity, Entity.id == M.entity_id)

        if level_id:
            query = query.where(Entity.level_id == level_id)
        if parent_id:
            query = query \
                .join(AdminHierarchy, AdminHierarchy.child_id == Entity.id) \
                .where(AdminHierarchy.entity_id == parent_id)

        return query

    with Session(engine) as session:
        query = build_query(Variation)
        results = session.exec(query).all()
        if not use_community_variations:
            return results
        if len(results) == 0:
            query = build_query(DiscoveredVariation)
            results = session.exec(query).all()
            return results
        return []


# %%


def get_matches_using_community_variations(name: str, level_id: int = None, parent_id: int = None) -> list[tuple[Entity, DiscoveredVariation]]:
    query = select(Entity, DiscoveredVariation) \
        .where(DiscoveredVariation.name == name) \
        .join(Entity, Entity.id == DiscoveredVariation.entity_id)

    if level_id:
        query = query.where(Entity.level_id == level_id)
    if parent_id:
        query = query \
            .join(AdminHierarchy, AdminHierarchy.child_id == Entity.id) \
            .where(AdminHierarchy.entity_id == parent_id)
    with Session(engine) as session:
        results = session.exec(query).all()
        matches = set(map(lambda x: x[0], results))
        return [r.model_dump() for r in matches]


# %%


def get_subtree(entity_id):
    pass


# %%


def get_matches(
    name: str,
    level_id: int = None,
    parent_id: int = None,
    with_parents: bool = False,
    with_community_variations: bool = False,
) -> list[dict]:
    # get exact match
    name = name.strip().lower()
    matches = get_exact_match(
        name=name, level_id=level_id, parent_id=parent_id)

    def prepare_repsonse(match: Entity):
        r = dict(
            ** match.model_dump(),
        )
        if with_parents:
            levels = get_levels()
            def get_level_name(id): return [
                lvl for lvl in levels if lvl.id == id][0].name
            parents = get_parents(match.id)
            r["parents"] = [
                dict(
                    **p.model_dump(),
                    level=get_level_name(p.level_id),
                )
                for p in parents
            ]
        return r

    if matches:
        return list(map(prepare_repsonse, matches))

    # match variations
    results = get_matches_using_variations(
        name=name, level_id=level_id, parent_id=parent_id, use_community_variations=with_community_variations)
    matches = set(map(lambda x: x[0], results))
    if matches:
        return list(map(prepare_repsonse, matches))

    return []
    # TODO: filter candidates using admin hierarchy

    # TODO: get_similar_match
    # TODO: get_similar_variation

# %%


def get_levels() -> list[Level]:
    with Session(engine) as session:
        query = select(Level)
        return session.exec(query).all()
# %%


def add_variation(variation_name: str, entity_id: int, email: str) -> Variation:
    variation_name = variation_name.strip().lower()
    email = email.strip().lower()
    with Session(engine) as session:
        q_entity_exists = select(Entity).where(Entity.id == entity_id)
        match= session.exec(q_entity_exists).first()
        if not match:
            raise ValueError("Entity does not exist")

        if match.name == variation_name:
            raise ValueError("Variation name can't be the same as entity name")

        q_variation_exists = select(Variation).where(
            Variation.name == variation_name).where(Variation.entity_id == entity_id)
        if session.exec(q_variation_exists).first():
            raise ValueError("Variation already exists")

        variation = DiscoveredVariation(
            name=variation_name, entity_id=entity_id, proposer_email=email)
        session.add(variation)
        session.commit()
        return variation
