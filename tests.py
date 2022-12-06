import os 
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
  def setUp(self):
    self.app_context = app.app_context()
    self.app_context.push()
    db.create_all()
  
  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()
  
  def test_follow(self):
    u1 = User(username='john', email='john@example.com')
    u2 = User(username='susan', email='susan@example.com')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    self.assertEqual(u1.followed.all(), [])
    self.assertEqual(u1.followers.all(), [])

    u1.follow(u2)
    db.session.commit()
    self.assertTrue(u1.is_following(u2))
    self.assertEqual(u1.followed.count(), 1)
    self.assertEqual(u1.followed.first().username, 'susan')
    self.assertEqual(u2.followers.count(), 1)
    self.assertEqual(u2.followers.first().username, 'john')

    u1.unfollow(u2)
    db.session.commit()
    self.assertFalse(u1.is_following(u2))
    self.assertEqual(u1.followed.count(), 0)
    self.assertEqual(u2.followers.count(), 0)
        




if __name__ == '__main__':
    unittest.main(verbosity=2)