import pytest


@pytest.fixture
def mock_role(mocker):
    role = mocker.Mock()
    role.name = "admin"
    return role

@pytest.fixture
def mock_user(mocker, mock_role):
    user = mocker.Mock()
    user.is_active = True
    user.must_change_password = False
    user.password_hash = "hashed_password"
    user.roles = [mock_role]
    user.email = "email@email.ru"
    return user

@pytest.fixture
def mock_user_data(mocker):
    data = mocker.Mock()
    data.email = "email@email.ru"
    data.password = "password1"
    data.inn = "1234567"
    data.company = "company"
    return data

@pytest.fixture
def mock_jwt(mocker):
    jwt = mocker.Mock()
    refresh = mocker.Mock()
    refresh.token = "test_refresh_token"
    refresh.exp = 3600
    jwt.create_access.return_value = "test_access_token"
    jwt.create_refresh.return_value = refresh
    return jwt