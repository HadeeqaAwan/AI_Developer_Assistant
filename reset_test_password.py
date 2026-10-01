from database.database import SessionLocal
from database.models import User
from auth.security import hash_password

db = SessionLocal()

user = db.query(User).filter(
    User.email == "test2@example.com"
).first()

if user:
    user.password = hash_password("Test12345")
    db.commit()
    print("Password updated successfully.")
else:
    print("User not found.")

db.close()