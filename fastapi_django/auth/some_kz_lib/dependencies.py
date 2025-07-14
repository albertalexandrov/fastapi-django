from fastapi import Depends
from typing import Annotated

from fastapi_django.auth.some_kz_lib.usr_adm import User, UsrAdmAuth

# TODO: скорее всего именование AdmUsr может сбивать с толку
AdmUsr = Annotated[User, Depends(UsrAdmAuth())]
