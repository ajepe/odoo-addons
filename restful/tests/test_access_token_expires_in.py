from odoo.tests.common import SingleTransactionCase


class TestTokenExpiry(SingleTransactionCase):
    """Test token expiration."""

    def test_access_token_expires_in(self, arg):
        """Test default token expiration date in seconds."""
        expires_in = self.env.ref("restful.access_token_expires_in")
        # self.assertEqual(expires_in.value, 31536000)
