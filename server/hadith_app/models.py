class User:
    def __init__(self, id, username, password, roles):
        self.id = id
        self.username = username
        self.password = password
        self.roles = roles


class HadithMeta:
    def __init__(self, book, chapter, number):
        self.book = book
        self.chapter = chapter
        self.number = number


from enum import Enum


class HadithFetchMode(Enum):
    DAILY = 1
    RANDOM = 2
