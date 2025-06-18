from modules.database.session import UsersSessionLocal

def get_users_db():
    db = UsersSessionLocal()
    try:
        yield db
    finally:
        db.close()