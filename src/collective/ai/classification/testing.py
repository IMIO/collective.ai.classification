# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2

import collective.ai.classification


class CollectiveAiClassificationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.ai.classification)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.ai.classification:default')


COLLECTIVE_AI_CLASSIFICATION_FIXTURE = CollectiveAiClassificationLayer()


COLLECTIVE_AI_CLASSIFICATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_AI_CLASSIFICATION_FIXTURE,),
    name='CollectiveAiClassificationLayer:IntegrationTesting',
)


COLLECTIVE_AI_CLASSIFICATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_AI_CLASSIFICATION_FIXTURE,),
    name='CollectiveAiClassificationLayer:FunctionalTesting',
)


COLLECTIVE_AI_CLASSIFICATION_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_AI_CLASSIFICATION_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveAiClassificationLayer:AcceptanceTesting',
)
