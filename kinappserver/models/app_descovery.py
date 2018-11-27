from flask import jsonify

from kinappserver import db
from kinappserver.utils import test_image, InvalidUsage
import logging as log
import json


class AppDiscovery(db.Model):
    """ the app discovery class represents a single Discoverable App """
    app_identifier = db.Column(db.String(40), nullable=False, primary_key=True)
    title = db.Column(db.String(80), nullable=False, primary_key=False)
    subtitle = db.Column(db.String(40), nullable=False, primary_key=False)
    app_category_id = db.Column(db.Integer(), nullable=False, primary_key=False)
    is_active = db.Column(db.Boolean, unique=False, default=False)
    os_type = db.Column(db.String(20), primary_key=False, nullable=False)
    meta_data = db.Column(db.JSON, primary_key=False, nullable=False)
    move_kin_data = db.Column(db.JSON, primary_key=False, nullable=True)

    def __repr__(self):
        return '<app_identifier: %s, title: %s, app_category_id: %d, meta_data: %s, move_kin_data: %s>' % (
            self.app_identifier, self.title, self.app_category_id, self.meta_data, self.move_kin_data)


class AppDiscoveryCategory(db.Model):
    """ the app discovery category represents a single App Category """
    category_id = db.Column(db.Integer(), nullable=False, primary_key=True)
    title = db.Column(db.String(80), nullable=False, primary_key=False)


def app_discovery_category_to_json(app_discovery_category):
    """converts app_discovery_category to a json-representation"""
    if not app_discovery_category:
        return {}

    # Build json
    json_app_discovery_category = {'category_id': app_discovery_category.category_id,
                                   'title': app_discovery_category.title}

    return json_app_discovery_category


def app_discovery_to_json(app_discovery):
    """converts app_discovery to a json-representation"""
    if not app_discovery:
        return {}

    # Build json
    json_app_discovery = {'app_identifier': app_discovery.app_identifier, 'title': app_discovery.title,
                          'app_category_id': app_discovery.app_category_id, 'is_active': app_discovery.is_active,
                          'os_type': app_discovery.os_type, 'meta_data': app_discovery.meta_data}
    if app_discovery.move_kin_data:
        json_app_discovery['move_kin_data'] = app_discovery.move_kin_data

    return json_app_discovery


def add_discovery_app(discovery_app_json, set_active=False):
    """ add discovery app to the db """

    if discovery_app_json['meta_data']:
        meta_data = discovery_app_json['meta_data']
    else:
        log.error('cant add discovery app to db with id %s' % discovery_app_json['app_identifier'])
        return False

    skip_image_test = discovery_app_json.get('skip_image_test', False)

    if not skip_image_test:
        print('testing accessibility of discovery apps urls (this can take a few seconds...)')
        # ensure all urls are accessible:
        fail_flag = False

        image_url, card_image_url, icon_url = meta_data['image_url'], meta_data['card_image_url'], meta_data['icon_url']

        if not test_image(image_url):
            log.error('discovery app image_url - %s - could not be verified' % image_url)
            fail_flag = True
        if not test_image(card_image_url):
            log.error('discovery app card_image_url - %s - could not be verified' % card_image_url)
            fail_flag = True
        if not test_image(icon_url):
            log.error('discovery app icon_url - %s - could not be verified' % icon_url)
            fail_flag = True

        if fail_flag:
            log.error('could not ensure accessibility of all urls. refusing to add discovery app')
            return False

        log.info('done testing accessibility of discovery app urls')

    try:
        discovery_app = AppDiscovery()
        discovery_app.app_identifier = discovery_app_json['app_identifier']
        discovery_app.title = discovery_app_json['title']
        discovery_app.subtitle = discovery_app_json['subtitle']
        discovery_app.app_category_id = int(discovery_app_json['app_category_id'])
        discovery_app.os_type = discovery_app_json['os_type']
        discovery_app.meta_data = discovery_app_json['meta_data']
        discovery_app.move_kin_data = discovery_app_json.get('move_kin_data', None)  # Optional

        db.session.add(discovery_app)
        db.session.commit()
    except Exception as e:
        print(e)
        log.error('cant add discovery app to db with id %s' % discovery_app_json['app_identifier'])
        return False
    else:
        if set_active:
            set_discovery_app_active(discovery_app_json['app_identifier'], True)
        return True


def add_discovery_app_category(app_category_json):
    """ add a discovery app category to the db"""
    try:
        discovery_app_category = AppDiscoveryCategory()
        discovery_app_category.category_id = int(app_category_json['category_id'])
        discovery_app_category.title = app_category_json['title']

        db.session.add(discovery_app_category)
        db.session.commit()
    except Exception as e:
        print(e)
        log.error('cant add discovery app to db with id %s' % app_category_json['category_id'])
        return False
    else:
        return True


def set_discovery_app_active(app_identifier, is_active):
    """ show/hide discovery app"""
    app = AppDiscovery.query.filter_by(app_identifier=app_identifier).first()
    if not app:
        raise InvalidUsage('no such discovery app_identifier')

    app.is_active = is_active
    db.session.add(app)
    db.session.commit()
    return True


def get_discovery_apps(os_type):
    """ get discovery apps from the db, filter by platform """
    apps = AppDiscovery.query.filter(AppDiscovery.os_type.contains(os_type)).all() # android, iOS or both
    categories = AppDiscoveryCategory.query.all()

    json_array = []
    # convert to json
    for cat in categories:
        json_array.append(app_discovery_category_to_json(cat))
        json_array[cat.category_id]['apps'] = []
        for app in apps:
            if app.app_category_id == cat.category_id and app.is_active:
                json_array[cat.category_id]['apps'].append(app_discovery_to_json(app))

    return json_array
