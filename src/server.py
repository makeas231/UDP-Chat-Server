# Server Code
import socket
import queue
import threading
import logging
import logging.handlers as handlers 
from const import port_on_server, max_byte_off_file



# Ротация логов
file_handler = handlers.RotatingFileHandler(f'log_file_server.log',
                                            maxBytes= max_byte_off_file,
                                            backupCount=5)

# Создаем пользовательский лог и задаем уровень логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика для logger
handler = logging.FileHandler(f"server.log", mode='a', encoding='utf-8')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler.setFormatter(formatter)
# добавление обработчика к логгеру
logger.addHandler(file_handler)


class Server:
    def __init__(self):
        """Инициализация атрибутов класса """
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port_on_server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = set()
        self.recvPackets = queue.Queue()
        self.ban_list = list()

    def recv_data(self) -> None:
        """Получает данные"""
        while True:
            data, addr = self.socket.recvfrom(1024)
            self.recvPackets.put((data, addr))
    
    def on_board_computer(self) -> None:
        """Активирует бортовой компьютер (типо управление сервером)"""
        print("\nВы активировали бортовой компьютер на сервере, с помощью него")
        question = ''
        while question != "/exit":
            try:
                print("Вы можете: \n1)Банить участников\n2)Поменять порт сервера")
                print("3) Посмотреть список всех активных пользователей")
                print("4)Выключить борт-комп (/exit)")
                question = int(input("Что вы хотите сделать(ответ введите цифрой) - "))
            except ValueError:
                print("ВВЕДИТЕ ОТВЕТ ЦИФРОЙ!!!")
                logging.exception('ValueError')
                self.on_board_computer()
            else:
                if question == 1:
                    port_banner = int(input("Введите port кого вы хотите удалить"))
                    ban_of_client = 'ban_of_you.Error250'
                    answer = list(self.clients)
                    if port_banner in self.clients:
                        for ip, port in answer:
                            if port == port_banner:
                                self.socket.sendto(ban_of_client.encode('utf-8'), (ip, port))
                                self.clients.remove((ip, port))
                                self.ban_list.append((ip, port))
                                logging.warning(f"Пользователь {ip} {port} получил бан")
                    else:
                        print("НЕ СУЩЕСТВУЕТ АКТИВНОГО ПОЛЬЗОВАТЕЛЯ С ДАННЫМ ПОРТОМ\n")

                if question == 2:
                    print(f"Ваш сервера работает на порту {self.port}")
                    new_port = input("Введите новый порт --> ")
                    if 4 <= len(new_port) >= 5:
                        logging.info(f'Сервер под IP {self.host} изменил порт',
                                     f'на {self.port}')
                        self.port = new_port
                    else:
                        print(f"{new_port} - не может быть устанавовлен, так как"
                              f"длина порта должна быть в диапазоне от 4 до 5 цифр")
                if question == 3:
                    print(f"\nСПИСОК ВСЕХ АКТИВНЫХ УЧАСТНИКОВ СЕРВЕРА -->")
                    print(f'{self.clients}')

    def run(self) -> None:
        """Запускает сам сокет"""
        print(f'Сервер расположен на IP -> {self.host}')
        logger.info(f'Сервер запущен на IP -> {self.host}, Port -> {self.port}')
        with self.socket:
            self.socket.bind((self.host, self.port))
            print('Сервер начал свою работу...')
            threading.Thread(target=self.recv_data).start() # Создаем поток
            threading.Thread(target=self.on_board_computer).start()

            fitler_word = {'питон': 'python', "джава": 'java', 'хтмль': 'html',
                'негр': 'афроамериканец', "убить": 'ЗАПРЕТНОЕ СЛОВО',
                "смерть": 'ЗАПРЕТНОЕ СЛОВО'}
            while True:
                while not self.recvPackets.empty():
                    data, addr = self.recvPackets.get()
                    if addr not in self.ban_list:
                        if addr not in self.clients:
                            self.clients.add(addr)
                        data = data.decode('utf-8')
                        for key in fitler_word.keys(): # Фильтр по cловам
                            if data == key:
                                data = fitler_word[key]
                                logging.info(f"Сработал фильтр слов - {data}")
                        if data.endswith('/exit'):
                            self.clients.remove(addr)
                            logging.info(f'{addr} - покинул сервер')
                            print("Ждем снова :-)")
                            continue         
                        logging.info(f'[{addr}] : {data}')
                        print(f'[{addr}] : [{data}]')
                        for client in self.clients:
                            if client != addr:
                                self.socket.sendto(data.encode('utf-8'), client)
            

if __name__ == '__main__':
    server = Server()
    server.run()



# Спросить о том как сделать так чтобы когда у нас запущен бортовой компьютер
# сообщения которые приходят с клиента не будут перекрывать input()