import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class Database:

    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            autocommit=False,
        )

    def cursor(self):
        return self.connection.cursor(dictionary=True)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()
