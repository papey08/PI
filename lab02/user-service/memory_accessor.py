from entities import User

class MemoryAccessor:
    def __init__(self):
        self.users_db = {}
        self.current_id = 1

    def create_user(self, 
                    nickname: str,
                    first_name: str,
                    last_name: str, 
                    email: str, 
                    password: str) -> User:
        id = self.current_id
        user = User(
            id=id, 
            nickname=nickname,
            first_name=first_name,
            last_name=last_name,
            email=email, 
            password=password
        )
        self.users_db[user.id] = user
        self.current_id += 1
        return user
    
    def get_user_by_id(self, user_id: int) -> User | None:
        return self.users_db.get(user_id)
    
    def get_users(self, nickname: str, first_name: str, last_name: str, limit: int, offset: int) -> list[User]:
        res = []
        for user in self.users_db.values():
            if ((nickname and user.nickname == nickname) or not nickname) and \
                ((first_name and user.first_name == first_name) or not first_name) and \
                ((last_name and user.last_name == last_name) or not last_name):
                res.append(user)
        return res[offset:offset+limit]
    
    def login(self, email: str, password: str) -> User | None:
        for user in self.users_db.values():
            if user.email == email and user.password == password:
                return user
        return None
