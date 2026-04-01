import pytest
from app.services.user import create_user, change_user
from app.config.config import ApplicationException


class TestUserCreate:
    @pytest.fixture
    def create_user_happy_path(self, mocker, mock_user, mock_branch):
        mocker.patch("app.services.user.Access", return_value=mocker.MagicMock(is_owner=lambda: True))
        mocker.patch("app.services.user.get_branch_by_id", new_callable=mocker.AsyncMock, return_value=mock_branch)
        mocker.patch("app.services.user.add_user_role", new_callable=mocker.AsyncMock)
        mocker.patch("app.services.user.add_user", new_callable=mocker.AsyncMock, return_value=mock_user)
        mocker.patch("app.services.user.get_user_by_email", new_callable=mocker.AsyncMock, return_value=None)
        mocker.patch("app.services.user.generate_password", return_value="password")
        mocker.patch("app.services.user.hash_password", return_value="hashed_password")


    @pytest.mark.asyncio
    async def test_success_create(self, mocker, mock_user_data, create_user_happy_path):
        result = await create_user(session=None, roles={"admin"}, data=mock_user_data)
        assert result == {
            "name": "name",
            "password": "password"
        }
    
    @pytest.mark.asyncio
    async def test_user_exists(self, mocker, mock_user, mock_user_data, create_user_happy_path):
        mocker.patch(
            "app.services.user.get_user_by_email",
            new_callable=mocker.AsyncMock,
            return_value=mock_user
        )
        with pytest.raises(ApplicationException) as e:
            await create_user(session=None, roles={"admin"}, data=mock_user_data)
        
        assert e.value.code == 400
    
    @pytest.mark.asyncio
    async def test_user_archived(self, mocker, mock_user, mock_user_data, create_user_happy_path):
        mock_user.is_active = False
        mocker.patch(
            "app.services.user.get_user_by_email",
            new_callable=mocker.AsyncMock,
            return_value=mock_user
        )

        with pytest.raises(ApplicationException) as e:
            await create_user(session=None, roles={"admin"}, data=mock_user_data)
        
        assert e.value.code == 400
    
    @pytest.mark.asyncio
    async def test_owner_in_roles(self, mocker, mock_user_data, create_user_happy_path):
        mock_user_data.roles = ["owner"]

        with pytest.raises(ApplicationException) as e:
            await create_user(session=None, roles={"admin"}, data=mock_user_data)
        
        assert e.value.code == 400


class TestUserChange:
    @pytest.fixture
    def change_user_happy_path(self, mocker, mock_user, mock_branch):
        mocker.patch("app.services.user.get_user_by_id", new_callable=mocker.AsyncMock, return_value=mock_user)
        mocker.patch("app.services.user.get_branch_by_id", new_callable=mocker.AsyncMock, return_value=mock_branch)
        mocker.patch("app.services.user.add_user_role", new_callable=mocker.AsyncMock)
        mocker.patch("app.services.user.to_schema", return_value=True)

        item = mocker.Mock()
        item.model_dump.return_value = {
            "branch_id": 1,
            "role": ["admin"]
        }
        return item

    @pytest.mark.asyncio
    async def test_user_not_found(self, mocker):
        mocker.patch(
            "app.services.user.get_user_by_id",
            new_callable=mocker.AsyncMock,
            return_value=None
        )
        with pytest.raises(ApplicationException) as e:
            await change_user(session=None, roles={"admin"}, user_id=1, item=None)

        assert e.value.code == 404

    @pytest.mark.asyncio
    async def test_user_inactive(self, mock_user, change_user_happy_path):
        mock_user.is_active = False

        with pytest.raises(ApplicationException) as e:
            await change_user(session=None, roles={"admin"}, user_id=1, item=None)

        assert e.value.code == 400

    @pytest.mark.asyncio
    async def test_success_change(self, change_user_happy_path):
            result = await change_user(session=None, roles={"admin"}, user_id=1, item=change_user_happy_path)

            assert result is True
            