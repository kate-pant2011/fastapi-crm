from app.auth.service import check_password
import pytest
    

@pytest.mark.parametrize(
    "password, expected",
    [
        ("pass12", "too short"),
        ("password123toolong", "too long"),
        ("password1ф", "includes forbidden symbols"),
        ("password", "doesn't include digit"),
        ("12345678", "doesn't include letter"),
        ("password1", None)
    ]
)
def test_password_validation(password, expected):
    
    assert check_password(password) == expected