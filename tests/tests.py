import keystone_user
import mock
from nose.tools import assert_equal


def setup_foo_tenant():
    keystone = mock.MagicMock()
    tenant = mock.Mock()
    tenant.id = "21b505b9cbf84bdfba60dc08cc2a4b8d"
    tenant.name = "foo"
    tenant.description = "The foo tenant"
    keystone.tenants.list = mock.Mock(return_value=[tenant])
    return keystone


def test_tenant_exists_when_present():
    """ tenant_exists when tenant does exist"""
    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    assert keystone_user.tenant_exists(keystone, "foo")


def test_tenant_exists_when_absent():
    """ tenant_exists when tenant does not exist"""
    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    assert not keystone_user.tenant_exists(keystone, "bar")


def test_ensure_tenant_exists_when_present():
    """ ensure_tenant_exists when tenant does exists """

    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "foo",
                    "The foo tenant", False)

    # Assertions
    assert not changed
    assert_equal(id, "21b505b9cbf84bdfba60dc08cc2a4b8d")


def test_ensure_tenant_exists_when_absent():
    """ ensure_tenant_exists when tenant does not exist """
    # Setup
    keystone = setup_foo_tenant()
    keystone.tenants.create = mock.Mock(return_value=mock.Mock(
        id="7c310f797aa045898e2884a975ab32ab"))

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "bar",
                    "The bar tenant", False)

    # Assertions
    assert changed
    assert_equal(id, "7c310f797aa045898e2884a975ab32ab")
    keystone.tenants.create.assert_called_with(tenant_name="bar",
                                               description="The bar tenant",
                                               enabled=True)


def test_change_tenant_description():
    """ ensure_tenant_exists with a change in description """
    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "foo",
                    "The foo tenant with a description change", False)

    # Assertions
    assert changed
    assert_equal(id, "21b505b9cbf84bdfba60dc08cc2a4b8d")


@mock.patch('keystone_user.ensure_tenant_exists')
def test_dispatch_tenant_present(mock_ensure_tenant_exists):
    """ dispatch with tenant only"""
    # Setup
    keystone = setup_foo_tenant()
    mock_ensure_tenant_exists.return_value = (True,
                                       "34469137412242129cd908e384717794")

    # Code under test
    res = keystone_user.dispatch(keystone, tenant="bar",
                           tenant_description="This is a bar")

    # Assertions
    mock_ensure_tenant_exists.assert_called_with(keystone, "bar",
                                                "This is a bar", False)
    assert_equal(res,
        dict(changed=True, id="34469137412242129cd908e384717794"))


@mock.patch('keystone_user.ensure_user_exists')
def test_dispatch_user_present(mock_ensure_user_exists):
    """ dispatch with tenant and user"""
    # Setup
    keystone = setup_foo_tenant()
    mock_ensure_user_exists.return_value = (True,
                                       "0a6f3697fc314279b1a22c61d40c0919")

    # Code under test
    res = keystone_user.dispatch(keystone, tenant="foo", user="admin",
                                 email="admin@example.com",
                                 password="12345")

    # Assertions
    mock_ensure_user_exists.assert_called_with(keystone, "admin",
                                               "12345", "admin@example.com",
                                               "foo", False)

    assert_equal(res,
        dict(changed=True, id="0a6f3697fc314279b1a22c61d40c0919"))

