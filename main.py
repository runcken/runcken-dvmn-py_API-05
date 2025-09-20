"""Сбор статистики по вакансиям программистов с hh.ru, superjob."""
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
    salary = vacancy.get('salary')
    if not salary or salary.get('currency') != 'RUR':
        return None
    from_salary = salary.get('from')
    to_salary = salary.get('to')
    return predict_rub_salary(from_salary, to_salary)


def predict_rub_salary_sj(vacancy):
    """Определение зарплатной вилки, Superjob."""
    if vacancy.get('currency') != 'rub':
        return None
    from_salary = vacancy.get('payment_from')
    to_salary = vacancy.get('payment_to')
    return predict_rub_salary(from_salary, to_salary)


def get_response(url, params, headers):
    """Запрос к API."""
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    response_data = response.json()
    return response_data


def get_stats(all_pages_vacancies, found, salary_predictor):
    """Определение статистики по зарплатам."""
    valid_salaries = []
    for vacancy in all_pages_vacancies:
        salary = salary_predictor(vacancy)
        if salary:
            valid_salaries.append(salary)

    if valid_salaries:
        avg_salary = int(sum(valid_salaries) / len(valid_salaries))
    else:
        avg_salary = 0

    lang_stats = {
        'vacancies_found': found,
        'vacancies_processed': len(valid_salaries),
        'avg_salary': avg_salary
    }
    return lang_stats


def get_hh_vacancies(languages, headers):
    """Получение вакансий, HH."""
    url = 'https://api.hh.ru/vacancies'
    month_ago = (date.today() - relativedelta(months=1)).strftime('%Y-%m-%d')
    stats = {}
    region_code = 1
    results_on_page = 100
    for lang in languages:
        page = 0
        params = {
            'text': f'Программист {lang}',
            'area': region_code,
            'date_from': month_ago,
            'per_page': results_on_page,
            'page': page
        }
        count_response = get_response(url, params, headers)
        pagination = count_response['pages']
        found = count_response['found']
        all_pages_vacancies = count_response['items'].copy()
        page += 1

        while page < pagination:
            params['page'] = page
            hh_response = get_response(url, params, headers)
            vacancies = hh_response['items']
            all_pages_vacancies.extend(vacancies)
            page += 1
            time.sleep(0.5)

        stats[lang] = get_stats(
            all_pages_vacancies, found, predict_rub_salary_hh
        )

    return stats


def get_sj_vacancies(languages, headers):
    """Получение вакансий, SuperJob."""
    url = 'https://api.superjob.ru/2.0/vacancies/'
    catalog_section = 48
    job_title = 1
    qualification = 4
    town_code = 4
    results_on_page = 10
    stats = {}
    for lang in languages:
        page = 0
        more = True
        all_pages_vacancies = []
        while more:
            params = {
                'catalogues': catalog_section,
                'keywords[0][srws]': job_title,
                'keywords[0][skwc]': 'or',
                'keywords[0][keys]': (
                    f'программист разработчик developer {lang}'
                ),
                'keywords[1][srws]': qualification,
                'keywords[1][skwc]': 'and',
                'keywords[1][keys]': lang,
                'town': town_code,
                'count': results_on_page,
                'page': page
            }
            superjob_response = get_response(url, params, headers)
            found = superjob_response['total']
            vacancies = superjob_response.get('objects')
            all_pages_vacancies.extend(vacancies)

            if len(vacancies) < results_on_page:
                more = False
            else:
                page += 1
                time.sleep(0.5)

        stats[lang] = get_stats(
            all_pages_vacancies, found, predict_rub_salary_sj
        )

    return stats


def get_table(stats, title):
    """Сбор статистики в таблицу."""
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
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['avg_salary'],
        ])

    vacancies_table = AsciiTable(table_headers, title=title)
    return vacancies_table.table


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
    headers = {'User-Agent': 'My-App/1.0 (runcken@gmail.com)'}
    stats = get_hh_vacancies(languages, headers)
    title = 'HeadHunter Moscow'
    print(get_table(stats, title))
    headers = {'X-Api-App-Id': env.str('SJ_KEY')}
    stats = get_sj_vacancies(languages, headers)
    title = 'SuperJob Moscow'
    print(get_table(stats, title))
