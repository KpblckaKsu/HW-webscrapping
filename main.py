import requests
import re
from fake_headers import Headers
from bs4 import BeautifulSoup
from pprint import pprint
import json

hh_link = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
headers = Headers(os='win', browser='chrome')


def get_page(url):
    return requests.get(url, headers=headers.generate())


def get_last_page_number():
    html_page = get_page(hh_link).text
    soup = BeautifulSoup(html_page, features='lxml')
    pages = soup.find('div', class_='pager')
    last_page = pages.find_all('a', class_='bloko-button')[-2].get_text()
    last_page_number = int(last_page) - 1
    return last_page_number


def check_vacancy_validity(link):
    html_page = get_page(link).text
    soup = BeautifulSoup(html_page, features='lxml')
    vacancy_description = soup.find('div', class_='vacancy-description').get_text()
    pattern = r'([Ff]lask.*?[Dd]jango)|([Dd]jango.*?[Ff]lask)'
    result = re.search(pattern, vacancy_description, re.M)
    if result is not None:
        return True
    else:
        return False


def parse_vacancy(vacancy):
    vacancy_link = vacancy.find('a', class_='serp-item__title')['href']
    employer_info = vacancy.find('div', class_='vacancy-serp-item__info').find_all('div', class_='bloko-text')
    employer = employer_info[0].text.replace('\xa0', ' ')
    location = employer_info[1].contents[0]
    salary = 'з/п не указана'
    salary_html = vacancy.find('span', class_='bloko-header-section-3')
    if salary_html is not None:
        salary = salary_html.text.replace('\u202f', ' ')
    if check_vacancy_validity(vacancy_link):
        vacancy_data = {
            'link': vacancy_link,
            'salary': salary,
            'employer': employer,
            'location': location
        }
        return vacancy_data


def parse_page(page_number):
    html_page = get_page(f'{hh_link}&page={page_number}').text
    soup = BeautifulSoup(html_page, features='lxml')
    vacancies = soup.find_all('div', class_="serp-item")
    vacancies_list = []
    for vacancy in vacancies:
        new_vacancy = (parse_vacancy(vacancy))
        if new_vacancy is not None:
            vacancies_list.append(new_vacancy)
    return vacancies_list


def parse_pages(end_page=0):
    last_page = get_last_page_number()
    if end_page > last_page:
        end_page = last_page
    total_vacancies = []
    count = 0
    while count <= end_page:
        new_vacancies = parse_page(count)
        if new_vacancies is not None:
            for element in new_vacancies:
                total_vacancies.append(element)
        count += 1
    with open('vacancies.json', 'w', encoding='utf8') as f:
        json.dump(total_vacancies, f, ensure_ascii=False)
        pprint(json.dumps(total_vacancies, ensure_ascii=False))


def main():
    while True:
        print('Список доступных комманд: \n "n" - найти только новые вакансии (парсинг первой страницы); \
         \n "s" - найти вакансии на нескольких страницах; \
         \n "a" - найти все вакансии (парсинг по всем страницам сайта); \
         \n "q" - выйти из программы')
        command = input('Введите команду: ')
        if command == 'n':
            parse_pages()
        elif command == 's':
            end_page = int(input('Введите количество страниц для поиска: ')) - 1
            parse_pages(end_page)
        elif command == 'a':
            end_page = get_last_page_number()
            parse_pages(end_page)
        elif command == 'q':
            print('Выход из программы')
            break


if __name__ == '__main__':
    main()
