from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from modules.api.users.schemas import UserResponse
from config.logger import configure_logger
from modules.database.dependencies import get_users_db
from modules.api.users.functions import get_current_user, get_user_by_email
from modules.api.users.schemas import UserResponse, UserCreate, RoleUpdate, UserUpdate
from modules.api.users.models import User, Role
from modules.api.auth.security import anonymize, hash_password

# Configuration du logger
logger = configure_logger()

# Gestion de l'authentification avec OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users_router = APIRouter()


@users_router.get("/users/me", response_model=UserResponse)
def read_users_me(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_users_db)
):
    user = get_user_by_email(current_user.sub, db)

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        role=user.role.role,
    )


@users_router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Récupérer un utilisateur par son ID",
    description="Retourne les informations d'un utilisateur "
    "spécifique en fonction de son ID.",
)
def get_user(user_id: int, db: Session = Depends(get_users_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        role=user.role.role,
    )


@users_router.get("/users", response_model=list[UserResponse])
def get_all_users(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_users_db)
):
    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé : réservé aux administrateurs.",
        )

    # Récupérer tous les utilisateurs de la base de données
    users = db.query(User).all()

    # Retourner les utilisateurs sous forme de liste de UserResponse
    return [
        UserResponse(
            id=u.id,
            name=u.name,
            email=u.email,
            is_active=u.is_active,
            role=u.role.role,
        )
        for u in users
    ]


@users_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_users_db),
):
    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé : réservé aux administrateurs.",
        )

    # Recherche de l'utilisateur à supprimer dans la base de données
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    # Suppression de l'utilisateur
    db.delete(user_to_delete)
    db.commit()

    return JSONResponse({"message": "Utilisateur supprimé"})


@users_router.post(
    "/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user_data: UserCreate, db: Session = Depends(get_users_db)):
    anonymized_email = anonymize(user_data.email)
    existing_user = get_user_by_email(anonymized_email, db)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Un utilisateur avec cet email existe déjà",
        )

    role_obj = db.query(Role).filter_by(role="reader").first()
    if not role_obj:
        raise HTTPException(status_code=500, detail="Le rôle 'reader' est introuvable")

    new_user = User(
        email=anonymized_email,
        name=user_data.name,
        password=hash_password(user_data.password),
        role_id=role_obj.id,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        is_active=new_user.is_active,
        role=new_user.role.role,
    )


@users_router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_update: RoleUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_users_db),
):
    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=403, detail="Accès refusé : réservé aux administrateurs."
        )

    # Recherche de l'utilisateur à modifier dans la base de données
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="Utilisateur à modifier non trouvé."
        )

    # Recherche du nouveau rôle à assigner à l'utilisateur
    new_role = db.query(Role).filter(Role.role == role_update.role).first()
    if not new_role:
        raise HTTPException(status_code=404, detail="Rôle non trouvé.")

    # Mise à jour du rôle de l'utilisateur
    user.role_id = new_role.id
    db.commit()
    db.refresh(user)

    return JSONResponse(
        {"message": f"Rôle de l'utilisateur mis à jour en '{new_role.role}'."}
    )


@users_router.patch("/users/me", response_model=UserResponse)
def update_current_user(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_users_db),
):
    user = get_user_by_email(current_user.sub, db)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if update_data.name:
        user.name = update_data.name

    if update_data.email:
        user.email = anonymize(update_data.email)

    if update_data.password:
        user.password = hash_password(update_data.password)

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        role=user.role.role,
    )

@users_router.patch("/users/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: int,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_users_db),
):
    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=403, detail="Accès refusé : réservé aux administrateurs."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if update_data.name:
        user.name = update_data.name

    if update_data.email:
        user.email = anonymize(update_data.email)

    if update_data.password:
        user.password = hash_password(update_data.password)

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        role=user.role.role,
    )

