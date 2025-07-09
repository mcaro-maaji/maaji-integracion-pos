"""Modulo de utilidades para crear los scripts de cegid y2 retail."""

from utils.ftp import FTPID, DS_FTP, get_maaji_ftp as _get_maaji_ftp

def get_maaji_ftp(name: str = None, host: str = None):
    """Busca el FTP por defecto configurado para las operaciones de cegid"""

    if not name or not host:
        id_ftp = None
    else:
        id_ftp = FTPID(name=name, host=host)

    if not id_ftp or id_ftp not in DS_FTP:
        _, ftp = _get_maaji_ftp()
        return ftp

    return DS_FTP[id_ftp]
