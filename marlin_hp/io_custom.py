
import requests



def send_email(email, name, msg):
    pass


def send_new_run(run_id, target, user_uid, location, config):
    url = 'https://vixen.hopto.org/rs/api/v1/data/ident/new'
    post_data = {'run_id': run_id, "target" : target, "user_uid" : user_uid, "status" : 0, "location" : location, "config" : config}
    r = requests.post(url, json = post_data)
    
    
def update_run(run_id, status):
    url = 'https://vixen.hopto.org/rs/api/v1/data/ident/update_run'
    post_data = {'run_id': run_id, "status" : status}
    r = requests.post(url, json = post_data)

