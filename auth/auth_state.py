class AuthState:

    def __init__(self):
        self.authenticated = False
        self.student_id = None
        self.password = None

        self.awaiting_student_id = True
        self.awaiting_password = False

    def authenticate(self):
        self.authenticated = True
        self.awaiting_student_id = False
        self.awaiting_password = False

    def reset(self):
        self.authenticated = False
        self.student_id = None
        self.password = None
        self.awaiting_student_id = True
        self.awaiting_password = False

    def is_authenticated(self):
        return self.authenticated


# Global instance
auth_state = AuthState()

def is_authenticated() -> bool:
    return auth_state.authenticated

def get_auth_flag() -> str:
    if auth_state.authenticated:
        return "AUTH_SUCCESS"

    return "AUTH_REQUIRED"