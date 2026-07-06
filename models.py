from flask_login import UserMixin

class User(UserMixin):  
  def __init__(self, id, name, surname, username, password, profile_img):
    self.id = id
    self.name = name
    self.surname = surname
    self.username = username
    self.password = password
    self.profile_img = profile_img