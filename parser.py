# import schedule
# import time
from urllib.error import URLError
from urllib.request import build_opener, urlopen, install_opener
from bs4 import BeautifulSoup
from models.location import Location
from models.company import Company
root_url = 'http://taxist.com.ua'
cities_url = root_url + '/city'


def get_html(url):
    try:
        return urlopen(url).read()
    except URLError:
        print(URLError)
        return False


def get_taxi_info(html, company):
    try:
        soup = BeautifulSoup(html, 'html.parser')

        ul = soup.find('ul', attrs={'id': 'taxiul'})
        desc = '\n'.join(ul.stripped_strings)
        end = desc.find('Рейтинг:')

        company.description = desc[:end]
        company.phone = '\n'.join(soup.find('div', attrs={'id': 'telefon'}).stripped_strings)
        company.save()
    except UnicodeEncodeError:
        print('Unicode error')


def get_taxi_link(url, loc_id):
    html = get_html(url)
    if html:
        soup = BeautifulSoup(html, 'html.parser').find('table', id='bl')('td', class_='blname')
        for td in soup:
            try:
                html = get_html(root_url + td.a['href'])
                if html:
                    company = Company(location=loc_id, name=str(td.a.string))
                    get_taxi_info(html, company)
                else:
                    print('Invalid url')
            except UnicodeEncodeError:
                print('Unicode error')
    else:
        print('Invalid url')


def get_location(url):
    html = get_html(url)
    if html:
        soup = BeautifulSoup(html, 'html.parser').find_all('ul', id='city')
        for ul_tag in soup:
            for li_tag in ul_tag.find_all('li'):
                location = Location(ul_tag.next_element.rstrip(), str(li_tag.string))
                if location.region == '':
                    location.region = location.city
                location.save()
                get_taxi_link(li_tag.a['href'], location.get_id())
    else:
        print('Invalid url')


def main():
    opener = build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 ')]
    install_opener(opener)

    get_location(root_url + '/city')
    """
    schedule.every(1).minutes.do(get_location(root_url + '/city'))

    while True:
        schedule.run_pending()
        time.sleep(1)
    """


if __name__ == '__main__':
    main()
