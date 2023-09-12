import requests
import fake_headers
from bs4 import BeautifulSoup
import json

url = 'https://spb.hh.ru/search/vacancy'

headers_gen = fake_headers.Headers(browser='chrome', os='windows')
pages = [1,2,3]
params = {
    'text': 'Python',
    'area': [1, 2],
    'page': pages,
    'items_on_page': 20
}

all_vacancies = []
count_yes = 0
count_no = 0

for page in pages:
    hh_link = requests.get(url, headers=headers_gen.generate(), params=params).text
    hh_page = BeautifulSoup(hh_link,'lxml')

    res = hh_page.find_all('div',class_="serp-item")

    for item in res:
       #Парсим название вакансии
        vacancy = item.find('a', class_="serp-item__title").text

       #Парсим ссылку
        link = item.find('a',class_="serp-item__title")['href']

       #Парсим название компании
        name_company = item.find('a', class_="bloko-link bloko-link_kind-tertiary").text

       #Парсим город
        cities = ['Санкт-Петербург', 'Москва']
        city = item.find('div', attrs={"data-qa": "vacancy-serp__vacancy-address"}).text
        for name_city in cities:
            if name_city.lower() in city.lower():
                city = name_city

       #Парсим зп
        salary = item.find('span', class_="bloko-header-section-2")
        if salary is None:
            salary = 'Не указана'
        else:
            salary = salary.text

       #Выбираем вакансии с Django и Flask
        requirements = ['Django', 'Flask']
        desc = requests.get(link, headers=headers_gen.generate()).text
        soup = BeautifulSoup(desc, 'lxml')
        tag = soup.find('div', class_='g-user-content').text
        for i in requirements:
            if i.lower() in tag.lower():
                count_yes += 1
                result = {
                   'Вакансия': vacancy.replace('\"',''),
                   'Ссылка на вакансию': link,
                   'Зарплата': salary.replace('\u202f', ''),
                   'Название компании': name_company.replace('\xa0',' '),
                   'Город': city
                }
                all_vacancies.append(result)
            else:
                count_no += 1

if __name__ == "__main__":
    print(f'Вакансий подошло: {count_yes}')
    print(f'Вакансий не подошло: {count_no}')
    with open('vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(all_vacancies, f, ensure_ascii=False, indent=4)