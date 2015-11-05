import json
from flask import make_response
from flask.ext.restful import Resource, reqparse, marshal, url_for
from eveauth.models import User, UserSchema
from eveauth.api.parsers import PaginationParser
from eveauth.api.fields import user_fields
from link_header import LinkHeader, Link


def make_link_headers(pagination, endpoint):
    links = [
        Link(url_for(endpoint, page=pagination.page, limit=pagination.per_page), rel='self'),
    ]
    if pagination.pages > 1:
        links.append(Link(url_for(endpoint, page=1, limit=pagination.per_page), rel='first'))
    if pagination.has_prev:
        links.append(Link(url_for(endpoint, page=pagination.prev_num, limit=pagination.per_page), rel='previous'))
    if pagination.has_next:
        links.append(Link(url_for(endpoint, page=pagination.next_num, limit=pagination.per_page), rel='next'))
    if pagination.pages > 1:
        links.append(Link(url_for(endpoint, page=pagination.pages, limit=pagination.per_page), rel='last'))
    return str(LinkHeader(links))


class UsersResource(Resource):
    def get(self):
        args = PaginationParser.parse_args()
        pagination = User.query.order_by(User.created_on.desc()).paginate(args['page'], args['limit'])
        resp = make_response(UserSchema().dumps(pagination.items, many=True).data, 200)
        resp.headers['Link'] = make_link_headers(pagination, 'api.users')
        resp.headers['X-Total-Count'] = pagination.total
        return resp
