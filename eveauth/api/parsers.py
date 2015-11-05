from flask.ext.restful.reqparse import RequestParser

PaginationParser = RequestParser()
PaginationParser.add_argument('page', type=int, default=1)
PaginationParser.add_argument('limit', type=int, default=20)
