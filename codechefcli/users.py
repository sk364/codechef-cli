# -*- coding: utf-8 -*-

from codechefcli.helpers import BASE_URL, get_session, request, style_text
from codechefcli.teams import get_team_url

HEADER = 'header'
RATING_NUMBER_CLASS = '.rating-number'
RATING_RANKS_CLASS = '.rating-ranks'
STAR_RATING_CLASS = '.rating'
USER_DETAILS_CONTAINER_CLASS = '.user-details-container'
USER_DETAILS_CLASS = '.user-details'


def get_user_teams_url(username):
    return f'/users/{username}/teams/'


def format_list_item(item):
    return ": ".join([i.strip() for i in item.text.split(':')])


def get_user(username):
    resp = request(get_session(), url=f'/users/{username}')

    if resp.status_code == 200:
        team_url = get_team_url(username)
        if resp.url == team_url:
            return [{
                'data': 'This is a team handle. Run `codechefcli --team {name}` to get team info\n',
                'code': 400
            }]
        elif resp.url.rstrip('/') == BASE_URL:
            return [{'code': 404, 'data': 'User not found.'}]
        else:
            resp_html = resp.html
            details_container = resp_html.find(USER_DETAILS_CONTAINER_CLASS, first=True)

            # basic info
            header = details_container.find(HEADER, first=True).text.strip()
            info_list_items = details_container.find(USER_DETAILS_CLASS, first=True).find('li')

            # ignore first & last item i.e. username item & teams item respectively
            info = "\n".join([format_list_item(li) for li in info_list_items[1:-1]])
            user_teams_url = get_user_teams_url(username)

            # rating
            star_rating = details_container.find(STAR_RATING_CLASS, first=True).text.strip()
            rating = resp_html.find(RATING_NUMBER_CLASS, first=True).text.strip()
            rank_items = resp_html.find(RATING_RANKS_CLASS, first=True).find('li')
            global_rank = rank_items[0].find('a', first=True).text.strip()
            country_rank = rank_items[1].find('a', first=True).text.strip()

            user_details = ['']
            user_details.append(style_text(f'User Details for {header} ({username}):', 'BOLD'))
            user_details.append('')
            user_details.append(info)
            user_details.append(f"User's Teams: {user_teams_url}")
            user_details.append('')
            user_details.append(f'Rating: {star_rating} {rating}')
            user_details.append(f'Global Rank: {global_rank}')
            user_details.append(f'Country Rank: {country_rank}')
            user_details.append('')
            user_details.append(f'Find more at: {resp.url}')
            user_details.append('')

            return [{'data': "\n".join(user_details)}]
    return [{'code': 503}]
