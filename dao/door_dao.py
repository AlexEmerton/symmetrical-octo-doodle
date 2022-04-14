from flask import jsonify

from models.door import Door


class DoorDao:
    """
    Обьект для доступа в базу данных для дверей
    """
    DOOR_TABLE = "doors_"
    
    def __init__(self, connection):
        self.connection = connection

    def get_all(self):
        """
        достать все ряды из базы данных для таблицы дверей
        :return:
        """
        all_doors = self.connection.execute_select_statement("*", self.DOOR_TABLE)

        return all_doors

    def get_by_id(self, _id):
        """
        достать все ряды из базы данных где ID двери подходит тому который был дан функции
        :param _id:
        :return:
        """
        door = self.connection.execute_select_where("*", self.DOOR_TABLE, f"id={_id}")
        return Door(
            door[0][0],
            door[0][1],
            door[0][2],
            door[0][3],
            door[0][4],
            door[0][5])

    def add(self, door: Door):
        """
        добавить дверь в базу данных
        :param door:
        :return:
        """
        query = f"{door.id}, \"{door.name}\", {door.price}, \"{door.size}\", \"{door.color}\", \"{door.image}\""

        results = self.connection.execute_insert_statement(self.DOOR_TABLE, query)

        return jsonify(results)

    def update(self, door: Door, target_key, target_value):
        """
        обновить дверь в базе данных
        :param door:
        :param target_value:
        :param target_key:
        :return:
        """
        query = f"Name='{door.name}', Price='{door.price}', Size='{door.size}', Color='{door.color}', ImageLink='{door.image}'"
        results = self.connection.execute_update_statement(
            self.DOOR_TABLE,
            query,
            target_key,
            target_value
        )
        return jsonify(results)
