# -*- coding: utf-8 -*-
import json
import logging

from collective.ai.classification.browser.controlpanel import IAIClassificationSettings
from collective.ai.core.browser.controlpanel import IAICoreSettings
from collective.ai.core.services import IAIAPIService
from plone import api
from plone.dexterity.utils import iterSchemataForType
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getUtility, adapter
from zope.component._api import getAdapter, getMultiAdapter
from zope.interface import implementer, Interface

logger = logging.getLogger("collective.ai.summarizer")


class IAIClassificationAdapter(Interface):
    """"""

    def __init__(self, context, request):
        pass


@implementer(IAIClassificationAdapter)
@adapter(Interface)
class AIClassificationAdapter:
    """Handle classification operations on an object"""

    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST
        registry = getUtility(IRegistry)
        self.ai_settings = registry.forInterface(IAICoreSettings, check=False)
        self.classification_settings = registry.forInterface(IAIClassificationSettings, check=False)
        self.classification_config = self.classification_settings.classifications[
            int(self.request.form['classification'])]

    def source_field(self):
        return self.classification_config['source_field']

    def prompt_context(self):
        serializer = getMultiAdapter((self.context, self.request), ISerializeToJson)
        return serializer()

    def prompt(self):
        return self.classification_config['prompt']

    def classify(self):
        config_id, model_id = self.classification_config["model"].split("__")
        service_type = self.ai_settings.text_completion_services[int(config_id)]["service_type"]
        service = getAdapter(self.context, IAIAPIService, service_type)
        service(int(config_id), model_id)
        portal_type = self.context.portal_type
        field, schema = _get_field_and_schema_for_fieldname(self.source_field(), portal_type)
        tokens, values, titles = _get_vocabulary_values(self.context, self.source_field())
        response = service.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user",
                 "content": self.prompt().format(self.prompt_context())}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "classification_response",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "string",
                                "anyOf": [{"const": v} for v in values]
                            }
                        },
                        "required": ["value"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            })
        try:
            res = response.choices[0].message.content
            res = json.loads(res)
            setattr(self.context, self.source_field(), res["value"])
            self.context.reindexObject()
        except:
            api.portal.show_message(message='There was an error during the classification process, check the configuration of the model and the prompt.',)



def _get_field_and_schema_for_fieldname(field_id, portal_type):
    """Get field and its schema from a portal_type."""
    # Turn form.widgets.IDublinCore.title into title
    field_id = field_id.split(".")[-1]
    for schema in iterSchemataForType(portal_type):
        field = schema.get(field_id, None)
        if field is not None:
            return (field, schema)


def _get_vocabulary_values(context, field_name):
    field, _schema = _get_field_and_schema_for_fieldname(field_name, context.portal_type)

    # Bind the field to the actual context (important for dynamic vocabularies).
    bound_field = field.bind(context)

    vocab = bound_field.vocabulary
    # vocab is an instance of zope.schema.interfaces.IVocabulary

    # If you want the raw token strings:
    tokens = [term.token for term in vocab]

    # If you want the underlying Python values:
    values = [term.value for term in vocab]

    # If you want the human-readable titles:
    titles = [term.title for term in vocab]

    return tokens, values, titles
