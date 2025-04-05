import requests
from django.conf import settings
import random
import string
import uuid
from kariotar_auth.models import UserMaster

backblaze_cred = settings.BACKBLAZE_CREAD

key_id = backblaze_cred.get("key_id")
app_key = backblaze_cred.get("app_key")
bucket_id = backblaze_cred.get("bucket_id")
bucket_name = backblaze_cred.get("bucket_name")



def b2_authorize(key_id, app_key):
    auth_url = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"
    auth_res = requests.get(auth_url, auth=(key_id, app_key))
    
    if auth_res.status_code != 200:
        raise Exception(f"Auth failed: {auth_res.text}")
    return auth_res.json()


def b2_upload_file(file_path, file_name):
    key_id = backblaze_cred.get("key_id")
    app_key = backblaze_cred.get("app_key")
    bucket_id = backblaze_cred.get("bucket_id")
    bucket_name = backblaze_cred.get("bucket_name")
    auth_data = b2_authorize(key_id, app_key)
    api_url = auth_data['apiUrl']
    auth_token = auth_data['authorizationToken']
    
    headers = {"Authorization": auth_token}
    
    # Step 2: Get Upload URL
    upload_url_endpoint = f"{api_url}/b2api/v2/b2_get_upload_url"
    payload = {"bucketId": bucket_id}
    upload_url_res = requests.post(upload_url_endpoint, headers=headers, json=payload)
    
    if upload_url_res.status_code != 200:
        raise Exception(f"Failed to get upload URL: {upload_url_res.text}")
    
    upload_data = upload_url_res.json()
    upload_url = upload_data['uploadUrl']
    upload_auth_token = upload_data['authorizationToken']
    
    file_data = file_path.read()
    
    file_headers = {
        "Authorization": upload_auth_token,
        "X-Bz-File-Name": file_name,
        "Content-Type": "b2/x-auto",
        "X-Bz-Content-Sha1": "do_not_verify"
    }
    
    upload_res = requests.post(upload_url, headers=file_headers, data=file_data)
    if upload_res.status_code != 200:
        raise Exception(f"File upload failed: {upload_res.text}")
    
    return file_name

def b2_get_signed_url(key_id, app_key, bucket_id, file_name, bucket_name, expiry=600):
    auth_data = b2_authorize(key_id, app_key)
    api_url = auth_data['apiUrl']
    auth_token = auth_data['authorizationToken']
    
    headers = {"Authorization": auth_token}  
    
    download_auth_url = f"{api_url}/b2api/v2/b2_get_download_authorization"
    payload = {
        "bucketId": bucket_id,
        "fileNamePrefix": file_name,
        "validDurationInSeconds": expiry
    }
    download_auth_res = requests.post(download_auth_url, headers=headers, json=payload)
    
    if download_auth_res.status_code != 200:
        raise Exception(f"Failed to get download authorization: {download_auth_res.text}")
    
    download_token = download_auth_res.json()["authorizationToken"]
    download_url = f"{auth_data['downloadUrl']}/file/{bucket_name}/{file_name}?Authorization={download_token}"
    
    return download_url



def generate_username(first_name: str, user_type: str) -> str:
    first_name = "".join(first_name.split())
    while True:
        unique_part = uuid.uuid4().hex[:6]
        username = (
            f"{user_type}{random.randint(10, 99)}"
            f"{random.choice(string.ascii_uppercase)}{random.randint(100, 990)}"
            f"{random.choice(string.ascii_uppercase)}{first_name[-2:].upper()}{unique_part.upper()}"
        )
        username = "".join(username.split())
        if not UserMaster.objects.filter(unique_username=username).exists():
            return username