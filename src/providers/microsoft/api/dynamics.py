"""Modulo para gestionar la api del ERP Dynamics 365"""

from typing import TypedDict, TypeGuard, Literal
from datetime import datetime, timedelta
from requests import request
from requests.exceptions import Timeout as RequestTimeoutError
from utils.env import Environment
from utils.constants import TZ_LOCAL
from .login import LoginMicrosoft

class DynamicsApiError(Exception):
    """Errores generales sobre la api de Dynamics."""

class DynamicsApiReqData(TypedDict):
    """Estructura de la peticion a la api de Dynamics 365, para consultar en la base de datos."""
    DataAreaId: str
    FecIni: str
    FecFin: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["DynamicsApiReqData"]:
        """Comprueba de que el objecto sea tipo `DynamicsApiReqData`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(att := obj.get("DataAreaId"), str) and att != "",
            isinstance(att := obj.get("FecIni"), str) and att != "",
            isinstance(att := obj.get("FecFin"), str) and att != "",
        ))

class DynamicsApiRequest(TypedDict):
    """Estructura de la peticion a la api de Dynamics 365"""
    _request: DynamicsApiReqData

    @classmethod
    def validate(cls, obj) -> TypeGuard["DynamicsApiRequest"]:
        """Comprueba de que el objecto sea tipo `DynamicsApiRequest`"""
        if not isinstance(obj, dict):
            return False
        return DynamicsApiReqData.validate(obj.get("_request"))

class DynamicsApiResponse(TypedDict):
    """Estructura de la respuesta de la api de Dynamics 365"""
    id: str
    ErrorMessage: str
    Success: bool
    DebugMessage: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["DynamicsApiResponse"]:
        """Comprueba de que el objecto sea tipo `DynamicsApiResponse`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(obj.get("$id"), str),
            isinstance(obj.get("ErrorMessage"), str),
            isinstance(obj.get("Success"), bool),
            isinstance(obj.get("DebugMessage"), str),
        ))

DynamicsKeyEnv = Literal["PROD", "UAT"]
DynamicsKeyApi = Literal[
    "BILLS:CEGID",
    "BILLS:SHOPIFY",
    "PRODUCTS:CEGID",
    "PRICES:CEGID"
]

class DynamicsApi:
    """Gestiona las peticiones a la api de Dynamics 365."""
    __env: str | bytes
    __path: str | bytes
    __login: LoginMicrosoft
    __response: DynamicsApiResponse | None
    timeout: float | tuple[float, float]
    data_area_id: str | None

    def __init__(self,
                 env: str | bytes,
                 path: str | bytes,
                 login: LoginMicrosoft,
                 timeout: float | tuple[float, float] = None,
                 data_area_id: str | None = None):
        self.__env = env
        self.__path = path
        self.__login = login
        self.__response = None
        self.timeout = timeout or (5, 600)
        self.data_area_id = data_area_id

    @property
    def env(self):
        """Es la URL del entorno en cual crear la api"""
        return self.__env

    @property
    def path(self):
        """Es la ruta de la URL de la api"""
        return self.__path

    @property
    def login(self):
        """Gestionado el login de Microsoft para obtener la autorizacion a la aplicacion."""
        return self.__login

    @property
    def response(self):
        """Ultima respuesta de la api."""
        return self.__response

    @property
    def headers(self):
        """Construye el encabezado de la peticion."""
        return {
            "Authorization": self.login.auth
        }

    def run(self, req: DynamicsApiRequest, timeout: float | tuple[float, float] = None):
        """Corre la peticion a la api de Dynamics 365"""

        if timeout is None:
            timeout = self.timeout

        url = self.env + self.path

        try:
            response = request("POST", url, headers=self.headers, json=req, timeout=timeout)
        except RequestTimeoutError as err:
            msg = f"tiempo de espera agotado para la api Dynamics: {self.path}"
            raise DynamicsApiError(msg) from err

        if not response.ok:
            msg = f"ocurrio un error en la peticion a la api Dynamics: {self.path}"
            raise DynamicsApiError(msg)

        obj = response.json()
        if not DynamicsApiResponse.validate(obj):
            msg = f"la respuesta no es valida de la api Dynamics: {self.path}"
            raise DynamicsApiError(msg)

        self.__response = obj
        return obj

    def getreq(self,
               *,
               data_area_id: str = None,
               date_end: datetime = None,
               date_start: datetime = None,
               apply_tzlocal: bool = True,
               offset: timedelta = None) -> DynamicsApiRequest:
        """Obtiene los datos de la peticion, usando las fechas facil de gestionar con datetime."""

        data_area_id = data_area_id if data_area_id else self.data_area_id
        offset = offset if offset else timedelta(hours=6)

        if date_end is None and date_start is None:
            date_end = datetime.now()

        if apply_tzlocal and not date_start is None:
            date_start = date_start.astimezone(TZ_LOCAL)

        if apply_tzlocal and not date_end is None:
            date_end = date_end.astimezone(TZ_LOCAL)

        if date_end is None and not date_start is None:
            date_end = date_start + offset

        if not date_end is None and date_start is None:
            date_start = date_end - offset

        return {
            "_request": {
                "DataAreaId": data_area_id,
                "FecIni": date_start.isoformat(),
                "FecFin": date_end.isoformat()
            }
        }

    # IDEA: cuando el rango de fechas es muy grande y tarda mucho en extraer los datos
    #       tratemos de hacer mas peticiones pero con fechas mas pequenas de forma automatica.

    def getdata(self,
                *,
                data_area_id: str = None,
                date_end: datetime = None,
                date_start: datetime = None,
                apply_tzlocal: bool = True,
                offset: timedelta = None) -> str:
        """Obtener los datos de la api."""

        req = self.getreq(
            data_area_id=data_area_id,
            date_end=date_end,
            date_start=date_start,
            apply_tzlocal=apply_tzlocal,
            offset=offset
        )

        obj = self.run(req)
        success = obj.get("Success")
        data = obj.get("DebugMessage")
        err = obj.get("ErrorMessage")
        err = "con el msg de error: " + err if err else ""

        if not success:
            raise DynamicsApiError(f"la api respondio sin exito en la operacion{err}")
        return data

    @classmethod
    def fromenv_login_microsoft(cls, resource: str):
        """Crea una instancia `LoginMicrosoft` para la api de Dynamics con variables de entorno."""
        login_microsoft_url = Environment.getenv("PROVIDER_MICROSOFT_API_DYNAMICS_AUTH_URL")
        grant_type = Environment.getenv("PROVIDER_MICROSOFT_API_DYNAMICS_AUTH_GRANT_TYPE")
        client_id = Environment.getenv("PROVIDER_MICROSOFT_API_DYNAMICS_AUTH_CLIENT_ID")
        client_secret = Environment.getenv("PROVIDER_MICROSOFT_API_DYNAMICS_AUTH_CLIENT_SECRET")

        return LoginMicrosoft(login_microsoft_url, {
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret,
            "resource": resource
        })

    @classmethod
    def fromenv(cls, key_env: DynamicsKeyEnv, key_api: DynamicsKeyApi):
        """Crea una instancia de `DynamicsApi` con las variables de entorno."""

        if key_env == "PROD":
            key_env = "PROVIDER_MICROSOFT_API_DYNAMICS_ENV_PROD"
        elif key_env == "UAT":
            key_env = "PROVIDER_MICROSOFT_API_DYNAMICS_ENV_UAT"
        else:
            raise DynamicsApiError("no se ha escogido un ambiente valido en DynamicsApi")

        if key_api == "BILLS:CEGID":
            key_api = "PROVIDER_MICROSOFT_API_DYNAMICS_URL_BILLS"
        elif key_api == "BILLS:SHOPIFY":
            key_api = "PROVIDER_MICROSOFT_API_DYNAMICS_URL_BILLS_SHOPIFY"
        elif key_api == "PRODUCTS:CEGID":
            key_api = "PROVIDER_MICROSOFT_API_DYNAMICS_URL_PRODUCTS_CEGID"
        elif key_api == "PRICES:CEGID":
            key_api = "PROVIDER_MICROSOFT_API_DYNAMICS_URL_PRICES_CEGID"
        else:
            raise DynamicsApiError("no se ha escogido una api valida en DynamicsApi")

        dynamics_env = Environment.getenv(key_env)
        dynamics_api = Environment.getenv(key_api)
        login_microsoft = cls.fromenv_login_microsoft(dynamics_env)
        data_area_id = Environment.getenv("PROVIDER_MICROSOFT_API_DYNAMICS_DATA_AREA_ID")

        return DynamicsApi(
            dynamics_env,
            dynamics_api,
            login_microsoft,
            data_area_id=data_area_id
        )
