import streamlit as st
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from uuid import uuid4

class DBClient:
    """
    A client for handling MongoDB connections and operations.
    """
    def __init__(self):
        self.client = None

    def get_connection(self):
        """
        Establishes and returns a MongoDB client connection.
        Reads the connection string from Streamlit secrets.
        """
        if self.client is None:
            try:
                connection_string = st.secrets["mongo_connection_string"]
                self.client = MongoClient(connection_string, uuidRepresentation='standard')
            except KeyError:
                st.error("MongoDB connection string not found in st.secrets.")
                return None
            except Exception as e:
                st.error(f"Failed to create MongoDB client: {e}")
                return None
        return self.client

    def check_connection(self):
        """
        Checks the connection to the MongoDB server by pinging it.
        Returns True if the connection is successful, False otherwise.
        """
        client = self.get_connection()
        if client:
            try:
                # The ismaster command is cheap and does not require auth.
                client.admin.command('ismaster')
                return True
            except ConnectionFailure:
                return False
        return False

    def get_currency_rate_by_date(self, date_str: str):
        """
        Retrieves the currency rate for a given date string (e.g., "2025/08/24").
        """
        client = self.get_connection()
        if not client:
            return None
        db = client["prod"]
        collection = db["currency_rate"]
        query = {"date": date_str}
        return collection.find_one(query)

    def get_latest_currency_rate(self):
        """
        Retrieves the latest currency rate from the database.
        """
        client = self.get_connection()
        if not client:
            return None
        db = client["prod"]
        collection = db["currency_rate"]
        # Sort by timestamp in descending order and get the first one
        latest_rate = collection.find_one(sort=[("date", DESCENDING)])
        return latest_rate

    def insert_currency_rate(self, base: str, target: str, date_str: str, rate: float):
        """
        Inserts a new currency rate record into the database.
        """
        client = self.get_connection()
        if not client:
            st.error("Failed to get DB connection for insertion.")
            return None
        db = client["prod"]
        collection = db["currency_rate"]
        document = {
            "_id": str(uuid4()),
            "base": base,
            "target": target,
            "date": date_str,
            "rate": rate
        }
        try:
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            st.error(f"Failed to insert currency rate into DB: {e}")
            return None
