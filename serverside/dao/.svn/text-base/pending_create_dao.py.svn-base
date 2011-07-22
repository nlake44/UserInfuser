'''
Created on May 8, 2011

@author: shan
'''
from serverside.entities.pending_create import Pending_Create

def get_id_by_email(email):
  return Pending_Create.gql("WHERE email = :1", email).get()
