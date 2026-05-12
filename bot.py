import os
import json
import base64
from firebase_admin import credentials, firestore

# ─── Firebase ───
b64_creds = os.environ["GOOGLE_CREDENTIALS_B64"]
json_str = base64.b64decode(b64_creds).decode("utf-8")
cred_info = json.loads(json_str)
cred = credentials.Certificate(cred_info)
firebase_admin.initialize_app(cred)
db = firestore.client()
