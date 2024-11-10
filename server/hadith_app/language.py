import iso639

EN = 'en'
AR = 'ar'

SUPPORTED_LANGUAGES = [EN, AR]


def is_supported_lang(lang_code: str):
    return iso639.is_valid639_1(lang_code) and lang_code in SUPPORTED_LANGUAGES
