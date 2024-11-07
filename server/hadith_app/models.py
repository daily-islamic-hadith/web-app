class User:
    def __init__(self, id, username, password, roles):
        self.id = id
        self.username = username
        self.password = password
        self.roles = roles


class HadithMeta:
    def __init__(self, reference, hadith_json, ar_explanation, en_explanation):
        self.reference = reference
        self.hadith_json = hadith_json
        self.ar_explanation = ar_explanation
        self.en_explanation = en_explanation


from enum import Enum


class HadithFetchMode(Enum):
    DAILY = 'daily'
    RANDOM = 'random'
