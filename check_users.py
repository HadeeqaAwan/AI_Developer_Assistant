from database.database import SessionLocal
from database.models import User

db = SessionLocal()

users = db.query(User).all()

print("Users in database:")

for user in users:
    print(user.id, user.email)

db.close()