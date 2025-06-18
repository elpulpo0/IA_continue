from sqlalchemy.orm import Session
from dotenv import load_dotenv

from modules.api.auth.security import anonymize, hash_password
from config.logger import configure_logger
from modules.api.users.models import User, Role
from modules.database.config import USERS_DATABASE_PATH, INITIAL_USERS_CONFIG_PATH
from modules.database.session import users_engine, UsersSessionLocal, UsersBase
import yaml

# Configuration du logger
logger = configure_logger()

# Charger les variables d'environnement
load_dotenv()


def init_users_db():
    """Vérifie si la base de données existe et crée l'admin si besoin."""
    db_exists = USERS_DATABASE_PATH.exists()

    if not db_exists:
        logger.info("La base de données 'users' n'existe pas. Création en cours...")
        UsersBase.metadata.create_all(bind=users_engine)
        logger.info("Base de données 'users' créée avec succès.")
        create_roles_and_first_users()
    else:
        logger.info(
            "La base de données 'users' existe déjà. Aucun changement nécessaire."
        )


def load_initial_users_config():
    if not INITIAL_USERS_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Fichier de config non trouvé : {INITIAL_USERS_CONFIG_PATH}")
    with open(INITIAL_USERS_CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def create_roles_and_first_users():
    config = load_initial_users_config()
    db: Session = UsersSessionLocal()

    try:
        # Créer les rôles
        for role_name in config.get("roles", []):
            if not db.query(Role).filter_by(role=role_name).first():
                db.add(Role(role=role_name))
        db.commit()

        roles = {role.role: role.id for role in db.query(Role).all()}

        for user_cfg in config.get("users", []):
            role_id = roles.get(user_cfg["role"])
            if not role_id:
                raise ValueError(f"Le rôle '{user_cfg['role']}' n'existe pas")

            if db.query(User).filter_by(email=anonymize(user_cfg["email"])).first():
                continue

            user = User(
                email=anonymize(user_cfg["email"]),
                name=user_cfg["name"],
                password=hash_password(user_cfg["password"]),
                role_id=role_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Utilisateur '{user.name}' créé avec succès.")

    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la création des utilisateurs initiaux : {e}")
    finally:
        db.close()
