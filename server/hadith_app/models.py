from hadith_app.extensions import bcrypt


class User:
    def __init__(self, id, username, password, roles):
        self.id = id
        self.username = username
        self.password = password
        self.roles = roles

    @staticmethod
    def get_user_by_username(username):
        #TODO This should be replaced with actual database query
        users = {
            'admin': User(1, 'admin', 'admin_password', ['admin']),
            'user': User(2, 'user', 'user_password', ['user'])
        }
        return users.get(username)

    @staticmethod
    def validate_user_credentials(username, password):
        user = User.get_user_by_username(username)
        return user and user.validate_password(password)

    def validate_password(self, password):
        return bcrypt.check_password_hash(bcrypt.generate_password_hash(password), self.password)
