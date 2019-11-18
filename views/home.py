from pyramid.view import view_config
from pyramid.response import Response

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Vendor
from simple_settings import settings

from contextlib import contextmanager

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    engine = create_engine(settings.DATABASES['ENGINE'])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

@view_config(route_name='update_alias', renderer='json')
def update_alias(request):

    if request.POST:
        id = request.POST.get('id')
        alias = request.POST.get('alias')
        if id and alias:
            with session_scope() as session:
                vendor = session.query(Vendor).filter_by(id=id).first()
                vendor.alias = alias
                session.commit()

                return { 'success': True }

    return { 'success': False }

@view_config(route_name='home', renderer='../templates/vendors.mako')
def home_page(request):

    vendors = []
    engine = create_engine(settings.DATABASES['ENGINE'])

    Session = sessionmaker(bind=engine)
    session = Session()

    for id, name, site_permit, alias in session.query(Vendor.id, Vendor.name, Vendor.site_permit, Vendor.alias):
        alias = alias if alias else ''
        vendors.append({
            'id': id,
            'name': name,
            'site_permit': site_permit,
            'alias': alias,
        })

    return { 'vendors': vendors }
