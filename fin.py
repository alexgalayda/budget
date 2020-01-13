import json, os, csv
from datetime import datetime

class Budget:
    def __init__(self, path, log, config):
        self.path = path
        self.log = Log(log)
        if os.path.exists(path):
            with open(path, 'r') as read_file:
                data = json.load(read_file)
                self.score = float(data['score'])
                self.person = {int(config[name]['id']): Person(name, config[name],
                                           score=float(data['person'][config[name]['id']]['score']),
                                           last=int(data['person'][config[name]['id']]['last']),
                                           tran_type=data['person'][config[name]['id']]['tran_type']) for name in config['name']['name_list'].split(',')}
        else:
            self.score = 0
            self.person = {int(config[name]['id']): Person(name, config[name]) for name in config['name']['name_list'].split(',')}

    def __repr__(self):
        ans = 'Общий счет: {}'.format(
            int(round(self.score))
        )
        return ans

    def make_dict(self):
        return {
            'score': self.score,
            'person': {person: self.person[person].make_dict() for person in self.person}
        }

    def buy(self, id_name, cost, code=None):
        if isinstance(id_name, str):
            id_name = self.name2id(id_name)
        self.log.push(name=self.person[id_name].name, operation='buy', score=cost, message=code)
        for name in self.person:
            if name == id_name:
                self.person[name].score += cost * 2 / 3
            else:
                self.person[name].score -= cost / 3

    def pay(self, id_name, fee, code=None):
        if isinstance(id_name, str):
            id_name = self.name2id(id_name)
        self.log.push(name=self.person[id_name].name, operation='pay', score=fee, message=code)
        self.score += fee
        self.person[id_name].score += fee

    def take(self, id_name, fee, code=None):
        if isinstance(id_name, str):
            id_name = self.name2id(id_name)
        self.log.push(name=self.person[id_name].name, operation='take', score=fee, message=code)
        self.score -= fee
        self.person[id_name].score -= fee

    def pay_renta(self):
        score = sum([int(self.person[id_name].renta) for id_name in self.person])
        self.log.push(name='all', operation='renta', score=score)
        self.score -= score
        for id_name in self.person:
            self.person[id_name].score -= self.person[id_name].renta

    def show(self, log=True, id_name=None, shot=False):
        if id_name is None:
            print(self)
            for id_name in self.person:
                print(self.person[id_name])
            if log:
                print(self.log)
        else:
            return '{}' \
                   '\nИз которых твои: {}' \
                   '\n{}'.format(
                self.__repr__(),
                int(self.person[id_name].score),
                self.log.__repr__(shot=shot)
            )

    def write(self):
        with open(self.path, 'w') as write_file:
            json.dump(self.make_dict(), write_file, indent=4)
        print('БД была записана в {}'.format(self.path))
        with open(self.log.path, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            filewriter.writerow(['id', 'name', 'operation', 'score', 'message', 'date'])
            for i in self.log.log_list:
                filewriter.writerow([i[0], i[1], i[2], i[3], i[4], i[5]])
        print('Лог был записан в {}'.format(self.log.path))

    def log_remove(self, num_list):
        self.log.log_list = [i for ind, i in enumerate(self.log.log_list) if i[0] not in num_list]
        self.log.log_list = [[ind] + i[1:] for ind, i in enumerate(self.log.log_list)]
        self.log.size -= len(self.log.log_list)

    def name2id(self, name):
        for id_name in self.person:
            if self.person[id_name].name == name:
                return id_name
class Person:
    def __init__(self, name, config, score=0, last=0, tran_type=None):
        self.name = name
        self.score = float(score)
        self.id = int(config['id'])
        self.last_update = int(last)
        self.renta = int(config['renta'])
        self.tran_type = tran_type

    def __repr__(self):
        ans = \
            'Имя: {}' \
            '\nСчет: {}' \
            '\nt.me id: {}'.format(
                self.name,
                int(round(self.score)),
                self.id
            )
        return ans

    def make_dict(self):
        return {
            'name': self.name,
            'score': self.score,
            'last': self.last_update,
            'tran_type': self.tran_type
        }


class Log:
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            self.log_list = []
            with open(path) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for line in reader:
                    self.log_list.append(
                        [int(line["id"]), line["name"], line["operation"], float(line["score"]), line["message"], datetime.strptime(line["date"], '%Y-%m-%d %H:%M:%S.%f')])
            self.size = len(self.log_list)
        else:
            self.size = 0
            self.log_list = []

    def push(self, name, operation, score, message=None):
        self.log_list.append([self.size, name, operation, score, message, datetime.now()])
        self.size += 1

    def show(self, num=None):
        if num is None:
            for i in self.log_list:
                print(self.log2st(i))
        else:
            for i in self.log_list[-num:]:
                print(self.log2st(i))

    def __repr__(self, shot=False):
        ans = 'Кол-во записей: {}'.format(
            int(self.size)
        )
        for i in self.log_list[-5:]:
            ans += '\n' + self.log2st(i, shot)
        return ans

    def log2st(self, ar, shot=False):
        if shot:
            ans = '|{:<3}|{:<10}|{:<5}|{:<6}|{:<15}|'.format(
                ar[0], ar[1], ar[2], int(ar[3]), 'None' if ar[4] is None else ar[4]
            )
        else:
            ans = '|{:<3}|{:<10}|{:<5}|{:<6}|{:<15}|{}|'.format(
                    ar[0], ar[1], ar[2], int(ar[3]), 'None' if ar[4] is None else ar[4], ar[5]
                )
        return ans