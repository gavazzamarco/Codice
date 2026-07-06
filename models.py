from flask_login import UserMixin

class User(UserMixin):     
  def __init__(self, id, name, surname, username, password, role, profile_img):     
    self.id = id     
    self.name = name     
    self.surname = surname     
    self.username = username     
    self.password = password
    self.role = role 
    self.profile_img = profile_img