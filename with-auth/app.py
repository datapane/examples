import datapane as dp
import random
import string

def get_key():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10)) 

def password_protect(app, correct_pw, password, ref):

    if correct_pw == password:
        return app
    else:
        return dp.Group(
            dp.Text("Not OK"),
            withAuth(app, correct_pw),
            name=ref,
        )
    
def withAuth(app, correct_pw, ref = None):

    ref = ref or get_key()

    controls = dp.TextBox("password", "Enter your password")

    return dp.Interactive(
        lambda params: password_protect(app, correct_pw, params['password'], ref), 
        controls=dp.Controls(controls),
        target=ref,
        swap=dp.Swap.REPLACE,
        name=ref
    )
    
