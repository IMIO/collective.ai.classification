# -*- coding: utf-8 -*-
import json
import logging

from collective.ai.classification.browser.controlpanel import IAIClassificationSettings
from collective.ai.core.browser.controlpanel import IAICoreSettings
from collective.ai.core.services import IAIAPIService
from plone.dexterity.utils import iterSchemataForType
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, adapter
from zope.component._api import getAdapter
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

    def prompt(self):
        return self.classification_config['prompt']

    def classify(self):
        config_id, model_id = self.classification_config["model"].split("__")
        service_type = self.ai_settings.text_completion_services[int(config_id)]["service_type"]
        service = getAdapter(self.context, IAIAPIService, service_type)
        service(int(config_id), model_id)
        portal_type = self.context.portal_type
        testy = _get_field_and_schema_for_fieldname("category", portal_type)
        tokens, values, titles = _get_vocabulary_values(self.context, "category")
        response = service.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are a helpful classification assistant. Classify the following content:"},
                {"role": "user",
                 "content": "Here is the content:\n\n'''" + getattr(self.context, "text").output + "''' \n Catégorie:"}
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
        res = response.choices[0].message.content
        res = res.replace("\\\\xe9", "é")
        try:
            res = json.loads(res)
            setattr(self.context, "category", res["value"])
        except:
            pass



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
