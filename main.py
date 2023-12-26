# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sqlite3
import bcrypt
import random


class Photocenter:
    def __init__(self, db_name='Photocenter'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS photo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        self.conn.commit()

        self.cursor.execute('DELETE FROM photo')
        self.conn.commit()

        self.cursor.execute('DELETE FROM sqlite_sequence WHERE name="photo"')
        self.conn.commit()

        self.cursor.executemany('INSERT INTO photo (name, price) VALUES (?, ?)', [
            ('Фото стандарт', 20),
            ('Фото премиум', 38),
            ('Фото 10x15', 25),
            ('Фото 10x15 премиум с подписью', 63),
            ('Фото Polaroid', 100),
            ('Фото 10x10', 18),
            ('Фотографии 15х20', 75),
            ('Фотографии 30х45', 150)
        ])
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                photo_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(photo_id) REFERENCES photo(id)
            )
        ''')
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                address TEXT,
                total_amount REAL,
                order_number INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def close_connection(self):
        self.conn.close()



class User:
    def __init__(self, photocenter):
        self.photocenter = photocenter
        self.authenticated_user = None

    def validate_credentials(self, login, password):
        if not login.strip() or not password.strip():
            print("----------Логин и пароль не могут быть пустыми. Пожалуйста, попробуйте снова.----------")
            return False
        return True

    def authenticate(self, login, password):
        if not self.validate_credentials(login, password):
            return False

        self.photocenter.cursor.execute('SELECT * FROM users WHERE login = ?', (login,))
        existing_user = self.photocenter.cursor.fetchone()

        if existing_user and bcrypt.checkpw(password.encode('utf-8'), existing_user[2]):
            self.authenticated_user = existing_user
            return True
        else:
            print("----------Неправильный логин или пароль. Пожалуйста, попробуйте снова.----------")
            return False

    def display_photo(self):
        self.photocenter.cursor.execute('SELECT * FROM photo')
        photo = self.photocenter.cursor.fetchall()
        print("----------------Фото----------------")
        for photo in photo:
            print(f"{photo[0]}. {photo[1]} - ₽{photo[2]}")
        return photo

    def add_to_cart(self, photo_id):
        self.photocenter.cursor.execute('INSERT INTO shopping_cart (user_id, photo_id) VALUES (?, ?)',
                                  (self.authenticated_user[0], photo_id))
        self.photocenter.conn.commit()

class Client(User):
    def __init__(self, photocenter):
        super().__init__(photocenter)

    def validate_photo_id(self, photo_id, photo):
        try:
            photo_id = int(photo_id)
            if not (1 <= photo_id <= len(photo)):
                print(
                    "----------Неверный номер товара(. Пожалуйста, попробуйте снова.----------")
                return False
            return True
        except ValueError:
            print(
                "----------Неверный ввод(. Пожалуйста, введите число.----------")
            return False

    def add_to_cart(self, photo_id):
        photo = self.display_photo()
        if not self.validate_photo_id(photo_id, photo):
            return

        self.photocenter.cursor.execute('INSERT INTO shopping_cart (user_id, photo_id) VALUES (?, ?)',
                                  (self.authenticated_user[0], photo_id))
        self.photocenter.conn.commit()

    def display_cart(self):
        self.photocenter.cursor.execute('''
            SELECT photo.name, photo.price
            FROM shopping_cart
            JOIN photo ON shopping_cart.photo_id = photo.id
            WHERE shopping_cart.user_id = ?
        ''', (self.authenticated_user[0],))
        cart_items = self.photocenter.cursor.fetchall()

        def display_photo(self):
            return super().display_photo()

        if cart_items:
            total_sum = sum(item[1] for item in cart_items)
            print("----------Товары в вашей корзине:----------")
            for item in cart_items:
                print(f"{item[0]} - ₽{item[1]}")
            print(f"----------Общая сумма: ₽{total_sum}----------")
        else:
            print("----------Ваша корзина пуста(----------")

    def checkout(self, address):
        self.photocenter.cursor.execute('''
            SELECT photo.price
            FROM shopping_cart
            JOIN photo ON shopping_cart.photo_id = photo.id
            WHERE shopping_cart.user_id = ?
        ''', (self.authenticated_user[0],))
        prices = self.photocenter.cursor.fetchall()
        total_sum = sum(price[0] for price in prices)

        order_number = random.randint(1000, 9999)

        self.photocenter.cursor.execute('''
            INSERT INTO orders (user_id, address, total_amount, order_number)
            VALUES (?, ?, ?, ?)
        ''', (self.authenticated_user[0], address, total_sum, order_number))
        self.photocenter.conn.commit()

        self.photocenter.cursor.execute('DELETE FROM shopping_cart WHERE user_id = ?', (self.authenticated_user[0],))
        self.photocenter.conn.commit()

        print("Заказ был успешно оформлен!")
        print(f"Ваш номер заказа №{order_number}")
        print("--------------------")
        print(f"Итоговая сумма: ₽{total_sum}")
        print("Благодарим вас за ваш заказ! Если вы хотите отследить доставку, используйте указанный номер для отслеживания.")

class Administrator(User):
    ADMIN_USERNAME = "Photocenter_Print"
    ADMIN_PASSWORD = "1111"

    def authenticate(self, login, password):
        return login == self.ADMIN_USERNAME and password == self.ADMIN_PASSWORD

    def add_photo(self, name, price):
        self.photocenter.cursor.execute('INSERT INTO photo (name, price) VALUES (?, ?)', (name, price))
        self.photocenter.conn.commit()

    def remove_photo(self, name):
        self.photocenter.cursor.execute('DELETE FROM photo WHERE name = ?', (name))
        self.photocenter.conn.commit()

    def change_photo_name(self, current_name, new_name):
        self.photocenter.cursor.execute('UPDATE photo SET name = ? WHERE name = ?', (new_name, current_name))
        self.photocenter.conn.commit()


photocenter = Photocenter()

while True:
    print("----------Чтобы войти в Photocenter_Print, вам необходимо авторизоваться или зарегистрироваться----------")

    print("1. - Авторизоваться")
    print("2. - Зарегистрироваться")
    print("3. - Выйти")
    choice = input("Выберите действие: ")

    if choice == '1':
        print("------------Авторизация------------")
        print("1. - Авторизоваться как клиент")
        print("2. - Авторизоваться как сотрудник")
        print("3. - Вернуться назад")
        auth_choice = input("Выберите действие: ")

        if auth_choice == '1':
            client = Client(photocenter)

            while True:
                login_client = input("Введите ваш логин: ")
                password_client = input("Введите ваш пароль: ")

                if login_client.strip() and password_client.strip():
                    break
                else:
                    print("----------Логин и пароль не могут быть пустыми. Пожалуйста, попробуйте снова.----------")

            if client.authenticate(login_client, password_client):
                print("Авторизация прошла успешно!")
            else:
                continue

            while True:
                print("----------Добро пожаловать в Photocenter_Print!----------")
                print("1. - Фото")
                print("2. - Корзина")
                print("3. - Выйти")

                client_action = input("Выберите действие: ")

                if client_action == '1':
                    client.display_photo()
                    add_to_cart = input("Введите номер товара для добавления в корзину или '0' чтобы вырнуться назад:")

                    if add_to_cart == '0':
                        continue

                    try:
                        photo_id = int(add_to_cart)
                        photo = client.display_photo()
                        if 1 <= photo_id <= len(photo):
                            client.add_to_cart(photo_id)
                            print(f"----------Выбранный товар '{photo[photo_id - 1][1]}' был добавлен в корзину.----------")
                        else:
                            print("----------Неверный номер товара. Пожалуйста, попробуйте снова.----------")
                    except ValueError:
                        print("----------Неверный ввод. Пожалуйста, введите число.----------")

                elif client_action == '2':
                    client.display_cart()

                    print("1. - Оформить заказ")
                    print("2. - Вернуться назад")
                    cart_choice = input("Выберите действие: ")

                    if cart_choice == '1':
                        print("-----------------Оформление заказика-----------------")

                        address = input("Введите адрес доставки: ")
                        client.checkout(address)
                        break

                    elif cart_choice == '2':
                        continue

                elif client_action == '3':
                    print("----------До свидания, приходите к нам ещё :3!----------")
                    break

        elif auth_choice == '2':
            administrator = Administrator(photocenter)

            while True:
                administrator_login = input("Введите логин: ")
                administrator_password = input("Введите пароль: ")

                if administrator_login.strip() and administrator_password.strip():
                    break
                else:
                    print("-----------Логин и пароль не могут быть пустыми. Пожалуйста, попробуйте снова.-----------")

            if administrator.authenticate(administrator_login, administrator_password):
                print("Авторизация прошла успешно!")

                while True:
                    print("----------Что бы вы хотели изменить в Photocenter_Print?----------")
                    print("1. - Добавить товар")
                    print("2. - Удалить товар")
                    print("3. - Изменить название товара")
                    print("4. - Выйти")

                    administrator_action = input("Выберите действие: ")

                    if administrator_action == '1':
                        print("-----------------Идёт процесс добавления товара...-----------------")
                        while True:
                            photo_name = input("Введите название товара: ")
                            photo_price = input("Введите цену товара: ")
                            try:
                                photo_price = float(photo_price)
                                if photo_name.strip() and photo_price >= 0:
                                    administrator.add_photo(photo_name, photo_price)
                                    print(f"---------------Товар '{photo_name}' был успешно добавлен.---------------")
                                    break
                                else:
                                    print("---------------Название товара не может быть пустым, а цена должна быть неотрицательной.---------------")
                            except ValueError:
                                print("---------------Неверный формат цены. Пожалуйста, введите число.---------------")

                    elif administrator_action == '2':
                        print("---------------Процесс удаления товара...---------------")
                        while True:
                            photo_name_to_delete = input("Введите название товара для удаления или '0' чтобы вернуться назад: ")

                            if photo_name_to_delete == '0':
                                break

                            administrator.remove_photo(photo_name_to_delete)
                            print(f"---------------Товар '{photo_name_to_delete}' успешно удален.---------------")
                            break

                    elif administrator_action == '3':
                        print("---------------Идёт процесс изменения в названии товара...---------------")
                        while True:
                            photo_name_to_change = input("Введите название товара для изменения или '0' чтобы вернуться назад: ")

                            if photo_name_to_change == '0':
                                break

                            new_photo_name = input("Введите новое название товара: ")
                            administrator.change_photo_name(photo_name_to_change, new_photo_name)
                            print(f"---------------Название товара было успешно изменено на '{new_photo_name}'.---------------")
                            break

                    elif administrator_action == '4':
                        print("-----------------Выход был успешно выполнен!-----------------")
                        break
            else:
                print("---------------Неправильный логин или пароль. Пожалуйста, попробуйте снова.---------------")

    elif choice == '2':
        print("-----------Регистрация-----------")
        print("Логин должен быть не менее 4 символов")

        while True:
            login_client = input("Придумайте ваш логин: ")

            if len(login_client) >= 4:
                break
            else:
                print("---------------Логин должен содержать не менее 4 символов и не должен быть пустым. Пожалуйста, попробуйте снова.---------------")

        while True:
            password_client = input("Придумайте ваш пароль: ")

            if len(password_client) > 0:
                break
            else:
                print("---------------Пароль не может быть пустым. Пожалуйста, попробуйте снова.---------------")

        photocenter.cursor.execute('SELECT * FROM users WHERE login = ?', (login_client,))
        existing_user = photocenter.cursor.fetchone()

        if existing_user:
            print("---------------Пользователь с таким логином уже существует(. Пожалуйста, выберите другой логин.---------------")


        else:

            hashed_password = bcrypt.hashpw(password_client.encode('utf-8'), bcrypt.gensalt())

            photocenter.cursor.execute('INSERT INTO users (login, password) VALUES (?, ?)', (login_client, hashed_password))

            photocenter.conn.commit()

            print("Регистрация прошла успешно!")

    elif choice == '3':
        print("---------------Вы успешно вышли из Photocenter_Print!---------------")
        break

    else:
        print("---------------Неправильный ввод(. Пожалуйста, попробуйте снова.---------------")

photocenter.close_connection()