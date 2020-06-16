# -*- coding: utf-8 -*-

from codechefcli.helpers import BASE_URL, request, style_text
from codechefcli.teams import get_team_url

HEADER = 'header'
RATING_NUMBER_CLASS = '.rating-number'
RATING_RANKS_CLASS = '.rating-ranks'
STAR_RATING_CLASS = '.rating'
USER_DETAILS_CONTAINER_CLASS = '.user-details-container'
USER_DETAILS_CLASS = '.user-details'


def get_user_teams_url(username):
    return f'{BASE_URL}/users/{username}/teams/'


def format_list_item(item):
    return ": ".join([i.strip() for i in item.text.split(':')])


def get_user(username):
    if not username:
        return []

    resp = request(url=f'/users/{username}')

    if resp.status_code == 200:
        team_url = get_team_url(username)
        if resp.url == team_url:
            return [{
                'data': f'This is a team handle.'
                        f'Run `codechefcli --team {username}` to get team info\n',
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

            # rating
            star_rating = details_container.find(STAR_RATING_CLASS, first=True).text.strip()
            rating = resp_html.find(RATING_NUMBER_CLASS, first=True).text.strip()
            rank_items = resp_html.find(RATING_RANKS_CLASS, first=True).find('li')
            global_rank = rank_items[0].find('a', first=True).text.strip()
            country_rank = rank_items[1].find('a', first=True).text.strip()

            user_details = "\n".join([
                '',
                style_text(f'User Details for {header} ({username}):', 'BOLD'),
                '',
                info,
                f"User's Teams: {get_user_teams_url(username)}",
                '',
                f'Rating: {star_rating} {rating}',
                f'Global Rank: {global_rank}',
                f'Country Rank: {country_rank}',
                '',
                f'Find more at: {resp.url}',
                ''
            ])
            return [{'data': user_details}]
    return [{'code': 503}]
