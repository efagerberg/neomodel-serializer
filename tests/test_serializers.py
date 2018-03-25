import json

from mock import patch

from neomodel import (
    db, clear_neo4j_database,
    ArrayProperty, IntegerProperty,
    StructuredNode, StructuredRel,
    StringProperty, RelationshipFrom
)
import pytest
from neomodel_serializer.serializers import StructuredThingSerializer


class Person(StructuredNode):
    name = StringProperty(required=True)


class ActorRel(StructuredRel):
    roles = ArrayProperty(StringProperty())


class Movie(StructuredNode):
    actors = RelationshipFrom(Person, 'ACTED_IN', model=ActorRel)
    directors = RelationshipFrom(Person, 'DIRECTED')

    released = IntegerProperty(required=True)
    tagline = StringProperty()
    title = StringProperty(unique_index=True, required=True)


@pytest.fixture()
def movie():
    yield Movie(title="Space Cop", released=2016).save()
    clear_neo4j_database(db)


@pytest.fixture()
def movies():
    for i in range(2):
        Movie(title=i, released=2016).save()
    clear_neo4j_database(db)


@pytest.fixture()
def mock_isinstance():
    path = 'neomodel_serializer.serializers.isinstance'
    with patch(path) as m:
        yield m


def test_parses_data(movie):
    """StructuredThingSerializer should parse data from instance."""
    p = Person(name="Mike Stoklasa").save()
    movie.directors.connect(p)
    actor_rel = movie.actors.connect(p, {'roles': ['Detective Ted Cooper']})

    expected = {
        'id': movie.id,
        'actors': [
            {'id': p.id,
             'name': p.name,
             'roles': actor_rel.roles}
        ],
        'directors': [
            {'id': p.id,
             'name': p.name}
        ],
        'released': movie.released,
        'tagline': movie.tagline,
        'title': movie.title,
    }
    actual = StructuredThingSerializer(movie).data
    assert actual == expected


def test_parses_only_certain_fields(movie):
    """"StructuredThingSerializer should exclude fields not
    declared in fields"""
    expected = {
        'title': movie.title,
        'released': movie.released,
    }
    actual = StructuredThingSerializer(
        movie, fields=('title', 'released')).data
    assert actual == expected


def test_serializes_structured_node_without_prop_or_rel_defs():
    """StructuredThingSerializer should handle a StructuredNode
    without any properties or relationship definitions."""
    class Foo(StructuredNode):
        pass

    x = Foo().save()
    expected = json.dumps({'id': x.id})
    actual = StructuredThingSerializer(x).serialized_data
    assert actual == expected


def test_raises_on_non_property_non_rel_def(movie, mock_isinstance):
    """StructuredThingSerializer should raise ValueError
    when a prop that is passed is not a Property or
    RelationshipDefinition"""
    mock_isinstance.return_value = False
    with pytest.raises(ValueError):
        StructuredThingSerializer(movie)


def test_serialize_many(movies):
    """StructuredThingSerializer should be able to serialize
    many movies"""
    qs = Movie.nodes
    expected = [{
        'id': movie.id,
        'actors': [],
        'directors': [],
        'released': movie.released,
        'tagline': movie.tagline,
        'title': movie.title,
    } for movie in qs]
    actual = StructuredThingSerializer(qs, many=True).data
    assert actual == expected
