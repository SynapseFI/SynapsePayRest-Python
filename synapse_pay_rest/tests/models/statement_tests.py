import unittest
import pdb
from synapse_pay_rest.tests.fixtures.client import *
from synapse_pay_rest.models import User
from synapse_pay_rest.models import Statement

class StatementTestCases(unittest.TestCase):
    def setUp(self):
        print('\n{0}.{1}'.format(type(self).__name__, self._testMethodName))
        self.client = test_client
        self.user = User.by_id(self.client, '5a271c2592571b0034c0d9d8')

    def test_by_user(self):
        statements = Statement.retrieve(self.user)
        statement = statements[0]
        properties = ['user', '_id', 'client_id', 'date_end', 'date_start', 'ending_balance', 'is_active', 'node_id', 'opening_balance', 'status', 'csv_url', 'json_url', 'pdf_url', 'user_id']

        self.assertIsInstance(statement, Statement)

        for prop in properties:
            self.assertIsNotNone(getattr(statement, prop))

    def test_by_node(self):
        statements = Statement.retrieve(self.user, '5a399beece31670034632427')
        statement = statements[0]
        properties = ['user', '_id', 'client_id', 'date_end', 'date_start', 'ending_balance', 'is_active', 'node_id', 'opening_balance', 'status', 'csv_url', 'json_url', 'pdf_url', 'user_id']

        self.assertIsInstance(statement, Statement)

        for prop in properties:
            self.assertIsNotNone(getattr(statement, prop))
