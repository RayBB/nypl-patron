import json
import re
import urllib

import requests

from bs4 import BeautifulSoup


def strip_spaces_and_newlines(input_text: str) -> str:
    out = re.sub(r'(\n|\r)', "", input_text)
    out = re.sub(r' +', " ", out)
    out = out.strip()  # removes trailing spaces
    return out


class NYPLPatron:

    def __init__(self, library_card_number, pin):
        print("Patron init")
        self.library_card_number = library_card_number
        self.pin = pin
        self.session = self.__login()
        self.patron_id = self.get_patron_info()['data']['patron']['id']

    def __login(self):
        login_url = "https://login.nypl.org/auth/login?redirect_uri=https://browse.nypl.org/iii/encore/myaccount"
        session = requests.Session()
        response = session.get(login_url)
        soup = BeautifulSoup(response.content, features="html.parser")

        # This is a value randomly generated by server that we must submit
        lt = soup.find("input", {"name": "lt"})['value']

        payload = {
            'code': self.library_card_number,
            'pin': self.pin,
            "rememberme": "on",
            "_eventId": "submit",
            "lt": lt
        }
        response = session.post("https://ilsstaff.nypl.org/iii/cas/login", data=payload)

        # Successful login
        if 'PatronAccountPage' in response.text:
            print("Logged in sucessfully")
        else:
            # TODO: LOOK INTO BEST PRACTICES for exceptions
            raise ValueError('Login Failed!')
        
        return session

    def get_patron_info(self):
        """
        EXAMPLE Output:
        {
        'data': {
            'decodedToken': {
                'iss': 'https://www.nypl.org',
                'sub': '1111111',
                'aud': 'app_myaccount',
                # These three below are epoch timestamps
                'iat': 1581913282,
                'exp': 1581916882,
                'auth_time': 1581913282,
                'scope': 'openid offline_access patron:read'
            },
            'patron': {
                'id': '1111111',
                'names': ['LAST_NAME, FIRST_NAME'],
                'barCodes': ['11111111111111'],
                'emails': ['EMAIL@GMAIL.COM']
            }
        },
        'count': 1,
        'statusCode': 200,
        'debugInfo': []
        }
        """
        access_token = self.get_session_info()['access_token']
        url = f"https://platform.nypl.org/api/v0.1/auth/patron/tokens/{access_token}"
        patron_info = self.session.get(url).json()
        # print(patron_info)
        return patron_info
        # Info needed to get holds is ['data']['patron']['id']

    def get_session_info(self):
        """
        {
            "token_type": "Bearer",
            "scope": "openid+offline_access+patron:read",
            "access_token": "long_string",
            "refresh_token": "short_string",
            "expires": 1581916405 # epoch timestamp
        }
        """
        encoded_dict = self.session.cookies.get_dict()['nyplIdentityPatron']
        decoded_dict = json.loads(urllib.parse.unquote(encoded_dict))
        return decoded_dict

    def get_hold_info(self):
        response = self.session.get(
            f"https://ilsstaff.nypl.org/dp/patroninfo*eng~Sdefault/{self.patron_id}/holds")
        soup = BeautifulSoup(response.content, features="html.parser")
        hold_rows = soup.find_all("tr", {"class": "patFuncEntry"})
        holds = []
        for row in hold_rows:
            holds.append({
                "title": row.find("td", {"class", "patFuncTitle"}).text.strip(),
                "status": row.find("td", {"class", "patFuncStatus"}).text.strip(),
                "pickup location": row.find("option", {"selected": "selected"}).text.strip(),
                "cancel date": row.find("td", {"class", "patFuncCancel"}).text.strip(),
                "frozen": row.find('input', checked=True) is not None,
            })
        print(holds)
        return holds

    def get_checkout_info(self):
        response = self.session.get(
            f"https://ilsstaff.nypl.org/dp/patroninfo*eng~Sdefault/{self.patron_id}/items")
        soup = BeautifulSoup(response.content, features="html.parser")
        checkout_rows = soup.find_all("tr", {"class": "patFuncEntry"})
        checkouts = []
        for row in checkout_rows:
            checkouts.append({
                "title": row.find("td", {"class", "patFuncTitle"}).text.strip(),
                "barcode": row.find("td", {"class", "patFuncBarcode"}).text.strip(),
                "status": row.find("td", {"class", "patFuncStatus"}).text.strip(),
                "call number": row.find("td", {"class": "patFuncCallNo"}).text.strip(),
            })
        print(checkouts)
        return checkouts

    def get_ebook_info(self):
        url = "https://browse.nypl.org/iii/encore/PatronAccountPage,patronPageMenuComponent.patronEbookDirectLinkComponent.sdirect?lang=eng&suite=def&beventname=onClick&beventtarget.id=patronEbookDirectLinkComponent&dojo.preventCache=1581914728649"
        response = self.session.get(url)
        soup = BeautifulSoup(response.content, features="html.parser")
        rows = soup.find_all("tr", {"class": "patronEbookInfoEntry"})
        ebooks = []
        for row in rows:

            title = row.find("span", {"class", "title"}).text
            title = strip_spaces_and_newlines(title)

            date = row.find("div", {"class", "dateCountdown"}).parent.text
            date = strip_spaces_and_newlines(date)

            ebooks.append({
                "title": title,
                "date": date,
                "ebook provider": row.find("img")['alt'],
            })
        print(ebooks)
        return ebooks

    def get_eContent_holds(self):
        pass
