import mysql.connector
from mysql.connector import Error


class Database:

    def __init__(self, database, user, password, host, port):
        """
        при создании обьекта создаем соединение
        :param database:
        :param user:
        :param password:
        :param host:
        :param port:
        """
        self.connection = self.connection(database, user, password, host, port)

    def __del__(self):
        """
        при разрушении Питон обьекта, закрываем соединение
        :return:
        """
        self.close_connection()

    @staticmethod
    def connection(database, user, password, host, port):
        """
        устанавливаем соединение с базой данных.
        используем клиент mysql.connector которому нужны следующие детали:
        :param database:
        :param user:
        :param password:
        :param host:
        :param port:
        :return:
        """
        try:
            conn = mysql.connector.connect(
                database=database,
                user=user,
                password=password,
                host=host,
                port=port
            )

            if conn.is_connected():
                return conn
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def close_connection(self):
        """
        закрываем соединение с БД
        :return:
        """
        self.connection.close()

    def execute_select_statement(self, target, table):
        """
        выбираем ряды из БД
        :param target:
        :param table:
        :return:
        """
        cursor = self.connection.cursor()
        base_query = f"select {target} from {table};"

        try:
            cursor.execute(base_query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
        finally:
            cursor.close()

    def execute_select_where(self, target, table, filters):
        """
        выбираем ряды которые подходят по запросы из БД
        :param target:
        :param table:
        :param filters:
        :return:
        """
        cursor = self.connection.cursor()
        base_query = f"select {target} from {table} where {filters};"

        try:
            cursor.execute(base_query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
        finally:
            cursor.close()

    def execute_update_statement(self, table, update, target_key, target_value):
        """
        обновляем ряды БД
        :param table:
        :param update:
        :param target_key:
        :param target_value:
        :return:
        """
        cursor = self.connection.cursor()
        base_query = f"update {table} set {update} where {target_key} = {target_value}"

        try:
            cursor.execute(base_query)
            self.connection.commit()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
        finally:
            cursor.close()

    def execute_insert_statement(self, table, values):
        """
        добавляем ряды БД
        :param table:
        :param values:
        :return:
        """
        cursor = self.connection.cursor()
        base_query = f"insert into {table} values ({values});"

        try:
            cursor.execute(base_query)
            self.connection.commit()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
        finally:
            cursor.close()
