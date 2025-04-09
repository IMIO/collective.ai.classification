from collective.ai.classification.browser.controlpanel import IAIClassificationSettings
from collective.ai.core.interfaces import IAIActionsProvider
from collective.ai.summarizer.behaviors.summarizable import IAISummarizable
from collective.ai.summarizer.browser.controlpanel import IAISummarizerSettings
from plone.protect.utils import addTokenToUrl
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer


@implementer(IAIActionsProvider)
class ClassificationsActions:
    def __call__(self, context, request):
        registry = getUtility(IRegistry)
        classification_settings = registry.forInterface(IAIClassificationSettings, check=False)
        results = []
        if not hasattr(classification_settings, "classifications") or not classification_settings.classifications:
            return []

        for i, classification in enumerate(classification_settings.classifications):
            if context.portal_type != classification['portal_type'] or classification['active'] is False:
                continue
            results.append(
                {
                    "title": classification["label"],
                    "description": "",
                    "action": addTokenToUrl(f"{context.absolute_url()}/@@ai-classification-action?classification={i}", request),
                    "selected": False,
                    "icon": "inboxes",
                    "extra": {
                        "id": "plone-contentmenu-actions-" + "id",
                        "separator": None,
                        "class": 'cssClass',
                        "modal": '',
                    },
                    "submenu": None,
                }
            )
        return results
