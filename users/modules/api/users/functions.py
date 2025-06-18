from modules.api.users.create_db import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from config.logger import configure_logger
from dotenv import load_dotenv
import os
from modules.api.users.schemas import TokenData
from modules.database.dependencies import get_users_db
from pydantic import ValidationError
from jose import JWTError, jwt

# Configuration du logger
logger = configure_logger()

# Charger les variables d'environnement
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Gestion de l'authentification avec OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={
        "me": "Voir ses informations personnelles",
        "admin": "Accès aux opérations administratives",
        "reader": "Accès en lecture aux ressources",
    },
)

def get_user_by_email(email: str, db: Session):
    # Effectuer la recherche dans la base de données avec l'email anonymisé
    user = db.query(User).filter(User.email == email).first()

    return user

def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_users_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        # Décodage du token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)  # Validation Pydantic
        email = token_data.sub
        token_scopes = token_data.scopes

    except JWTError:
        raise credentials_exception
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token payload validation error: {e.errors()}",
        )

    # Vérification des permissions
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    # Recherche de l'utilisateur par email
    user = get_user_by_email(email, db)
    if not user:
        raise credentials_exception

    return token_data