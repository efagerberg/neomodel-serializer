from collections import OrderedDict
import json

from six import iteritems

from neomodel import Property
from neomodel.relationship_manager import RelationshipDefinition


class StructuredThingSerializer(object):
    """Initially made to only handle StructuredNodes
    but found that it also worked for StructuredRels."""

    def __init__(self, *args, **kwargs):
        """
        Args:
            instance (StructuredNode/StructuredRel): The thing to serialize.
            fields (str[], optional): Fields to include.
                                      Excludes subobject fields.
        """
        self.instance = args[0]
        self.fields = kwargs.get('fields', '__all__')
        self.many = kwargs.get('many')

        if self.many:
            self.data = []
            for i in self.instance:
                entry_data = StructuredThingSerializer(i).data
                self.data.append(entry_data)
        else:
            self.data = OrderedDict()
            props = self.instance.defined_properties()

            if self.should_include('id'):
                self.data['id'] = self.instance.id

            self.process_properties(props)
        self.serialized_data = json.dumps(self.data)

    def should_include(self, key):
        return key in self.fields or self.fields == '__all__'

    def process_properties(self, props):
        for prop in iteritems(props):
            self.process_property(prop)

    def process_property(self, prop):
        _, value = prop
        if isinstance(value, Property):
            self.process_neomodel_property(prop)
        elif isinstance(value, RelationshipDefinition):
            self.process_relationship_definition(prop)
        else:
            # If we get here, chances are neomodel has changed
            msg = "Unexpected property received: {}".format(prop)
            raise ValueError(msg)

    def process_neomodel_property(self, prop):
        key, _ = prop
        if self.should_include(key):
            self.data[key] = getattr(self.instance, key)

    def process_relationship_definition(self, prop):
        key, value = prop
        if self.should_include(key):
            rel_def = getattr(self.instance, key)
            self.process_rel_def_nodes(rel_def, key)

    def process_rel_def_nodes(self, rel_def, key):
        self.data[key] = []
        for node in rel_def:
            self.process_rel_def_node(rel_def, node, key)

    def process_rel_def_node(self, rel_def, node, key):
        rel_def_data = StructuredThingSerializer(node).data
        rels = rel_def.all_relationships(node)

        self.process_relationships(rels, rel_def_data, key)

    def process_relationships(self, rels, rel_def_data, key):
        for rel in rels:
            self.process_relationship(rel, rel_def_data, key)

        self.data[key].append(rel_def_data)

    def process_relationship(self, rel, rel_def_data, key):
        rel_data = StructuredThingSerializer(rel).data
        rel_data.pop('id')

        if rel_data:
            rel_def_data.update(rel_data)
