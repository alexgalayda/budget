from flask import Flask, request, jsonify
from flask_sslify import SSLify
import requests, json, configparser
import fin


app = Flask(__name__)
sslify = SSLify(app)

token = '1:A'
URL = 'https://api.telegram.org/bot'+token+'/'

def write_json(data, filename='/bot/answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def send_message(chat_id, text='паеш гавна'):
    url = URL + 'sendMessage'
    answer = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=answer)
    return r.json()

@app.route('/', methods=['POST', 'GET'])
def index():
    operations = ['/buy', '/take', '/pay']
    config = configparser.ConfigParser()
    config.read('/bot/config.ini')
    config.sections()
    broadcast = [int(config[name]['id']) for name in config['name']['name_list'].split(',')]
    if request.method == 'POST':
        r = request.get_json()
        # write_json(r)
        person_id = r['message']['from']['id']
        text = r['message']['text']
        if person_id in broadcast:
            budget = fin.Budget(path=config['path']['budget'], log=config['path']['log'], config=config)
            if budget.person[person_id].tran_type in operations:
                try:
                    text = text.split(' ')
                    fee = int(text[0])
                    if len(text) > 1:
                        text = ' '.join(text[1:])
                    else:
                        text = None
                except Exception:
                    send_message(person_id, text='Накосячено с транзакцией')
                    budget.person[person_id].tran_type = None
                else:
                    getattr(budget, budget.person[person_id].tran_type[1:])(person_id, fee, text)
                    budget.person[person_id].tran_type = None
                    send_message(person_id, text='Транзакция совершена')
            elif text in operations:
                budget.person[person_id].tran_type = text
                send_message(person_id, text='А теперь сумму')
            elif text == '/show':
                send_message(person_id, text=budget.show(id_name=person_id))
            elif text == '/show_shot':
                send_message(person_id, text=budget.show(id_name=person_id, shot=True))
            elif text == '/pay_renta':
                budget.pay_renta()
                for pers_id in broadcast:
                    send_message(pers_id, text='Рента заплачена\nКазна пустеет, мой лорд')
            budget.write()
        return jsonify(r)
    return '<h1>loool</h1>'

if __name__ == '__main__':
    app.run()
