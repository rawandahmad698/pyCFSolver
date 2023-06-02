import json
import logging
import os
import sys
import uuid

from bottle import run, response, Bottle, request

from bottle_plugins.error_plugin import error_plugin
from bottle_plugins.logger_plugin import logger_plugin
from dtos import IndexResponse, V1RequestBase, V1ResponseBase
import flaresolverr_service
import utils

envi = "dev"


class JSONErrorBottle(Bottle):
    """
    Handle 404 errors
    """
    def default_error_handler(self, res):
        response.content_type = 'application/json'
        return json.dumps(dict(error=res.body, status_code=res.status_code))


app = JSONErrorBottle()

# plugin order is important
app.install(logger_plugin)
app.install(error_plugin)


@app.route('/')
def index():
    """
    Show welcome message
    """
    res = flaresolverr_service.index_endpoint()
    return utils.object_to_dict(res)


@app.route('/health')
def health():
    """
    Healthcheck endpoint.
    This endpoint is special because it doesn't print traces
    """
    res = flaresolverr_service.health_endpoint()
    return utils.object_to_dict(res)

being_processed = []


@app.post('/v1')
def controller_v1():
    """
    Controller v1
    """
    req = V1RequestBase(request.json)
    if envi == "dev":
        try:
            req_url = req.url
            if req_url not in being_processed:
                being_processed.append(req_url)
            else:
                res = V1ResponseBase({})
                res.message = "Already being processed"
                res.status_code = 500
                res.__error_500__ = True
                return utils.object_to_dict(res)
        except Exception as e:
            _ = e
            pass

    res = flaresolverr_service.controller_v1_endpoint(req)
    if res.__error_500__:
        response.status = 500

    if envi == "dev":
        try:
            req_url = req.url
            being_processed.remove(req_url)
        except Exception as e:
            _ = e
            pass

    return utils.object_to_dict(res)


if __name__ == "__main__":
    # validate configuration
    log_level = os.environ.get('LOG_LEVEL', 'info').upper()
    log_html = utils.get_config_log_html()
    headless = utils.get_config_headless()
    server_host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8191)) if envi == "dev" else 8192
    server_port = port

    # configure logger
    logger_format = '%(asctime)s %(levelname)-8s %(message)s'
    if log_level == 'DEBUG':
        logger_format = '%(asctime)s %(levelname)-8s ReqId %(thread)s %(message)s'

    logging.basicConfig(
        format=logger_format,
        level=log_level,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # disable warning traces from urllib3
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
    logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)

    logging.info(f'FlareSolverr {utils.get_flaresolverr_version()}')
    logging.debug('Debug log enabled')

    # test browser installation
    flaresolverr_service.test_browser_installation()

    # start webserver
    # default server 'wsgiref' does not support concurrent requests
    run(app, host=server_host, port=server_port, quiet=True, server='waitress')
