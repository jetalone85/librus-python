class Config:
    BASE_URL = "https://synergia.librus.pl"
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
    AUTH_URL = "https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata"
    LOGIN_URL = "https://api.librus.pl/OAuth/Authorization?client_id=46"
    TWO_FA_URL = "https://api.librus.pl/OAuth/Authorization/2FA?client_id=46"
    LOGIN_DATA_ACTION = 'login'
