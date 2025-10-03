from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


# Создание модели данных для пользователя
class User(BaseModel):
    username: str
    user_info: str


fake_db = [{"username": "vasya", "user_info": "любит колбасу"}, {"username": "katya", "user_info": "любит петь"}]

fake_users = {
    1: {"username": "john_doe", "email": "john@example.com"},
    2: {"username": "jane_smith", "email": "jane@example.com"},
    3: {"username": "alice_jones", "email": "alice@example.com"},
    4: {"username": "bob_white", "email": "bob@example.com"},
}


@app.get("/users/")
def read_users(username: str = None, email: str = None, limit: int = 10):
    filtered_users = fake_users

    if username:
        filtered_users = {
            key: user for key, user in filtered_users.items() if username.lower() in user["username"].lower()
        }

    if email:
        filtered_users = {key: user for key, user in filtered_users.items() if email.lower() in user["email"].lower()}

    return dict(list(filtered_users.items())[:limit])


@app.post("/add_user", response_model=User)
async def add_user(user: User):
    fake_db.append(({"username": user.username, "user_info": user.user_info}))
    return user


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id in fake_users:
        return fake_users[user_id]
    return {"error": "not found this user"}


# feedback самостоятельная работа
fake_feedback = {"Kris": "Все было замечательно"}


class Feedback(BaseModel):
    name: str
    message: str


@app.post("/feedback")
async def add_feedback(feedback: Feedback):
    fake_feedback[feedback.name] = feedback.message
    return {"message": f"Feedback received. Thank you, {feedback.name}."}
