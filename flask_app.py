import os

from flask import Flask, request
import logging

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

chooses = [
    'слон',
    'кролик'
]


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ],
            'choose': 0
        }
        res['response']['text'] = f'Привет! Купи {chooses[sessionStorage[user_id]["choose"]]}а!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю'
    ]:
        res['response']['text'] = f'{chooses[sessionStorage[user_id]["choose"]].capitalize()}а ' \
                                  f'можно найти на Яндекс.Маркете!'
        sessionStorage[user_id]['choose'] += 1
        if sessionStorage[user_id]['choose'] == len(chooses):
            # Пользователь согласился, прощаемся.
            res['response']['end_session'] = True
            sessionStorage[user_id]['choose'] = 0
            return
        res['response']['text'] = f'Ну тогда купи и {chooses[sessionStorage[user_id]["choose"]]}а!'
        sessionStorage[user_id]['suggests'] = ["Не хочу.",
                                               "Не буду.",
                                               "Отстань!"]
        res['response']['buttons'] = get_suggests(user_id)
        return
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а " \
        f"ты купи {chooses[sessionStorage[user_id]['choose']]}а!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?"
                   f"text={chooses[sessionStorage[user_id]['choose']]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run(port=os.environ.get("PORT", 5000), host='0.0.0.0')
