from entities import User

class MemoryAccessor:
    def __init__(self):
        self.users_db = {}
        self.current_id = 1

    def create_user(self, nickname: str, email: str):
        id = self.current_id
        user = User(id=id, nickname=nickname, email=email)
        self.users_db[user.id] = user
        self.current_id += 1
        return user
    
    def get_user(self, user_id: int):
        return self.users_db.get(user_id)
