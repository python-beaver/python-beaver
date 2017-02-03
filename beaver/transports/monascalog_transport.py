# -*- coding: utf-8 -*-
import time
import os
import random
import requests
import json
import collections
import logging
import types

from beaver.transports.base_transport import BaseTransport
from beaver.transports.exception import TransportException
from dogpile.cache import make_region
from keystoneclient.auth.identity import v3
from keystoneclient import session
from keystoneclient.v3 import client


MAX_LEN=255

class MonascalogTransport(BaseTransport):

    def __init__(self, beaver_config, logger=None):
        super(MonascalogTransport, self).__init__(beaver_config, logger=logger)

        self._is_valid = False
        self._beaver_config = beaver_config
        self._parse_config_entries(self._beaver_config)
        self._monasca_logger = MonascaLogger(
                                    auth_url = self._keystone_auth_url,
                                    username = self._keystone_user_name,
                                    password = self._keystone_password,
                                    project_name = self._keystone_project_name,
                                    user_domain_name = self._keystone_domain_name,
                                    project_domain_name = self._keystone_domain_name,
                                    log_api_url = self._monasca_log_url,
                                    log_api_hosts = self._monasca_log_hosts,
                                    log_api_protocol = self._monasca_log_protocol,
                                    log_api_uri = self._monasca_log_uri,
                                    enable_batching = self._enable_batching,
                                    token_cache_expiration_secs = self._cache_expiration_secs,
                                    retry_on_failure = True,
                                    max_failure = self._max_retries,
                                    logger = self._logger
                                    )
        self._log_session = None
        self._log_api_url = None
        self._token = None

        self._connect()

    def _parse_config_entries(self, beaver_config):
        self._keystone_auth_url = beaver_config.get('monascalog_auth_url')
        log_hosts = beaver_config.get('monascalog_hosts')
        self._monasca_log_hosts = log_hosts.split(",") if log_hosts else []
        self._monasca_log_url = beaver_config.get('monascalog_url')
        self._monasca_log_protocol = beaver_config.get('monascalog_protocol')
        self._monasca_log_uri = beaver_config.get('monascalog_uri')
        self._keystone_user_name = beaver_config.get('monascalog_user_name')
        self._keystone_password = beaver_config.get('monascalog_password')
        self._keystone_project_name = beaver_config.get('monascalog_project_name')
        self._keystone_domain_name = beaver_config.get('monascalog_domain_name')
        self._max_retries = int(beaver_config.get('monascalog_max_retries'))
        batching = beaver_config.get('monascalog_enable_batching', 'true')
        if batching in ['true','True','yes','Yes','y','Y']:
            self._enable_batching = True
        else:
            self._enable_batching = False
        cache_expire_secs = beaver_config.get('monascalog_cache_expiration_secs')
        if cache_expire_secs:
            self._cache_expiration_secs = int(cache_expire_secs)
        else:
            # use the queue expiration time instead
            self._cache_expiration_secs = int(beaver_config.get('queue_timeout'))

    def _connect(self):
        self._is_valid = self._monasca_logger.check_connection()

    def reconnect(self):
        self._connect()

    def invalidate(self):
        """Invalidates the current transport"""
        super(MonascalogTransport, self).invalidate()
        self._monasca_logger.clear_cache()
        return False

    def _get_global_dimensions(self, filename, kwargs, normalize=True):
        """Returns formatted dimensions that are common for all lines"""
        timestamp = self.get_timestamp(**kwargs)
        dimensions = {
            self._fields.get('type'): kwargs.get('type'),
            '@timestamp': timestamp,
            self._fields.get('host'): self._current_host,
            self._fields.get('file'): filename,
        }

        if self._logstash_version == 0:
            dimensions['@source'] = 'file://{0}'.format(filename)
            dimensions['@fields'] = kwargs.get('fields')
        else:
            dimensions['@version'] = "{0}".format(self._logstash_version)
            fields = kwargs.get('fields')
            for key in fields:
                dimensions[key] = fields[key]

        self._logger.debug("DIMENSIONS = {}".format(dimensions))
        if normalize:
            dimensions = normalize_dimensions(dimensions, self._logger)
        return dimensions

    def callback(self, filename, lines, **kwargs):
        #FIXME: change this from info to debug
        self._logger.info('About to batch {0} lines for file {1}'.\
                          format(len(lines), filename) )
        self._log_format = self._beaver_config.get_field('format', filename)
        global_dimensions = self._get_global_dimensions(filename, kwargs)
        success, code, reason = self._monasca_logger.log_multi(lines, global_dimensions, self._log_format == "rawjson")
        if not success:
            raise TransportException("{}: {}".format(code,reason))
        return True

##########################################################

# Helper function to print requests size details
def print_req_stats(r, *args, **kwargs):
    logger = getattr(print_req_stats, "logger", logging.getLogger("monascalog_transport"))
    logger.debug("status_code: {}, reason: {}, url: {}".format(r.status_code,
                r.reason, r.url))
    if r.ok:
        req_body_len = len(r.request.body)
        req_headers_len = len('\n'.join("{}: {}".format(k,v) for k,v in r.request.headers.iteritems()))
        res_body_len = len(r.content)
        res_headers_len = len('\n'.join("{}: {}".format(k,v) for k,v in r.headers.iteritems()))
        total_size = req_body_len + req_headers_len + res_body_len + res_headers_len
        log_lines_len = getattr(print_req_stats, "lines_length", -1)
        logger.debug("Log size = {} bytes, Request = {} bytes, Response = {} bytes total({}) bytes and it took {} seconds".format(log_lines_len, req_body_len+req_headers_len, res_body_len+res_headers_len, total_size, r.elapsed.total_seconds()))


# Helper method to normalize dictionary and make it suitable to be sent
# as dimensions to log api
def normalize_dimensions(dimensions, logger):
    #First, flatten if there are any dict fields
    normalized_dimensions = flatten(dimensions)

    keys_to_remove = []
    #Next, if there are any list items, flatten
    for key in normalized_dimensions:
        value = normalized_dimensions[key]
        logger.debug("KEY = {} VALUE = {}".format(key,value))
        if isinstance(value, list):
            value = normalized_dimensions[key] = ",".join(value)
        if value and not isinstance(value, types.StringTypes):
            value = normalized_dimensions[key] = str(value)
        if not value:
            # log api doesn't like empty dimensions
            keys_to_remove.append(key)

    for k in keys_to_remove:
        logger.debug("Removing empty dimension entry: {}".format(k))
        del normalized_dimensions[k]
    return normalized_dimensions

# Helper method to flatten a dictionary
def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


"""
MonascaLogRecord abstracts an individual log line string.
It could be instantiated with the line that is read
from a log file or just a string.
If this is a JSON log line read from a file (for example,
Beaver does this), this would still be a string and has
to be converted to JSON. To do this, caller must set
is_json to True.
If this is just a plain text, the is_json field need
not be specified.
Once instantiated, the to_json method would format the
log in a manner suitable to be posted to the Monasca
Log API and returns the JSON payload.
"""
class MonascaLogRecord(object):

    def __init__(self, log_line, is_json=False, logger=None):
        self._log_line = log_line
        self._json_format = is_json
        self._logger = logger

    def is_json(self, validate=False):
        if validate and self._json_format:
            try:
                valid_dict = json.loads(self._log_line)
                return True
            except ValueError as ve:
                return False
        return  self._json_format

    def _validate_length(self, field):
        if len(field) > MAX_LEN:
            return (False, "{} exceeds {} chars!".format(field, MAX_LEN))
        return (True, "")

    def is_valid(self):
        """Check if this object would make a payload
           that confirms to Monasca log api validation
           rules"""
        errors = ["Dimension Validation Errors:"]
        #Get the json payload first
        json_payload = self.to_json(normalize=False)
        #check if the dimensions are valid
        for k,v in json_payload["dimensions"].iteritems():
            # check if value is non-empty
            if not v:
                reason = "Value for key:{} is empty".format(k)
                errors.append(reason)
                continue
            # check if the value is of string type
            if not isinstance(v, types.StringTypes):
                valid = False
                errors.append("Dimension value has to be string type. {} is not!".format(v))
                continue  # as the remaining checks are for a string type
            # check if the key and value lengths are valid
            valid, reason = self._validate_length(k)
            if not valid:
                errors.append(reason)
            valid, reason = self._validate_length(v)
            if not valid:
                errors.append(reason)
        success  = len(errors) == 1
        return success

    def to_json(self, normalize=True):
        output = {"message": self._get_log_message(),
                  "dimensions": self._get_dimensions(normalize)}
        return output


    def _get_dimensions(self, normalize=True):
        if self.is_json(validate=True):
            dims = json.loads(self._log_line)
            dims.pop("message", "")
        else:
            dims = {}

        if normalize:
            dims = normalize_dimensions(dims, self._logger)
        return dims

    def _get_log_message(self):
        if self.is_json(validate=True):
            return json.loads(self._log_line).get("message", "")
        else:
            return self._log_line


"""MonascaLogger implements the core transport details that
   formats, packages and ships logs to Monasca Log API.
   It uses a Keystone helper class to cache tokens used for
   authenticating the log requests"""
class MonascaLogger(object):

    def __init__(self, **kwargs):
        # extract keystone related fields
        self._keystone_auth_url = kwargs.get("auth_url", os.getenv("OS_AUTH_URL", "http://localhost:5000/v3"))
        self._keystone_username = kwargs.get("username", os.getenv("OS_USERNAME"))
        self._keystone_user_domain_name = kwargs.get("user_domain_name", os.getenv("OS_USER_DOMAIN_NAME"))
        self._keystone_project_name = kwargs.get("project_name", os.getenv("OS_PROJECT_NAME"))
        self._keystone_project_domain_name = kwargs.get("project_domain_name", os.getenv("OS_PROJECT_DOMAIN_NAME"))
        self._keystone_password = kwargs.get("password", os.getenv("OS_PASSWORD"))
        self._keystone_token_cache_expiration_secs = kwargs.get("token_cache_expiration_secs", 3600)

        # extract log_api related fields
        self._log_api_hosts = kwargs.get("log_api_hosts", os.getenv("OS_LOG_API_HOSTS"))
        if self._log_api_hosts:
            # get protocol and uri
            self._log_api_protocol = kwargs.get("log_api_protocol", os.getenv("OS_LOG_API_PROTOCOL", "http"))
            self._log_api_uri = kwargs.get("log_api_uri", os.getenv("OS_LOG_API_URI", "v3.0/logs"))

        self._log_api_url = kwargs.get("log_api_url", os.getenv("OS_LOG_API_URL"))

        # extract other fields
        enable_batching = kwargs.get("enable_batching", os.getenv("OS_LOG_API_ENABLE_BATCHING","True").lower())
        self._enable_batching = enable_batching in [True, "true", "yes", "y", "1"]
        retry_on_failure = kwargs.get("retry_on_failure", os.getenv("OS_LOG_API_RETRY_ON_FAILURE", "False").lower())
        self._retry_on_failure = retry_on_failure in ["true", "yes", "y", "1"]
        self._max_failure = int(kwargs.get("max_failure", os.getenv("OS_LOG_API_MAX_FAILURE", 3)))
        self._exp_backoff_secs = float(kwargs.get("exp_backoff_secs", os.getenv("OS_LOG_API_EXP_BACKOFF_SECS", 2)))
        self._logger = kwargs.get("logger", None)
        self._log_session = None
        self._token = None
        # construct a keystone client
        self._keystone = KeystoneClientHelper(self._keystone_auth_url,
                                              self._keystone_username,
                                              self._keystone_password,
                                              self._keystone_project_name,
                                              self._keystone_user_domain_name,
                                              self._keystone_project_domain_name,
                                              self._logger,
                                              self._keystone_token_cache_expiration_secs)

    def _get_token_and_log_server_url(self):
        # get from keystone
        token, log_url =  self._keystone.get_token_and_log_url()
        if self._log_api_hosts:
            # get a random server from the list
            self._log_api_url = "{0}://{1}/{2}".format(self._log_api_protocol,
                                             random.choice(self._log_api_hosts),
                                             self._log_api_uri
                                            )
        elif not self._log_api_url:
            self._log_api_url = log_url

        self._token = token

    def check_connection(self):
        failure = 1
        print_req_stats.logger = self._logger
        while True:
            if not self._log_session:
                self._log_session = requests.Session()
            try:
                self._get_token_and_log_server_url()
                self._logger.info('connect: {0}'.format(self._log_api_url))
                self._log_session.get(self._log_api_url, headers={"X-Auth-Token": self._token},
                                      verify=False,
                                      hooks=dict(response=print_req_stats))
            except Exception, e:
                self._logger.error(
                    'Exception caught validating url connection: ' + str(e))
                if failure < self._max_failure:
                    failure += 1
                    time.sleep(self._exp_backoff_secs ** failure)
                    self._logger.debug(
                        'Retrying connection, attempt {0}'.format(failure))
                    continue
                self._logger.error("Failed to connect")
                return False
            else:
                self._logger.info('Connection validated')
                return True

    def clear_cache(self):
        self._keystone.invalidate_cache()

    def  _build_request_headers(self):
         headers = {}
         headers["X-Auth-Token"] = self._token
         headers["Content-Type"] = "application/json"
         return headers

    def _build_request_payload(self, lines, global_dimensions, is_json=False):
        log_payload = {"dimensions": global_dimensions,
                   "logs": []}
        for line in lines:
            record = MonascaLogRecord(line, is_json, logger=self._logger)
            log_payload["logs"].append(record.to_json())
        return log_payload

    def _post_logs(self, lines, global_dimensions, is_json=False):
        if not isinstance(lines, list):
            lines = [lines]
        payload = self._build_request_payload(lines, global_dimensions, is_json)
        headers = self._build_request_headers()
        self._logger.debug('About to post log to url %s' % (self._log_api_url))
        self._logger.debug("Headers: {}".format(headers))
        self._logger.debug("Payload: {}".format(payload))
        message = ""

        lines_length = 0
        for l in lines:
            lines_length += len(l)
        print_req_stats.lines_length = lines_length
        print_req_stats.logger = self._logger
        failure = 1
        result = None
        while True:
            try:
                result = self._log_session.post(url=self._log_api_url,
                                                json=payload,
                                                headers=headers,
                                                verify=False,
                                                hooks=dict(response=print_req_stats))
                if result.status_code in range(200, 300):
                    self._logger.debug('success posting log')
                    # success
                    return (True, result.status_code, result.reason)
                elif result.status_code in [400, 422]:
                    # Bad format error, no point in retrying
                    # Log the error and move on
                    message = "The server rejected the payload: {0}".\
                              format(payload)
                    self._logger.error(message)
                    return (True, result.status_code, result.reason)
                elif result.status_code in [401,403]:
                    message = "Invalid token. Will invalidate cache and retry."\
                              " status code = %d" % result.status_code
                else:
                    message = 'Post returned non 2xx http status: {0}/{1}'.\
                              format(result.status_code, result.reason)
            except Exception, e:
                message = e.message

            self._logger.debug(message)
            if failure < self._max_failure:
                failure += 1
                time.sleep(self._exp_backoff_secs ** failure)
                self._logger.debug(
                    'Retrying connection, attempt {0}'.format(failure))
                continue
            status_code = result.status_code if result else None
            reason = result.reason if result else None
            return_value = (False, status_code, reason)
            break

        return return_value

    # Log a single line
    def log(self, line, global_dimensions, is_json=False):
        return self._post_logs(line, global_dimensions, is_json)

    # Log multiple lines
    def log_multi(self, lines, global_dimensions, is_json=False):
        result = (True, 200, 'OK')
        if self._enable_batching:
            result = self._post_logs(lines, global_dimensions, is_json)
        else:
            for line in lines:
                result = self._post_logs(line, global_dimensions, is_json)
                if not result[0]:
                    break
        return result


# Helper class to get keystone token and logging url from the service catalog
class KeystoneClientHelper(object):

    def __init__(self, auth_url, user_name, password, project_name, user_domain_name,
                 project_domain_name, logger, cache_expiration_seconds):
        self._auth_url = auth_url
        self._user_name = user_name
        self._password = password
        self._project_name = project_name
        self._user_domain_name = user_domain_name
        self._project_domain_name = project_domain_name
        self._logger = logger

        # set an in-memory dogpile cache that would cache token response for
        # a configurable period of time
        if cache_expiration_seconds > 0:
            self._cache = make_region().configure("dogpile.cache.memory",
                          expiration_time=cache_expiration_seconds)
        else:
            self._cache = None

    def _get_logging_url_from_catalog(self, auth):
        for catalog in auth.auth_ref['catalog']:
            if catalog['type'] != 'logging':
                continue
            for ept in catalog['endpoints']:
                if ept['interface'] == 'public':
                    return ept['url']
        return None

    def _get_cache_entries(self):
        token = None
        log_url = None
        if self._cache:
            token = self._cache.get("token")
            log_url = self._cache.get("log_url")
        return token, log_url


    def _cache_entries(self, token, log_url):
        if not self._cache:
            return
        # cache the token and url
        self._cache.set("token", token)
        self._cache.set("log_url", log_url)


    def get_token_and_log_url(self):
        token, log_url = self._get_cache_entries()
        if not token:
            self._logger.debug("going to call inner get_cached_token")
            token, log_url = self._get_token(
                self._auth_url, self._user_name, self._password,
                self._project_name, self._user_domain_name,
                self._project_domain_name)
            # cache the token and url, if caching is enabled
            self._cache_entries(token, log_url)

        return token, log_url

    def _get_token(self, auth_url, user_name, password, project_name,
                   user_domain_name, project_domain_name):
        logging_url = None
        try:
            auth = v3.Password(auth_url=auth_url, username=user_name,
                               password=password, project_name=project_name,
                               user_domain_name=user_domain_name,
                               project_domain_name=project_domain_name)
            sess = session.Session(auth=auth, verify=False)
            keystone = client.Client(session=sess)
            token = keystone.session.get_token()
            logging_url = self._get_logging_url_from_catalog(auth)
        except Exception, e:
            self._logger.error("Unable to get token from Keystone: {0}".format(e.message))
            raise TransportException(e.message)

        return token, logging_url

    def invalidate_cache(self):
        if self._cache:
            self._cache.invalidate("token")
            self._cache.invalidate("log_url")


def main():
    #logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("test")

    # Note: The constructor would use environment variables if not all params
    #       are explicitly passed
    mlogger = MonascaLogger(logger=logger, retry_on_failure=True,
                            max_failure=2)
    mlogger.check_connection()
    line = '{"a":{"b":10}, "m":"tessssssss"}'
    lines= ['{"message":"Once upon a time..the end", "type": "nova"}',
            line
           ]

    rec = MonascaLogRecord(line, is_json=True, logger=logger)
    # is_valid call below should return False, as the dict value is not
    # a valid dimension
    print "Is Valid = {}".format(rec.is_valid())
    result = mlogger.log(line, {"filename": "xyz.log"}, is_json=True)
    # however, it should log fine, as MonascaLogger should normalize and
    # flatten it
    print result
    result = mlogger.log_multi(lines, {"filename": "xyz.log"}, is_json=True)
    print result


if __name__ == "__main__":
    main()
