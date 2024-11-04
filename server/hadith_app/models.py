class User:
    def __init__(self, id, username, password, roles):
        self.id = id
        self.username = username
        self.password = password
        self.roles = roles


class HadithMeta:
    def __init__(self, book, chapter, number, reference, hadith_json):
        self.book = book
        self.chapter = chapter
        self.number = number
        self.reference = reference
        self.hadith_json = hadith_json


from enum import Enum


class HadithFetchMode(Enum):
    DAILY = 'daily'
    RANDOM = 'random'
