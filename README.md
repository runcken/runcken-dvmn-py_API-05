# Getting statistics of vacancies from HeadHunters and SuperJob using API web services

The script collect statistics of vacancies for different programming languages, such as quantity and payment value.


## How to install

Clone repository to your local device. To avoid problems with installing required additinal packages, its strongly to use a virtual environment [virtualenv/venv](https://docs.python.org/3/library/venv.html), for example:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

## Environment

### Requirements

Python3.12 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:

```bash
pip install -r requirements.txt
```

The script uses additinal packages:

- requests==2.20.1

- environs==14.2.0

- python-dateutil==2.8.2

- terminaltables==3.1.10

### Environment variables

- SJ_KEY

1. Put `.env` file near `main.py`.
2. `.env` contains text data without quotes.


#### How to get

* Register an application at [API SuperJob](https://api.superjob.ru/) and get the SuperJob Secret key

## Run

Launch on Linux(Python 3) or Windows:

```bash
python3 main.py
```

As result you will see statistics for vacancies, foer example:

<img width="852" height="526" alt="image" src="https://github.com/user-attachments/assets/ef424d7f-be16-40c2-8c8e-08f93a55a302" />


## Notes

The file with the contents of these environment variables isnt included in the repository.

## Project Goals

The code is written for educational purposes on online-course for web-developers dvmn.org.
