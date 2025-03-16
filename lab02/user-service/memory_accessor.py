from datetime import datetime, timezone

from entities import User
import exceptions

class MemoryAccessor:
    def __init__(self):
        self.users_db = {}
        self.logins = set()
        self.emails = set()
        self.current_id = 1

    def create_user(self, 
                    login: str,
                    first_name: str,
                    last_name: str, 
                    email: str, 
                    password: str) -> User:
        if login in self.logins or email in self.emails:
            raise exceptions.UserAlreadyExistsException(login, email)
        id = self.current_id
        user = User(
            id=id, 
            login=login,
            first_name=first_name,
            last_name=last_name,
            email=email, 
            password=password,
            is_admin=False,
            created_at=datetime.now(timezone.utc)
        )
        self.users_db[user.id] = user
        self.current_id += 1
        self.logins.add(login)
        self.emails.add(email)
        return user
    
    def get_user_by_id(self, user_id: int, actor_id: int) -> User:
        user = self.users_db.get(user_id)
        if user:
            return user
        raise exceptions.UserNotFoundException(user_id)
    
    def get_users(self, login: str, first_name: str, last_name: str, limit: int, offset: int, actor_id: int) -> list[User]:
        res = []
        for user in self.users_db.values():
            if ((login != '' and user.login == login) or login == '') and \
                ((first_name != '' and first_name.lower() in user.first_name.lower()) or first_name == '') and \
                ((last_name != '' and last_name.lower() in user.last_name.lower()) or last_name == ''):
                res.append(user)
        return res[offset:offset+limit]
    
    def login(self, login: str, password: str) -> User:
        for user in self.users_db.values():
            if user.login == login and user.password == password:
                return user
        raise exceptions.LoginUnableException()
