from ckan.tests.legacy.pylons_controller import PylonsTestCase
from ckan.tests.helpers import FunctionalTestBase

SAML_INFO = [
    {'tenancy': ['']},
    {'tenancy': ['ausgrid=editor']},
    {'tenancy': ['ausgrid=editor|australian-bureau-of-statistics=admin']},
]

PylonsTestCase()


class SimpleNSWTest(PylonsTestCase, FunctionalTestBase):

    def setup(self):
        super(SimpleNSWTest, self).setup()
