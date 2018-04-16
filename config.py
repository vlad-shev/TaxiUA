TOKEN = ''
WEBHOOK_HOST = ''
WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = ''  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = '/home/ubuntu/webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = '/home/ubuntu/webhook_pkey.pem'  # Path to the ssl private key
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
WEBHOOK_URL_PATH = f"/TOKEN/"

