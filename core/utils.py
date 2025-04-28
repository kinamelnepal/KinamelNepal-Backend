
import random
import threading

def generate_4_digit_unique_pass_code(Model):

      while True:
            pass_code = random.randint(1000, 9999) 
            if not Model.objects.filter(pass_code=pass_code).exists():
              return pass_code

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def set_current_user(user):
    _thread_locals.user = user
