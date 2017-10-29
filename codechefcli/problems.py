import requests
from bs4 import BeautifulSoup

from .utils.constants import BASE_URL, SERVER_DOWN_MSG


def get_description(problem_code):
    """
    
    """

    req_obj = requests.get(BASE_URL + '/problems/' + problem_code)

    if req_obj.status_code == 200:
        problem_html = req_obj.text
        soup = BeautifulSoup(problem_html, 'html.parser')
        if soup.find(id='problem-code'):
            content = soup.find_all('div', class_='content')[1]
            content.find_all('h3')[0].extract()
            content.find_all('h3')[0].extract()
            problem_info = soup.find_all('table')[2].text
            return content.text + problem_info
        else:
            print ('Problem not found')
            return ''
    else:
        print (SERVER_DOWN_MSG)
        return ''

