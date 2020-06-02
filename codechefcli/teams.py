from bs4 import BeautifulSoup

from .utils.constants import BASE_URL
from .utils.helpers import get_session, request


def get_team(team_name):
    """
    :desc: Retrieves team information.
    :param: `team_name` Name of the team.
    :return: `resps` response information array
    """

    session = get_session()
    url = BASE_URL + '/teams/view/' + team_name
    req_obj = request(session, 'GET', url)
    resps = []

    if req_obj.status_code == 200:
        soup = BeautifulSoup(req_obj.text, 'html.parser')
        header = soup.find_all('table')[1].text.strip()
        team_details = '\n' + header + '\n\n' + soup.find_all('table')[2].text.strip()

        resps = [{'data': team_details}]

    elif req_obj.status_code == 404:
        resps = [{'code': 404, 'data': 'Team not found.'}]

    elif req_obj.status_code == 503:
        resps = [{'code': 503}]

    return resps
