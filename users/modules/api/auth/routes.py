from config.logger import configure_logger
from datetime import timedelta, timezone, datetime
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from modules.api.auth.schemas import Token
from modules.api.users.models import User
from modules.api.auth.models import RefreshToken
from modules.database.dependencies import get_users_db
from sqlalchemy.orm import Session
from modules.api.auth.functions import (
    authenticate_user,
    create_token,
    store_refresh_token,
)
import os
from jose import JWTError, jwt
from modules.api.users.functions import get_user_by_email, oauth2_scheme, get_current_user
from modules.api.auth.functions import find_refresh_token
from modules.api.auth.security import anonymize, hash_token
from fastapi.responses import JSONResponse
from uuid import uuid4
from typing import List

load_dotenv()

# Configuration du logger
logger = configure_logger()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

auth_router = APIRouter()


@auth_router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_users_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    app_name = form_data.scopes[0] if form_data.scopes else "default"

    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=7)

    access_token = create_token(
        data={"sub": user.email, "role": user.role.role, "type": "access", "app": app_name},
        expires_delta=access_token_expires,
    )

    refresh_token = create_token(
        data={"sub": user.email, "type": "refresh", "app": app_name},
        expires_delta=refresh_token_expires,
    )

    refresh_expiry = datetime.now(timezone.utc) + refresh_token_expires
    hashed_token = hash_token(refresh_token)
    store_refresh_token(db, user.id, hashed_token, refresh_expiry, app_name=app_name)

    return JSONResponse(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )


@auth_router.post("/refresh", response_model=Token)
def refresh_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_users_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=401, detail="Token invalide pour rafraîchissement"
            )
    except JWTError:
        raise HTTPException(status_code=401, detail="Token non valide")

    hashed_token = hash_token(token)
    refresh_token_db = find_refresh_token(db, hashed_token)

    if not refresh_token_db:
        raise HTTPException(status_code=401, detail="Refresh token introuvable")

    if refresh_token_db.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
        timezone.utc
    ):
        raise HTTPException(status_code=401, detail="Refresh token expiré")

    refresh_token_db.revoked = True

    hashed_email = anonymize(email)
    user = get_user_by_email(hashed_email, db)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    new_access_token = create_token(
        data={"sub": email, "role": role}, expires_delta=timedelta(minutes=15)
    )

    new_refresh_token = create_token(
        data={"sub": email, "role": role, "type": "refresh", "jti": str(uuid4())},
        expires_delta=timedelta(days=7),
    )
    hashed_new_refresh_token = hash_token(new_refresh_token)
    refresh_expiry = datetime.now(timezone.utc) + timedelta(days=7)

    store_refresh_token(
        db, user_id=user.id, token=hashed_new_refresh_token, expires_at=refresh_expiry
    )

    db.commit()

    return JSONResponse(
        {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    )

@auth_router.get("/refresh-tokens", response_model=List[dict])
def list_refresh_tokens(db: Session = Depends(get_users_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit")

    tokens = db.query(RefreshToken).all()
    return [
        {
            "user_id": token.user_id,
            "token": token.token[:10] + "...",  # masqué partiellement
            "created_at": token.created_at,
            "expires_at": token.expires_at,
            "revoked": token.revoked,
            "app": token.app_name
        }
        for token in tokens
    ]