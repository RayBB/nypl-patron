from pathlib import Path
from unittest.mock import patch

import pytest
import responses
from nypl.patron import NYPLPatron


@responses.activate
@patch("nypl.patron.NYPLPatron.get_patron_info")
def test_login_success(mock_get_patron_info):
    lt_page = Path("tests/sample_responses/login_get_lt.html").read_text()
    login_success_page = Path(
        "tests/sample_responses/login_success.html").read_text()
    library_card_nummber = 123
    pin = 9999
    lt = "_cE2D2A7E9-AC10-4D2D-79C2-3BB289916B6A_kC15095AB-088B-84D7-EAB5-358E02139751"

    responses.add(responses.GET,
                  'https://login.nypl.org/auth/login?redirect_uri=https://browse.nypl.org/iii/encore/myaccount',
                  body=lt_page)

    responses.add(responses.POST,
                  'https://ilsstaff.nypl.org/iii/cas/login',
                  body=login_success_page)

    user = NYPLPatron(library_card_nummber, pin)
    assert lt in responses.calls[1].request.body
    assert str(library_card_nummber) in responses.calls[1].request.body
    assert str(pin) in responses.calls[1].request.body


@responses.activate
@patch("nypl.patron.NYPLPatron.get_patron_info")
def test_login_failure(mock_get_patron_info):
    lt_page = Path("tests/sample_responses/login_get_lt.html").read_text()
    login_failure_page = Path(
        "tests/sample_responses/login_failure.html").read_text()
    library_card_nummber = 123
    pin = 9999
    lt = "_cE2D2A7E9-AC10-4D2D-79C2-3BB289916B6A_kC15095AB-088B-84D7-EAB5-358E02139751"

    responses.add(responses.GET,
                  'https://login.nypl.org/auth/login?redirect_uri=https://browse.nypl.org/iii/encore/myaccount',
                  body=lt_page)

    responses.add(responses.POST,
                  'https://ilsstaff.nypl.org/iii/cas/login',
                  body=login_failure_page)

    with pytest.raises(ValueError) as excinfo:
        user = NYPLPatron(library_card_nummber, pin)
