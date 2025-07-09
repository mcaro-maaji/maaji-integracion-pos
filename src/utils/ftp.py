"""Modulo para controlar las conexiones FTP."""

from typing import NamedTuple
from io import IOBase
from os import PathLike, fspath
from datetime import datetime, timedelta
from time import sleep as time_sleep
from socket import error as SocketError
from fnmatch import fnmatch
from ftputil import FTPHost
from ftputil.error import FTPError
from app.logging import get_logger
from .env import Environment

logger = get_logger("app", "ftp")
DS_FTP: dict["FTPID", "FTP"] = {}

class FTPID(NamedTuple):
    """Identificador de una conexion FTP."""
    name: str
    host: str

class FTP:
    """Clase para escalar y gestionar conexiones a servidores FTP."""

    def __init__(self, host: str, user: str = "", password: str = ""):
        self.host = host
        self.user = user
        self.password = password
        self.conn: FTPHost | None = None

        # configuracio de reintentos
        self.max_retries = 5
        self.initial_backoff = 1  # en segundos

    def _is_connected(self) -> bool:
        """Valida si la conexión sigue activa"""
        if self.conn is None:
            return False

        try:
            self.conn.getcwd()
            return True
        except (FTPError, OSError, SocketError):
            return False

    def connect(self):
        """Conecta con reintentos y backoff."""
        if self._is_connected():
            return

        self.disconnect()

        retries = 0
        backoff = self.initial_backoff

        while retries < self.max_retries:
            try:
                logger.info("Intentado conectar a '%s' (Intento %d)", self.host, retries + 1)
                self.conn = FTPHost(self.host, self.user, self.password)
                self.conn.getcwd()
                logger.info("Conectado exitosamente a '%s'", self.host)
                return
            except (FTPError, OSError, SocketError) as err:
                logger.warning("Fallo al conectar a '%s', %s", self.host, str(err))
                retries += 1
                if retries < self.max_retries:
                    logger.info("Reintentando en %d segundos", backoff)
                    time_sleep(backoff)
                    backoff *= 2  # backoff exponencial
                else:
                    logger.error("Maximo de reintentos alcanzado al conectar a '%s'", self.host)
                    msg = f"No se pudo conectar a {self.host} tras {self.max_retries} intentos"
                    raise ConnectionError(msg) from err

    def disconnect(self):
        """Cierra la conexión."""
        if self.conn:
            logger.info("Desconectado de '%s'", self.host)
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None

    def exists(self, path: str) -> bool:
        """Verifica si existe un archivo o carpeta"""
        self.connect()
        return self.conn.path.exists(path)

    def cwd(self) -> str:
        """Devuelve el directorio actual."""
        self.connect()
        return self.conn.getcwd()

    def download(self, remote: str, local: str | PathLike | IOBase):
        """Descarga un archivo"""
        self.connect()
        try:
            with self.conn.open(remote, mode="r", encoding="utf-8") as remote_file:
                if isinstance(local, (str, PathLike)):
                    with open(fspath(local), "w", encoding="utf-8") as f_local:
                        f_local.write(remote_file.read())
                elif isinstance(local, IOBase):
                    local.write(remote_file.read())
                    local.seek(0)
                else:
                    msg = f"el argumento 'local' debe ser ruta o Buffer, no {type(local)}"
                    raise TypeError(msg)
        except (FTPError, OSError, SocketError) as err:
            logger.error("Error descargando '%s': %s", remote, err)
            raise

    def upload(self, local: str | PathLike | IOBase, remote: str):
        """Sube un archivo"""
        self.connect()
        try:
            with self.conn.open(remote, mode="w", encoding="utf-8") as remote_file:
                if isinstance(local, (str, PathLike)):
                    with open(fspath(local), "r", encoding="utf-8") as f_local:
                        remote_file.write(f_local.read())
                elif isinstance(local, IOBase):
                    local.seek(0)
                    remote_file.write(local.read())
                else:
                    msg = f"el argumento 'local' debe ser ruta o Buffer, no {type(local)}"
                    raise TypeError(msg)
        except (FTPError, OSError, SocketError) as err:
            logger.error("Error subiendo a '%s': %s", remote, err)
            raise

    def _list_files_recursive(self, dir_path: str, pattern: str) -> list[str]:
        resultado = []

        def _recursive_list(current_dir: str):
            try:
                items = self.conn.listdir(current_dir)
            except FTPError:
                return

            for item in items:
                path = f"{current_dir}/{item}"
                try:
                    if self.conn.path.isdir(path):
                        _recursive_list(path)
                    elif self.conn.path.isfile(path):
                        nombre_archivo = path.rsplit('/', 1)[-1]
                        if fnmatch(nombre_archivo, pattern):
                            resultado.append(path)
                except (FTPError, OSError, SocketError):
                    logger.warning("Error accediendo a '%s'", path)

        _recursive_list(dir_path)
        return resultado

    def list_files(self, pattern: str) -> list[str]:
        """Lista files en el servidor, soporta patrones glob simples o recursvos"""
        self.connect()

        if not pattern:
            raise ValueError("Se requiere un patrón de búsqueda no vacío.")

        if pattern.startswith("**/"):
            file_pattern = pattern.removeprefix("**/")
            return self._list_files_recursive("/", file_pattern)

        dir_path, _, file_pattern = pattern.rpartition('/')

        if not dir_path:
            dir_path = "."

        try:
            files = self.conn.listdir(dir_path)
        except FTPError:
            return []

        return [
            f"{dir_path}/{archivo}" if dir_path != "." else archivo
            for archivo in files
            if fnmatch(archivo, file_pattern) and self.conn.path.isfile(f"{dir_path}/{archivo}")
        ]

    def list_files_by_date(self,
                           pattern: str,
                           after_at: datetime = None,
                           before_at: datetime = None) -> list[str]:
        """Lista archivos que coincidan con el patrón y hayan sido modificados de la fecha."""

        self.connect()

        datenow = datetime.now()

        if before_at is None and after_at is None:
            before_at = datenow - timedelta(days=1)
            after_at = datenow

        ts_after = after_at.timestamp() if after_at else None
        ts_before = before_at.timestamp() if before_at else None

        files = self.list_files(pattern)
        resultado = []

        for path in files:
            try:
                if self.conn.path.isfile(path):
                    mod_time = self.conn.path.getmtime(path)

                    if ts_after and mod_time < ts_after:
                        continue
                    if ts_before and mod_time > ts_before:
                        continue

                    resultado.append(path)

            except (FTPError, OSError, SocketError):
                logger.warning("Error accediendo a '%s'", path)

        return resultado

def get_maaji_ftp():
    """Renueva el FTP de Maaji con las credenciales desde el entorno."""
    maaji_ftp = FTP(
        host=Environment.getenv("MAAJI_CONFIG_FTP_DEFAULT_HOST"),
        user=Environment.getenv("MAAJI_CONFIG_FTP_DEFAULT_USERNAME"),
        password=Environment.getenv("MAAJI_CONFIG_FTP_DEFAULT_PASSWORD")
    )
    maaji_ftp_name = Environment.getenv("MAAJI_CONFIG_FTP_DEFAULT_NAME")
    id_maaji_ftp = FTPID(name=maaji_ftp_name, host=maaji_ftp.host)

    if id_maaji_ftp not in DS_FTP:
        DS_FTP[id_maaji_ftp] = maaji_ftp
    else:
        maaji_ftp = DS_FTP[id_maaji_ftp]

    return id_maaji_ftp, maaji_ftp
