import sys

from flask import Flask
from flask_cors import CORS
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import redis
from kin import SDK

from kinappserver import amqp_publisher


app = Flask(__name__)
CORS(app)

from flask_sqlalchemy import SQLAlchemy
from kinappserver import config, utils

# get the base seed: either directly from config or decrypt using kms
base_seed = config.STELLAR_BASE_SEED
if not base_seed:
    print('decrypting base seed')
    base_seed = utils.decrypt_kms_key(config.STELLAR_BASE_SEED_CIPHER_TEXT_BLOB, config.ENCRYPTED_STELLAR_BASE_SEED, config.KMS_KEY_AWS_REGION)

if not base_seed:
    print('failed to acquire base seed - aborting')
    sys.exit(-1)

# get the channel seeds: either directly from config or decrypt using kms
channel_seeds = config.STELLAR_CHANNEL_SEEDS
if not channel_seeds:
    print('decrypting channel seeds')
    channel_seeds = utils.decrypt_kms_key(config.STELLAR_CHANNEL_SEEDS_CIPHER_TEXT_BLOB, config.ENCRYPTED_STELLAR_CHANNEL_SEEDS, config.KMS_KEY_AWS_REGION)

if not channel_seeds:
    print('failed to acquire channel seeds - aborting')
    sys.exit(-1)

app.kin_sdk = SDK(secret_key=base_seed,
                              horizon_endpoint_uri=config.STELLAR_HORIZON_URL,
                              network=config.STELLAR_NETWORK,
                              channel_secret_keys=channel_seeds)

app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_CONNSTR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
db = SQLAlchemy(app)


# TODO remove this on production
admin = Admin(app, name='KinApp', template_mode='bootstrap3')
from kinappserver.models import User, UserAppData, UserTaskResults, Task, Transaction, Offer, Order, Good
from flask_admin.contrib import sqla

class UserAdmin(sqla.ModelView):
    column_display_pk = True

class UserAppDataAdmin(sqla.ModelView):
    column_display_pk = True

class UserTaskResultsAdmin(sqla.ModelView):
    form_columns = ['user_id', 'task_id']
    column_display_pk = True

class TaskAdmin(sqla.ModelView):
    column_display_pk = True

class OfferAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['offer_id']

class OrderAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['order_id']

class TransactionAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['tx_hash']

class GoodAdmin(sqla.ModelView):
    column_display_pk = True
    form_columns = ['sid']

if config.DEBUG:
    print('enabling admin UI...')
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(UserAppDataAdmin(UserAppData, db.session))
    admin.add_view(UserTaskResultsAdmin(UserTaskResults, db.session))
    admin.add_view(TaskAdmin(Task, db.session))
    admin.add_view(TransactionAdmin(Transaction, db.session))
    admin.add_view(OfferAdmin(Offer, db.session))
    admin.add_view(OrderAdmin(Order, db.session))
    admin.add_view(GoodAdmin(Good, db.session))
else:
    print('NOT enabling admin UI')

import kinappserver.views
import time
import redis_lock
import redis
import sys
from threading import Lock
import requests

app.redis = redis.StrictRedis(host=config.REDIS_ENDPOINT, port=config.REDIS_PORT, db=0)
amqp_publisher.init_config(config.ESHU_RABBIT_ADDRESS, config.ESHU_QUEUE, config.ESHU_EXCHANGE, config.ESHU_VIRTUAL_HOST, config.ESHU_USERNAME, config.ESHU_PASSWORD, config.ESHU_HEARTBEAT, config.ESHU_APPID)
app.amqp_publisher = amqp_publisher

# sanity for configuration
if not config.DEBUG:
    # redis
    app.redis.setex('temp-key', 1, 'temp-value')
