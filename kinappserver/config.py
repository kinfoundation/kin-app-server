# tester config file. should be overwritten by ansible in prod/stage.

DEPLOYMENT_ENV = 'test'
DEBUG = True
DB_CONNSTR = "this gets overwritten by the tester code. it acutally uses a temp postgress db on the local disc"
REDIS_ENDPOINT = 'localhost'
REDIS_PORT = 6379

STELLAR_TIMEOUT_SEC = 10  # waitloop for tx data to be available
STELLAR_INITIAL_ACCOUNT_BALANCE = 10

ESHU_USERNAME = ''
ESHU_PASSWORD = ''
ESHU_HEARTBEAT = ''
ESHU_APPID = ''
ESHU_VIRTUAL_HOST = ''
ESHU_EXCHANGE = ''
ESHU_QUEUE = ''
ESHU_RABBIT_ADDRESS = ''
PUSH_TTL_SECS = 60 * 60 * 24

STELLAR_HORIZON_URL = 'https://horizon-playground.kininfrastructure.com'
STELLAR_NETWORK = 'Kin Playground Network ; June 2018'
STELLAR_KIN_ISSUER_ADDRESS = 'GBC3SG6NGTSZ2OMH3FFGB7UVRQWILW367U4GSOOF4TFSZONV42UJXUH7'

MAX_SIMULTANEOUS_ORDERS_PER_USER = 2
ORDER_EXPIRATION_SECS = 15

KMS_KEY_AWS_REGION = 'us-east-1'

PHONE_VERIFICATION_REQUIRED = False
PHONE_VERIFICATION_ENABLED = True

P2P_TRANSFERS_ENABLED = True
P2P_MIN_TASKS = 1
P2P_MIN_KIN_AMOUNT = 300
P2P_MAX_KIN_AMOUNT = 12500

TOS_URL = 'http://www.kinitapp.com/terms-and-privacy-policy'
FIREBASE_SERVICE_ACCOUNT_FILE = '/opt/kin-app-server/service-account.json'


AUTH_TOKEN_SEND_INTERVAL_DAYS = 1
AUTH_TOKEN_ENFORCED = False
AUTH_TOKEN_ENABLED = True

#BLACKHAWK
BLACKHAWK_PURCHASES_ENABLED = True
BLACKHAWK_CRITICAL_BALANCE_THRESHOLD = 10

#TRUEX
TRUEX_APP_ID = ''
TRUEX_PARTNER_HASH = ''
TRUEX_CALLBACK_SECRET = ''