from codechefcli.helpers import BASE_URL, html_to_list, request


def get_team_url(name):
    return f"{BASE_URL}/teams/view/{name}"


def format_contest(item):
    if item.startswith("Information for"):
        return f"\n{item}"
    return item


def get_team(name):
    if not name:
        return []
    resp = request(url=get_team_url(name))

    if resp.status_code == 200:
        resp_html = resp.html
        tables = resp_html.find('table')

        header = tables[1].text.strip()
        team_info = tables[2].text.strip()
        team_info = team_info.replace(':\n', ': ')
        team_info_list = team_info.split('\n')

        basic_info = "\n".join(team_info_list[:2])
        contests_info = "\n".join([format_contest(item) for item in team_info_list[2:-1]])
        problems_solved_table = html_to_list(tables[-1])

        team_details = "\n".join([
            '',
            header,
            '',
            basic_info,
            contests_info,
            '',
            'Problems Successfully Solved:',
            ''
        ])
        return [
            {'data': team_details},
            {'data': problems_solved_table, "data_type": "table", "is_pager": False}
        ]
    elif resp.status_code == 404:
        return [{'code': 404, 'data': 'Team not found.'}]
    return [{'code': 503}]
