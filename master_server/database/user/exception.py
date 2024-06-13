class UsernameAlreadyTaken(Exception):
    def __init__(self, username: str = ""):
        self.message = f"""
        Username {username} is already taken.
        """


class EmailAlreadyTaken(Exception):
    def __init__(self, email: str = ""):
        self.message = f"""
        Email {email} is already taken.
        """
