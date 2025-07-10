"""Modulo para gestionar las variables de entorno y la criptografia de claves secretas."""

from typing import Literal
from functools import lru_cache
from os import environ
from getpass import getpass
from base64 import urlsafe_b64encode
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from utils.constants import PATH_STATIC_DATA

class IncorrectCredentials(InvalidToken):
    """Lanzar un error al momento de obtener claves secretas con usuario y contraseña."""

def derive_key(salt_key: bytes, user: bytes, password: bytes) -> bytes:
    """Deriva una clave segura."""
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt_key, iterations=390000)
    key = kdf.derive(user + password)
    return urlsafe_b64encode(key)

def unlock_env(key: str, user: bytes, password: bytes, *salt: bytes) -> str:
    """Descifra una variable de entorno y devuelve su valor."""

    salt_key = environ.get("SALT_KEY")
    secret_key = environ.get("SECRET_KEY")
    variable_env = environ.get(key)

    if not salt_key or not secret_key or not variable_env:
        raise ValueError("variables secretas no establecidas en el entorno, llave: " + key)

    salt_key = salt_key.encode()
    salt_key += b"".join(salt)

    try:
        secret_key = Fernet(derive_key(salt_key, user, password)).decrypt(secret_key)
        variable_env = Fernet(secret_key).decrypt(variable_env)
    except InvalidToken as err:
        raise IncorrectCredentials("el usuario y contraseña no son validos") from err

    return variable_env.decode()

class _Environment:
    """Gestionar el entorno de ejecucion y las variables cifradas."""
    _instance = None
    _env: Literal["default", "development", "production"]
    salt: list[bytes]
    user: bytes
    password: bytes

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._env = "default"
            cls._instance.salt = []
            cls._instance.user = b""
            cls._instance.password = b""
        return cls._instance

    def set_salt(self, *salt: bytes):
        """Configura usuario y contraseña para el entorno."""
        if not salt:
            raise ValueError("no hay sal para establecer en el entorno.")
        if not all(isinstance(s, bytes) for s in salt):
            raise TypeError("la sal debe ser de tipo bytes.")
        self.salt = salt

    def set_credentials(self, user: bytes, password: bytes):
        """Configura usuario y contraseña para el entorno."""
        self.user = user
        self.password = password

    @lru_cache
    def getenv(self, key: str, *salt: bytes, user: bytes = None, password: bytes = None) -> str:
        """Obtiene variable de entorno descifrada, cacheando el resultado."""

        env = environ.get("ENVIRONMENT")
        if env == "development:local":
            value = environ.get(key)
            if not value:
                raise ValueError("no existe la variable de entorno con la llave: " + key)
            return value

        user = user if user is not None else self.user
        password = password if password is not None else self.password
        salt = salt if salt else self.salt

        if not user or not password:
            raise IncorrectCredentials("usuario y contraseña no establecidos")

        value = unlock_env(key, user, password, *salt)

        if user is None or password is None:
            self.user = user
            self.password = password

        return value

    def is_login(self) -> bool:
        """Comprueba que las credenciales ingresadas en el entorno sean las correctas."""
        key = "ENVIRONMENT"
        try:
            self._env = unlock_env(key, self.user, self.password, *self.salt).split(":")[0]
        except IncorrectCredentials:
            return False
        return True

    @property
    def env(self):
        """Verifica el tipo de entorno de ejecucion."""
        support_env = ["development", "production"]

        if ":" in self._env:
            self._env = self._env.split(":")[0]

        if self.is_login() and self._env in support_env:
            return self._env
        return "default"

    def login(self, *salt: bytes):
        """Pide usuario y contraseña por medio de CLI, lanza error sino."""

        user = input("Ingresar usuario: ").encode()
        password = getpass("Ingresar contraseña: ").encode()

        self.set_credentials(user, password)
        if salt:
            self.set_salt(*salt)

        if not self.is_login():
            raise IncorrectCredentials("el usuario y contraseña no son validos")

Environment = _Environment()

def exists_key_file():
    """Comprueba de que exista el archivo de llave para acceder a las variables de entorno"""
    return (PATH_STATIC_DATA / ".key").is_file()

if exists_key_file():
    load_dotenv(PATH_STATIC_DATA / ".key", override=True)
