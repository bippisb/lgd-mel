# %%
from bipp.lgd.models import Level, Entity, AdminHierarchy, Variation
from sqlmodel import create_engine, Session, select

# %%
engine = create_engine("sqlite:///D:/bippisb/lgd-mel/bipp/lgd/lgd.db")
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


def get_matches_using_variations(name: str, level_id: int = None, parent_id: int = None) -> list[tuple[Entity, Variation]]:
    name = name.strip().lower()
    with Session(engine) as session:
        query = select(Entity, Variation) \
            .where(Variation.name == name) \
            .join(Entity, Entity.id == Variation.entity_id)
        if level_id:
            query = query.where(Entity.level_id == level_id)
        if parent_id:
            query = query \
                .join(AdminHierarchy, AdminHierarchy.child_id == Entity.id) \
                .where(AdminHierarchy.entity_id == parent_id)
        return session.exec(query).all()

# %%


def get_subtree(entity_id):
    pass


# %%


def get_matches(name: str, level_id: int = None, parent_id: int = None, with_parents: bool = False) -> list[dict]:
    # get exact match
    name = name.strip().lower()
    matches = get_exact_match(
        name=name, level_id=level_id, parent_id=parent_id)

    def prepare_repsonse(match: Entity):
        r = dict(
            ** match.model_dump(),
        )
        if with_parents:
            r["parents"] = get_parents(match.id)
        return r

    if matches:
        return list(map(prepare_repsonse, matches))

    # match variations
    results = get_matches_using_variations(
        name=name, level_id=level_id, parent_id=parent_id)
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


def add_variation(variation_name: str, entity_id: int) -> Variation:
    variation_name = variation_name.strip().lower()
    with Session(engine) as session:
        q_entity_exists = select(Entity).where(Entity.id == entity_id)
        if not session.exec(q_entity_exists).first():
            raise ValueError("Entity does not exist")

        q_entity_name_same_as_variation = select(
            Entity).where(Entity.name == variation_name)
        if session.exec(q_entity_name_same_as_variation).first():
            raise ValueError("Variation name can't be the same as entity name")

        q_variation_exists = select(Variation).where(
            Variation.name == variation_name).where(Variation.entity_id == entity_id)
        if session.exec(q_variation_exists).first():
            raise ValueError("Variation already exists")

        variation = Variation(name=variation_name, entity_id=entity_id)
        session.add(variation)
        session.commit()
        return variation
