#!/usr/bin/env python3
# coding: utf-8

import os
import requests
import json

TOKEN = 'AQAAAAAq5tvuAAUyQJxdlAVNt0BqhPrK5P4L1Mg'
USER_AGENT = 'Directory Sync Example'


def update_user_password(nickname, password):
    user_data = load_user(nickname)
    if user_data and user_data['status_code'] == 200:
        user = user_data['result']
        password = update_password(user, password)
        return password
    else:
        return user_data


def load_user(nickname):
    params = {
        'fields': 'nickname,name,id',
        'nickname': nickname,
        'per_page': 10
    }

    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
    }

    response = requests.get(
        'https://api.directory.yandex.net/v6/users/',
        params=params,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()
    response_data = response.json()
    if response_data['total'] == 1:
        user = response_data['result'][0]
        return {'status_code': 200,
                'text': {'message': "User found", 'code': 'user.found'},
                'result': user
                }
    elif response_data['total'] > 1:
        return {'status_code': 404,
                'text': {'message': "Too much users in response", 'code': 'user.too_many_user'}
                }
    else:
        return {'status_code': 404,
                'text': {'message': "User not found", 'code': 'user.not_found'}
                }


def update_password(u, password):
    payload = {
        "password": password,
    }
    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
    }
    # print(u['name']['first'])
    response = requests.patch(
        'https://api.directory.yandex.net/v6/users/%s/' % (u['id']),
        json=payload,
        headers=headers,
        timeout=10,
    )
    if response.status_code != 200:
        return {'status_code': response.status_code, 'text': json.loads(response.text)}

    response.raise_for_status()
    response_data = response.json()
    # results = response_data['result']
    return {'status_code': response.status_code,
            'text': {'message': "Password changed", 'code': 'password.ok'}
            }


def create_user(data):
    payload = {
        "name": {
            "first": data.name,
            "last": data.surname,
            "middle": data.patronymic
        },
        "nickname": data.login,
        "password": data.password,
        "department_id": 1,
    }
    headers = {
        'Authorization': 'OAuth ' + TOKEN,
        'User-Agent': USER_AGENT,
    }
    # print(u['name']['first'])
    response = requests.post(
        'https://api.directory.yandex.net/v6/users/',
        json=payload,
        headers=headers,
        timeout=100,
    )
    if response.status_code != 200:
        return {'status_code': response.status_code, 'text': json.loads(response.text)}

    response.raise_for_status()
    response_data = response.json()
    # results = response_data['result']
    return {'status_code': response.status_code,
            'text': {'message': "User Created", 'code': 'password.ok'}
            }
