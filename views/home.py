from pyramid.view import view_config
from pyramid.response import Response

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Vendor
from simple_settings import settings

@view_config(route_name='home', renderer='../templates/vendors.mako')
def home_page(request):

    vendors = []
    engine = create_engine(settings.DATABASES['ENGINE'])

    Session = sessionmaker(bind=engine)
    session = Session()

    for id, name, site_permit, alias in session.query(Vendor.id, Vendor.name, Vendor.site_permit, Vendor.alias):
        vendors.append({
            'id': id,
            'name': name,
            'site_permit': site_permit,
            'alias': alias,
        })

    return { 'vendors': vendors }