# -*- coding: utf-8 -*-
from collective.ai.core.browser.controlpanel import AICoreControlPanelForm, AICoreControlPanelFormWrapper
from collective.ai.core.interfaces import ICollectiveAIControlPanelFieldProvider
from collective.ai.summarizer import _
from collective.z3cform.datagridfield.blockdatagridfield import BlockDataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.registry.interfaces import IRegistry
from plone.z3cform import layout
from plone.z3cform.fieldsets.interfaces import IFormExtender
from z3c.form import field
from z3c.form.browser.password import PasswordFieldWidget
from z3c.form.interfaces import IFormLayer
from zope import schema
from plone.supermodel import model
from zope.component import adapter
from zope.interface import alsoProvides, provider, implementer, Interface


class IAIClassificationRow(Interface):
    label = schema.TextLine(
        title=_("Label"),
        required=True,
    )

    model = schema.Choice(
        title=_("Model"),
        vocabulary="collective.ai.core.vocabularies.TextCompletionModelsVocabulary",
        required=True,
    )

    portal_type = schema.Choice(
        title=_("Portal type"),
        vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes",
        required=True,
    )

    source_field = schema.TextLine(
        title=_("Source field"),
        required=True,
    )

    prompt = schema.Text(
        title=_("Prompt"),
        default="""Voici un texte :
'''
{}
'''
Résume ce texte en 2 paragraphes. Sois clair et concis.
        """,
        required=False,
    )

    active = schema.Bool(
        title=_("Active"),
        required=False,
        default=True,
    )

class IAIClassificationSettings(Interface):
    directives.widget('classifications',
                      BlockDataGridFieldFactory,
                      allow_reorder=True,
                      auto_append=False)
    classifications = schema.List(
        title=_("classifications"),
        value_type=DictRow(
            title=_("classifications"),
            schema=IAIClassificationRow,
        ),
        required=False,
    )

class AIClassificationControlPanelForm(RegistryEditForm):
    label = _("AI classification settings")
    schema = IAIClassificationSettings


AIClassificationControlPanelView = layout.wrap_form(
    AIClassificationControlPanelForm, AICoreControlPanelFormWrapper
)
