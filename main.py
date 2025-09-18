"""Сбор статистики по вакансиям программистов с hh.ru, superjob."""
from __future__ import print_function
import requests
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from environs import Env
from terminaltables import AsciiTable


def predict_rub_salary(from_salary, to_salary):
    """Расчет ожидаемой зарплаты."""
    if from_salary and to_salary:
        return (from_salary + to_salary) / 2
    elif from_salary and not to_salary:
        return from_salary * 1.2
    elif not from_salary and to_salary:
        return to_salary * 0.8
    else:
        return None


def predict_rub_salary_hh(vacancy):
    """Определение зарплатной вилки, HH."""
    salary_data = vacancy.get('salary')
    if not salary_data or salary_data.get('currency') != 'RUR':
        return None
    from_salary = salary_data.get('from')
    to_salary = salary_data.get('to')
    return predict_rub_salary(from_salary, to_salary)


def predict_rub_salary_sj(vacancy):
    """Определение зарплатной вилки, Superjob."""
    from_salary = vacancy.get('payment_from')
    to_salary = vacancy.get('payment_to')
    return predict_rub_salary(from_salary, to_salary)


def get_response(url, params, headers, page):
    """Запрос к API."""
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    response_data = response.json()
    return response_data


def get_hh_vacancies_stats(languages):
    """Получение статистики по вакансиям, HH."""
    url = 'https://api.hh.ru/vacancies'
    month_ago = (date.today() - relativedelta(months=1)).strftime('%Y-%m-%d')
    headers = {'User-Agent': 'My-App/1.0 (runcken@gmail.com)'}
    stats = {}
    title = 'HeadHunter Moscow'
    for lang in languages:
        page = 0
        params = {
            'text': f'Программист {lang}',
            'area': '1',
            'date_from': month_ago,
            'per_page': 100,
            'page': page
        }
        count_vacancies = get_response(url, params, headers, page=0)

        pagination = count_vacancies['pages']
        valid_salaries = []
        all_pages_vacancies = []
        while page < pagination:
            params = {
                'text': f'Программист {lang}',
                'area': '1',
                'date_from': month_ago,
                'per_page': 100,
                'page': page
            }
            hh_response = get_response(url, params, headers, page)
            vacancies = hh_response['items']
            all_pages_vacancies.extend(vacancies)
            page += 1
            time.sleep(0.5)

        for vacancy in all_pages_vacancies:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
                valid_salaries.append(salary)

        if valid_salaries:
            avg_salary = int(sum(valid_salaries) / len(valid_salaries))

        stats[lang] = {
            'vacancies_found': len(all_pages_vacancies),
            'vacancies_processed': len(valid_salaries),
            'avg_salary': avg_salary
        }
    return stats, title


def get_sj_vacancies_stats(languages):
    """Получение статистики по вакансиям, SuperJob."""
    env = Env()
    title = 'SuperJob Moscow'
    headers = {'X-Api-App-Id': env.str('SJ_KEY')}
    url = 'https://api.superjob.ru/2.0/vacancies/'
    stats = {}
    env.read_env()
    for lang in languages:
        valid_salaries = []
        all_pages_vacancies = []
        params = {
            'catalogues': 48,
            'keywords[0][srws]': 1,
            'keywords[0][skwc]': 'or',
            'keywords[0][keys]': f'программист разработчик developer {lang}',
            'keywords[1][srws]': 4,
            'keywords[1][skwc]': 'and',
            'keywords[1][keys]': lang,
            'town': 4,
            'count': 40,
            'page': 0
        }
        superjob_response = get_response(url, params, headers, page=0)
        vacancies = superjob_response.get('objects')
        all_pages_vacancies.extend(vacancies)

        for vacancy in all_pages_vacancies:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                valid_salaries.append(salary)

        if valid_salaries:
            avg_salary = int(sum(valid_salaries) / len(valid_salaries))
        else:
            avg_salary = 0

        stats[lang] = {
            'vacancies_found': len(all_pages_vacancies),
            'vacancies_processed': len(valid_salaries),
            'avg_salary': avg_salary
        }

    return stats, title


def get_table(stats, title):
    """Вывод статистики в таблице."""
    table_headers = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]

    for lang, stats in stats.items():
        table_headers.append([
            lang,
            str(stats['vacancies_found']),
            str(stats['vacancies_processed']),
            str(stats['avg_salary']),
        ])

    vacancies_table = AsciiTable(table_headers, title=title)
    print(vacancies_table.table)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    languages = [
        'javascript',
        'java',
        'python',
        '1c',
        'PHP',
        'C++',
        'C#',
        'Go'
    ]
    stats, title = get_hh_vacancies_stats(languages)
    get_table(stats, title)
    stats, title = get_sj_vacancies_stats(languages)
    get_table(stats, title)
