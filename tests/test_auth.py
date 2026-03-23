import pytest
from app.config.config import ApplicationException
from app.auth.service import login_user, signup_user, change_user_password, update_tokens


class TestLogin:
    @pytest.fixture
    def login_happy_path(self, mocker, mock_user, mock_jwt):
        mocker.patch(
            "app.auth.service.get_user_by_email", 
            new_callable=mocker.AsyncMock, 
            return_value=mock_user
        )
        mocker.patch("app.auth.service.verify_password", return_value=True)
        mocker.patch(
            "app.auth.service.add_refresh_jwt", 
            new_callable=mocker.AsyncMock, 
            return_value=None
        )
        mocker.patch("app.auth.service.JWTService", return_value=mock_jwt)

    @pytest.mark.asyncio
    async def test_success_login(self, login_happy_path):
        result = await login_user(None, "test@test.com", "password1", "device")
        assert result.access == "test_access_token"
        assert result.refresh == "test_refresh_token"
        assert result.change_password is False

    @pytest.mark.asyncio
    async def test_user_not_found(self, mocker, login_happy_path):
        mocker.patch(
            "app.auth.service.get_user_by_email", 
            new_callable=mocker.AsyncMock, 
            return_value=None
        )
        with pytest.raises(ApplicationException) as e:
            await login_user(None, "test@test.com", "password1", "device")

        assert e.value.code == 401

    @pytest.mark.asyncio
    async def test_wrong_password(self, mocker, login_happy_path):
        mocker.patch("app.auth.service.verify_password", return_value=False)

        with pytest.raises(ApplicationException) as e:
            await login_user(None, "test@test.com", "password1", "device")

        assert e.value.code == 401


class TestSignup:
    @pytest.fixture
    def signup_happy_path(self, mocker, mock_branch, mock_user):
        mocker.patch(
            "app.auth.service.get_user_by_email", 
            new_callable=mocker.AsyncMock,
            return_value=None
        )
        mocker.patch("app.auth.service.check_password", return_value=None)
        mocker.patch("app.auth.service.add_branch", new_callable=mocker.AsyncMock, return_value=mock_branch)
        mocker.patch("app.auth.service.hash_password", return_value="hashed")
        mocker.patch("app.auth.service.add_user", new_callable=mocker.AsyncMock, return_value=mock_user)
        mocker.patch("app.auth.service.add_user_role", new_callable=mocker.AsyncMock, return_value=None)   

    @pytest.mark.asyncio
    async def test_success_signup(self, signup_happy_path, mock_user_data): 
        result = await signup_user(None, mock_user_data)
        assert result.get("company") == "company"

    @pytest.mark.asyncio
    async def test_user_exists(self, signup_happy_path, mocker, mock_user, mock_user_data):
        mocker.patch(
            "app.auth.service.get_user_by_email", 
            new_callable=mocker.AsyncMock,
            return_value=mock_user
        )
        with pytest.raises(ApplicationException) as e:
            await signup_user(None, mock_user_data)

        assert e.value.code == 400
    

class TestChangePassword:
    @pytest.fixture
    def change_password_happy_path(self, mocker, mock_user):
        mock_user.must_change_password = True
        mocker.patch(
            "app.auth.service.get_user_by_id",
            new_callable=mocker.AsyncMock,
            return_value=mock_user
        )
        mocker.patch("app.auth.service.check_password", return_value=None)
        mocker.patch("app.auth.service.hash_password", return_value="hashed")
        mocker.patch(
            "app.auth.service.update_user_password", 
            new_callable=mocker.AsyncMock, 
            return_value=None
        )

    @pytest.mark.asyncio
    async def test_user_not_found(self, mocker, change_password_happy_path):
        mocker.patch(
            "app.auth.service.get_user_by_id", 
            new_callable=mocker.AsyncMock, 
            return_value=None
        )
        with pytest.raises(ApplicationException) as e:
            await change_user_password(None, 1, "password1")

        assert e.value.code == 401
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, change_password_happy_path):
        result = await change_user_password(None, 1, "password1")
        assert result == "email@email.ru"


class TestUpdateTokens:
    @pytest.fixture
    def update_tokens_happy_path(self, mocker, mock_user, mock_jwt):
        mocker.patch(
            "app.auth.service.verify_refresh_jwt",
            new_callable=mocker.AsyncMock,
            return_value=mocker.Mock(user_id=1)
        )
        mocker.patch(
            "app.auth.service.get_user_by_id",
            new_callable=mocker.AsyncMock,
            return_value=mock_user
        )
        mocker.patch("app.auth.service.JWTService", return_value=mock_jwt)
        mocker.patch(
            "app.auth.service.add_refresh_jwt", 
            new_callable=mocker.AsyncMock, 
            return_value=None
        )

    @pytest.mark.asyncio
    async def test_success_update_tokens(self, update_tokens_happy_path):
        result = await  update_tokens(None, "refresh_jwt", "device")
        assert result.access == "test_access_token"
        assert result.refresh == "test_refresh_token"
        assert result.change_password is False

    @pytest.mark.asyncio
    async def test_refresh_not_found(self, mocker, update_tokens_happy_path):
        mocker.patch(
            "app.auth.service.verify_refresh_jwt",
            new_callable=mocker.AsyncMock,
            return_value=None
        )
        with pytest.raises(ApplicationException) as e:
            await update_tokens(None, "refresh_jwt", "device")
        
        assert e.value.code == 401

