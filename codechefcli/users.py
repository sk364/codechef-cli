# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from utils.constants import BASE_URL
from utils.helpers import get_session, request
import re

def get_user(username):
    """
    :desc: Retrieves user information.
    :param: `username` Username of the user.
    :return: `resps` response information array
    """

    session = get_session()
    url = BASE_URL + '/users/' + username
    req_obj = request(session, 'GET', url)
    resps = []

    if req_obj.status_code == 200:
        if 'Team handle' in req_obj.text:
            team_url = BASE_URL + '/teams/view/' + username
            resps = [{
                'data': 'This is a team handle. View at: ' + team_url + '\n',
                'code': 400
            }]
        else:
            soup = BeautifulSoup(req_obj.text, 'html.parser')
            header = soup.find_all('header')[1].text.strip()
            star_rating_span = soup.find('span', {'class' : 'rating'})
            star_rating = star_rating_span.get_text()
            user_info = soup.find(class_='user-details').text.strip()
            user_info = re.sub(u'\d★'," ",user_info, flags=re.UNICODE)
            user_details = '\nUser Details:\n' + header + '\n\nUser Star Rating: ' + star_rating +'\n' + user_info #soup.find(class_='user-details').text.strip()
            rating = soup.find(class_='rating-number').text
            ranks = soup.find(class_='rating-ranks').find('ul').find_all('li')

            user_details += ' - ' + BASE_URL + '/users/' + username + '/teams/\n\n'
            user_details += 'Rating: ' + rating + '\n\n'
            user_details += 'Global Rank: ' + ranks[0].text.split()[0] + '\n'
            user_details += 'Country Rank: ' + ranks[1].text.split()[0] + '\n\n'

            resps = [{'data': user_details}]
    elif req_obj.status_code == 404:
        resps = [{'code': 404, 'data': 'User not found.'}]
    elif req_obj.status_code == 503:
        resps = [{'code': 503}]

    return resps
