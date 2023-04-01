# Client Code
import socket
import threading
import random
import sys
import logging
import logging.handlers as handlers
import ipaddress
from const import port_on_server, port_on_client, max_byte_off_file



# Ротация логов
logHandler = handlers.RotatingFileHandler(f'log_file_client.log',
                                          maxBytes= max_byte_off_file,
                                          backupCount=5) 
# Создаем пользовательский лог и задаем уровень логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Создаем обработчик и форматировщик
create_handler = logging.FileHandler(f'log_{__name__}.log', mode='a', encoding='utf-8')
create_formatter = logging.Formatter('[%(astime)s] : [%(levelname)s] : [%(message)s]')

# Добавляем форматировщику к обработчикe и логгер к обработчику
create_handler.setFormatter(create_formatter)
logger.addHandler(logHandler)


class Client:
    def __init__(self, serverIP: str) -> None:
        """Инициализация атрибутов класса"""
        self.host     = socket.gethostbyname(socket.gethostname())
        self.port     = port_on_client
        self.socket   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server   = (str(serverIP), port_on_server)
        self.name     = ""
        self.serverIP = serverIP
    
    def is_valid_ip(self, ip_addr: str) -> bool:
        """проверяет, действителен ли IP адресс """
        try:
            ipaddress.ip_address(ip_addr)
            return True
        except ValueError:
            return False

    def name_change(self) -> None:
        """Позволяет изменить имя"""
        logging.info("Активирована функция name_change")
        print(f"\nПривет {self.name} 🤔, здесь ты можешь поменять свое имя!")
        print("Для смена имени нужно ввести свое старое имя")
        wrongaAttempt = 0
        while wrongaAttempt != 5:
            confirmation = input("Введи свое старое имя --> ")
            if wrongaAttempt == 4:
                print("У ТЕБЯ ОСТАЛАСЬ ПОСЛЕДННЯ ПОПЫТКА")
            if confirmation == self.name:
                new_name = input(f"Успешно ✅, введи новое имя --> ")
                logging.info("Имя пользователя изменено ")
                self.name = new_name
                break
            else:
                wrongaAttempt += 1
                logging.info('неправильный ввод старого имени')
                print("Имена не совпадают, попробуй еще раз у тебя осталось",
                      f'{5 - wrongaAttempt }')
                continue
            
    def change_connection(self) -> None:
        """Настройка подключение. Изменение IP и порта"""
        question = ''   
        while question != '/exit':
            logging.info("Активирована функция change_connection")
            print(f"\nТвой IP - {self.host}, Твой порт - {self.port}")
            print("Ты можешь - сменить порт (введите: порт)")
            print("И сменить IP подключаемого сервера (введите: сменить IP)")
            print("Ты можешь выйти (/exit)")

            question = input("\nЧто ты хочешь изменить? - ")
            if question.lower() == 'порт':
                print('\nТы можешь выбрать порт самостоятель или взять рандомный')
                try:
                    answer = int(input("Первое или второе?: (введи ответ цифрой) - "))
                except ValueError:
                    print("Ответ нужно ввести цифрой!!!!")
                    logging.exception('ValueError')
                    self.change_connection()
                else:
                    if answer == 1:
                        new_port = int(input("Выбери порт (от 8001 до 65535) - "))
                        self.port = new_port
                        logging.info("Изменен port в ручную")
                        break
                    if answer == 2:
                        new_port  = random.randint(8001, 65535)
                        self.port = new_port
                        logging.info("Изменен port рандомно")
                        print(f"Порт изменен на {self.port}")
                        break

            elif question.lower() == 'сменить ip':
                print(f'\nСейчас ты подключен к серверу с IP {self.serverIP}')
                new_serverIP = input("Введите новый IP сервера - ")

                # проверка действителен ли IP 
                if self.is_valid_ip(new_serverIP): 
                    logging.info("БЫЛ ИЗМЕНЕН IP КЛИЕНТА")
                    print(f"IP сервера успешно ✅ изменен на {serverIP}")
                    logging.info("БЫЛ ИЗМЕНЕН IP КЛИЕНТА")
                    main(new_serverIP) 
                else:
                    print(f"IP - {new_serverIP} --> недействителен")
            elif question.lower() != 'сменить ip' or 'порт' or '/exit':
                print("Не найдено данного ответа, попробуй еще раз!")
                continue
            exit()
    
    def help(self) -> str:
        """Выводит все доступные команды для клиента"""
        logging.info("Активирована функция help")
        print("\nПомощь:\n1) Поменять имя - /new_name\n") 
        print("2) Настроить подключение - /change_connection")
        print('3) Разорвать подключение - /disconnect')
        exit() 

    def receive_data(self) -> None:
        """Получат данные"""
        while True:
            data, addr = self.socket.recvfrom(1024)
            print(data.decode('utf-8'))

    def run(self) -> None:
        """Запускает работы сокета"""
        print(f'\nКлиент IP -> {self.host} : Порт -> {self.port}')
        logging.info(f'\n Был подключен Клиент IP -> {self.host} : Порт -> {self.port}')
        with self.socket:
            self.socket.bind((self.host, self.port))
            print(f'Вы подключены к серверу {self.serverIP}')
            self.name = input("Как тебя зовут?: ")
            if self.name == "":
                self.name = f'Гость - {random.randint(1, 999999)}'
                print(f'Тебя зовут - {self.name}')
            logging.info(f"Был присоединен новый пользователь {self.name}")
            data = f'{self.name} присоединился'
            self.socket.sendto(data.encode('utf-8'), self.server)

            # параллельная работа функции receive_data
            thread = threading.Thread(target=self.receive_data)
            thread.start()
            
            print("Привет! На сервере у тебя есть несколько возможностей")
            print("Ты можешь (в скобках написана команда которую нужно ввести)\n")
            print('1) Сменить ник (команда - /new_name)') 
            print('2) Настроить подключение (команда - /change_connection)')
            print('3) Разорвать соединение (команда - /disconnect)')
            print('4) Все возможные команды /help')
            
            while True:
                data = input('Напиши сообщение: ')
                if data == '':
                    continue
                elif data == '/new_name':
                    self.name_change()
                    continue
                elif data == '/change_connection':
                    self.change_connection()
                    continue
                elif data == '/disconnect':
                    break
                elif data == '/help':
                    self.help()
                    continue
                else:
                    fitler_word = {'питон': 'python', "джава": 'java', 'хтмль': 'html',
                    'негр': 'афроамериканец', "убить": 'ЗАПРЕТНОЕ СЛОВО',
                    "смерть": 'ЗАПРЕТНОЕ СЛОВО'}

                    for key in fitler_word.keys(): # Фильтр по cловам
                        if key == data:
                            data = fitler_word[key]
                    data = f'[{self.name}] -> {data}'
                    self.socket.sendto(data.encode('utf-8'), self.server)
                    continue


def main(serverIP):
    client = Client(serverIP)
    client.run()

if __name__ == '__main__':
    try:
        serverIP = sys.argv[1]
        main(serverIP)
    except IndexError:
        print("ФАЙЛ ЗАПУСКАЕТСЯ С КОНСОЛИ\n--> client.py <IP server>")
    
                

                    

                