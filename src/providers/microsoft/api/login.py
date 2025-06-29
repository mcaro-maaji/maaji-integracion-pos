"""Modulo para acceder al la API de Login Microsoft Online"""

from typing import TypedDict, TypeGuard, NewType
from datetime import datetime, timezone, timedelta
from requests import request
from requests.exceptions import Timeout as RequestTimeoutError

LoginMicrosoftAuthorization = NewType("LoginMicrosoftAuthorization", str)

class LoginMicrosoftError(Exception):
    """Errores generales sobre la api Login, del proveedor Microsoft."""

class LoginMicrosoftFormAuth(TypedDict):
    """Estructura form-data para la peticion a la api del login en Microsoft"""
    grant_type: str
    client_id: str
    client_secret: str
    resource: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["LoginMicrosoftFormAuth"]:
        """Comprueba de que el objecto sea tipo `LoginMicrosoftFormAuth`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(att := obj.get("grant_type"), str) and att != "",
            isinstance(att := obj.get("client_id"), str) and att != "",
            isinstance(att := obj.get("client_secret"), str) and att != "",
            isinstance(att := obj.get("resource"), str) and att != ""
        ))

class LoginMicrosoftResponseAuth(TypedDict):
    """Estructura de la respuesta a la api sobre la autenticacion en Microsoft."""
    token_type: str
    expires_in: str
    ext_expires_in: str
    expires_on: str
    not_before: str
    resource: str
    access_token: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["LoginMicrosoftResponseAuth"]:
        """Comprueba de que el objecto sea tipo `LoginMicrosoftResponseAuth`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(att := obj.get("token_type"), str) and att != "",
            isinstance(att := obj.get("expires_in"), str) and att != "",
            isinstance(att := obj.get("ext_expires_in"), str) and att != "",
            isinstance(att := obj.get("expires_on"), str) and att != "",
            isinstance(att := obj.get("not_before"), str) and att != "",
            isinstance(att := obj.get("resource"), str) and att != "",
            isinstance(att := obj.get("access_token"), str) and att != ""
        ))

class LoginMicrosoft:
    """Controla los inicio de session en las aplicaciones de Microsoft"""
    __url: str | bytes
    __form: LoginMicrosoftFormAuth
    __response: LoginMicrosoftResponseAuth | None
    timeout: float | tuple[float, float]

    def __init__(self,
                 url: str | bytes,
                 obj: LoginMicrosoftFormAuth,
                 *,
                 timeout: float | tuple[float, float] = None):
        if not LoginMicrosoftFormAuth.validate(obj):
            raise TypeError("el valor debe ser de tipo LoginMicrosoftFormAuth")
        self.__url = url
        self.__form = obj
        self.__response = None
        self.timeout = timeout or 5

    @property
    def url(self):
        """URL para la peticion."""
        return self.__url

    @property
    def form(self):
        """Formulario para la peticion."""
        return self.__form

    @property
    def response(self):
        """Ultima respuesta de la api con el token de autenticacion."""
        return self.__response

    def getauth(self) -> LoginMicrosoftAuthorization:
        """Extrae la autorizacion desde la respuesta, lanza error si no hay."""
        if self.response is None:
            raise LoginMicrosoftError("no hay respuesta de la api Login Microsoft")

        token_type = self.response["token_type"]
        access_token = self.response["access_token"]
        auth = f"{token_type} {access_token}"
        return LoginMicrosoftAuthorization(auth)

    def is_expired(self, safe_margin: timedelta = None):
        """Comprueba si el token ha expirado"""
        if self.response is None:
            return True

        if safe_margin is None:
            safe_margin = timedelta(minutes=10)

        expires_on = float(self.response["expires_on"])
        expires_on = datetime.fromtimestamp(expires_on, tz=timezone.utc)
        expires_on_with_margin = expires_on - safe_margin
        now = datetime.now(timezone.utc)

        return now >= expires_on_with_margin

    def run(self,
            *,
            force=True,
            safe_margin: timedelta = None,
            timeout: float | tuple[float, float] = None) -> LoginMicrosoftAuthorization:
        """Corre la peticion y devuelve la autorizacion."""

        if not force and not self.is_expired(safe_margin):
            return self.getauth()

        if timeout is None:
            timeout = self.timeout

        try:
            response = request("POST", self.url, data=self.form, timeout=timeout)
        except RequestTimeoutError as err:
            msg = "tiempo de espera agotado para la api Login Microsoft"
            raise LoginMicrosoftError(msg) from err

        if not response.ok:
            raise LoginMicrosoftError("ocurrio un error en la peticion a la api Login Microsoft")

        obj = response.json()
        if not LoginMicrosoftResponseAuth.validate(obj):
            raise LoginMicrosoftError("la respuesta de la api Login Microsoft no es valida")

        self.__response = obj
        return self.getauth()

    @property
    def auth(self):
        """Obtener la autenticacion y refresca automaticamente."""
        return self.run(force=False)
