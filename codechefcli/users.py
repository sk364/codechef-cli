import requests
from bs4 import BeautifulSoup

from .utils.constants import BASE_URL, SERVER_DOWN_MSG


def get_user(username):
    """
    :desc: Retrieves user information.
    :param: `username` Username of the user.
    :return: User information / User not found  / Server Down
    """

    req_obj = requests.get(BASE_URL + '/users/' + username)

    if req_obj.status_code == 200:
        if 'Team handle' in req_obj.text:
            team_url = BASE_URL + '/teams/view/' + username
            return 'This is a team handle. View at: ' + team_url + '\n'

        soup = BeautifulSoup(req_obj.text, 'html.parser')
        header = soup.find_all('header')[1].text.strip()
        user_details = '\n' + header + '\n\n' + soup.find(class_='user-details').text.strip()
        rating = soup.find(class_='rating-number').text
        ranks = soup.find(class_='rating-ranks').find('ul').find_all('li')
       
        user_details += ' - ' + BASE_URL + '/users/' + username + '/teams/\n\n'
        user_details += 'Rating: ' + rating + '\n\n'
        user_details += 'Global Rank: ' + ranks[0].text.split()[0] + '\n'
        user_details += 'Country Rank: ' + ranks[1].text.split()[0] + '\n\n'
        
        return user_details
    elif req_obj.status_code == 404:
        return 'User not found.'
    else:
        return SERVER_DOWN_MSG

