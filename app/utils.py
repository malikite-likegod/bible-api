from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def hash (password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def is_password_complexity_valid(password):
    regex = re.compile(
        # Must have:
        #  1 Capital letter, 
        # 1 Lower Case, 
        # 1 Number, 
        # 1 Special Char,
        # 8 characers in Length
        r'^(?=.*[A-Z])(?=.*\d)(?=.*[ !"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~])[A-Za-z\d !"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]{8,}$'
    )
    return bool(regex.match(password))