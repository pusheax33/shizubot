from pymongo import MongoClient
import pprint

class Connect():

    @staticmethod
    def get_connection():
        return MongoClient()

    def main(self):
        client = self.get_connection()
        db = client.shizu
        server_data = {
            "guild_id": 542131654651321,
            "guild_name": "Familia Tomate",
            "owner_id": 543534534534534,
            "members_id": [423423432, 423423423, 47524742, 11547865]
        }

        server_data_db = db.serverdata
        server_data_id = server_data_db.insert_one(server_data)
        print(server_data_id)

Connect().main()