# -*- coding: utf-8 -*-
import logging

from Products.Five.browser import BrowserView
from collective.ai.classification.adapters import IAIClassificationAdapter

logger = logging.getLogger("collective.ai.classifier")


class AIClassifierAction(BrowserView):

    def available(self):
        return True

    def __call__(self):
        handler = IAIClassificationAdapter(self.context)
        handler.classify()
        self.request.response.redirect(self.context.absolute_url())
