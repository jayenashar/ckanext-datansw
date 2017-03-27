from ckanext.nsw.tests import SimpleNSWTest, SAML_INFO
import nose.tools as nt
from ckanext.nsw.saml2_mapper import nsw_org_mapper


class TestSaml2Mapper(SimpleNSWTest):

    def setup(self):
        super(TestSaml2Mapper, self).setup()

    def test_saml2_mapper_none(self):

        result = nsw_org_mapper(SAML_INFO[0])
        nt.assert_equals(result, None)

    def test_saml2_mapper_single_role(self):

        result = nsw_org_mapper(SAML_INFO[1])
        nt.assert_equals(result, {'ausgrid': {'capacity': 'editor'}})

    def test_saml2_mapper_roles(self):

        result = nsw_org_mapper(SAML_INFO[2])
        nt.assert_equals(result, {
            'ausgrid': {'capacity': 'editor'},
            'australian-bureau-of-statistics': {'capacity': 'admin'}}
        )
