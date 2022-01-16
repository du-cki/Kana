import pymongo
from pymongo import MongoClient
from certifi import where

class MongoConnnection:
    def __init__(self, connection_url, collection_name, document_name):
        cluster = MongoClient(connection_url, tlsCAFile=where())
        db = cluster[collection_name]
        self.connection = db[document_name]

    def get(self, query=dict):
        """ Find one item and return it should it exist"""
        return self.connection.find_one(query)

    def update(self, query=dict, update=dict):
        """ Find one item, and then update it """
        return self.connection.find_one_and_update(query, update)

    def delete(self, query):
        """ Find one item, and then delete it """
        return self.connection.find_one_and_delete(query)

    def insert(self, document=dict):
        """ Inserts a document into DB """
        return self.connection.insert_one(document)
