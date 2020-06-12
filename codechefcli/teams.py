from codechefcli.helpers import request


def get_team_url(name):
    return f"/teams/view/{name}"


def format_contest(item):
    if item.startswith("Information for"):
        return f"\n{item}"
    return item


def get_team(name):
    resp = request(url=get_team_url(name))
    resps = []

    if resp.status_code == 200:
        resp_html = resp.html
        tables = resp_html.find('table')

        header = tables[1].text.strip()
        team_info = tables[2].text.strip()
        team_info = team_info.replace(':\n', ': ')
        team_info_list = team_info.split('\n')

        basic_info = "\n".join(team_info_list[:2])
        contests_info = "\n".join([format_contest(item) for item in team_info_list[2:-1]])

        # TODO: fix formatting
        problems_solved_table = tables[-1].text.strip()

        team_details = ['']
        team_details.append(header)
        team_details.append('')
        team_details.append(basic_info)
        team_details.append(contests_info)
        team_details.append('')
        team_details.append('Problems Successfully Solved:')
        team_details.append(problems_solved_table)

        return [{'data': "\n".join(team_details)}]

    elif resp.status_code == 404:
        return [{'code': 404, 'data': 'Team not found.'}]

    elif resp.status_code == 503:
        return [{'code': 503}]

    return resps
