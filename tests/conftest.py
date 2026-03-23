import pytest


@pytest.fixture
def mock_role(mocker):
    role = mocker.Mock()
    role.name = "admin"
    return role

@pytest.fixture
def mock_user(mocker, mock_role):
    user = mocker.Mock()
    user.id = 1
    user.name = "name"
    user.is_active = True
    user.must_change_password = False
    user.password_hash = "hashed_password"
    user.roles = [mock_role]
    user.email = "email@email.ru"
    return user

@pytest.fixture
def mock_branch(mocker):
    branch = mocker.Mock()
    branch.id = 1
    branch.name = "name"
    branch.inn = "1234567"
    branch.is_archived = False
    return branch

@pytest.fixture
def mock_user_data(mocker, mock_role):
    data = mocker.Mock()
    data.email = "email@email.ru"
    data.password = "password1"
    data.inn = "1234567"
    data.company = "company"
    data.branch_id = 1
    data.roles = [mock_role]
    return data

@pytest.fixture
def mock_jwt(mocker):
    jwt = mocker.Mock()
    jwt.jti = "jti"
    refresh = mocker.Mock()
    refresh.token = "test_refresh_token"
    refresh.exp = 3600
    jwt.create_access.return_value = "test_access_token"
    jwt.create_refresh.return_value = refresh
    return jwt
