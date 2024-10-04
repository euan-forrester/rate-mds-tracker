import configparser
import boto3
from botocore.exceptions import ClientError
import logging
import os
import json

class ConfigHelper:
    
    @staticmethod
    def get_config_helper(default_env_name, application_name):
        if not "ENVIRONMENT" in os.environ:
            logging.info("Did not find ENVIRONMENT environment variable, running in development mode and loading config from config files.")

            return ConfigHelperFile(environment=default_env_name, filename_list=["config/config.ini", "config/secrets.ini"])

        else:
            ENVIRONMENT = os.environ.get('ENVIRONMENT')

            logging.info(f"Found ENVIRONMENT environment variable containing '{ENVIRONMENT}': assuming we're running in AWS and getting our parameters from the AWS Parameter Store")

            return ConfigHelperParameterStore(environment=ENVIRONMENT, application_name=application_name)

    @staticmethod
    def _log(param, value, is_secret, cache_type="none"):
        logging.info(f"Got parameter {param} with value {ConfigHelper._get_value_log_string(value, is_secret)}")

    @staticmethod
    def _log_set(param, value, is_secret, cache_type="none"):
        logging.info(f"Set parameter {param} with value {ConfigHelper._get_value_log_string(value, is_secret)}")

    @staticmethod
    def _get_value_log_string(value, is_secret):
        if is_secret:
            return "<secret>"
        else:
            return f"{value}" 

class ConfigHelperFile(ConfigHelper):
    
    '''
    Uses the ConfigParser library to read config items from a set of local files
    '''

    def __init__(self, environment, filename_list):
        self.environment    = environment
        self.config         = configparser.ConfigParser(interpolation=None) # We may need % signs in our encryption key, and don't want people to have to worry about escaping them

        for filename in filename_list:
            logging.info(f"Reading in config file '{filename}'")
            self.config.read(filename)

    def get_environment(self):
        return self.environment

    def set(self, key, value, is_secret=False):
        try:
            # This doesn't update the actual .ini file -- it must just update the in-memory store of our config.
            # It might be better to just do nothing here? Not sure
            self.config.set(self.environment, key, value)
            ConfigHelper._log_set(key, value, is_secret)

        except configparser.NoOptionError as e:
            raise ParameterNotFoundException(message=f'Could not set parameter {key}') from e        

    def get(self, key, is_secret=False):
        try:
            value = self.config.get(self.environment, key)
            ConfigHelper._log(key, value, is_secret)
            return value

        except configparser.NoOptionError as e:
            raise ParameterNotFoundException(message=f'Could not get parameter {key}') from e

    # This will throw a ValueError if the parameter doesn't contain an int
    def getInt(self, key, is_secret=False):
        try:
            value = self.config.getint(self.environment, key)
            ConfigHelper._log(key, value, is_secret)
            return value

        except configparser.NoOptionError as e:
            raise ParameterNotFoundException(message=f'Could not get parameter {key}') from e

    # This will throw a ValueError if the parameter doesn't contain an boolean
    def getBool(self, key, is_secret=False):
        try:
            value = self.config.getboolean(self.environment, key)
            ConfigHelper._log(key, value, is_secret)
            return value

        except configparser.NoOptionError as e:
            raise ParameterNotFoundException(message=f'Could not get parameter {key}') from e

    # This will throw a ValueError if the parameter doesn't contain a float
    def getFloat(self, key, is_secret=False):
        try:
            value = self.config.getfloat(self.environment, key)
            ConfigHelper._log(key, value, is_secret)
            return value

        except configparser.NoOptionError as e:
            raise ParameterNotFoundException(message=f'Could not get parameter {key}') from e

    # This will throw a ValueError if the parameter doesn't contain a JSON-formatted array
    def getArray(self, key, is_secret=False):
        try:
            value = json.loads(self.config.get(self.environment, key))
            ConfigHelper._log(key, value, is_secret)
            return value

        except configparser.NoOptionError as e:
            raise ParameterNotFoundException(message=f'Could not get parameter {key}') from e

class ConfigHelperParameterStore(ConfigHelper):

    '''
    Reads config items from the AWS Parameter Store
    '''

    def __init__(self, environment, application_name):
        self.environment      = environment
        self.application_name = application_name
        self.ssm              = boto3.client('ssm') # Region is read from the AWS_DEFAULT_REGION env var

    def get_environment(self):
        return self.environment

    def get(self, key, is_secret=False):

        full_path = self._get_full_path(key)

        value = self._get_from_parameter_store(full_path, is_secret)

        ConfigHelper._log(key, value, is_secret)

        return value

    def set(self, key, value, is_secret=False):

        full_path = self._get_full_path(key)

        self._set_in_parameter_store(full_path, value, is_secret)

        ConfigHelper._log_set(key, value, is_secret)

        return value

    def _get_from_parameter_store(self, full_path, is_secret=False):
        
        try:
            return self.ssm.get_parameter(Name=full_path, WithDecryption=is_secret)['Parameter']['Value']

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == "ParameterNotFound":
                raise ParameterNotFoundException(message=f'Could not get parameter {full_path}: {error_code}') from e
            else:
                # Something else bad happened; better just let it through
                raise

    def _set_in_parameter_store(self, full_path, value, is_secret=False):
        
        try:
            return self.ssm.put_parameter(Name=full_path, Value=value, Overwrite=True)

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == "ParameterNotFound":
                raise ParameterNotFoundException(message=f'Could not set parameter {full_path}: {error_code}') from e
            else:
                # Something else bad happened; better just let it through
                raise

    def _get_full_path(self, key):
        return f'/{self.application_name}/{self.environment}/{key}'

    # This will throw a ValueError if the parameter doesn't contain an int
    def getInt(self, key, is_secret=False):
        return int(self.get(key, is_secret))

    # This will throw a ValueError if the parameter doesn't contain an boolean
    # Recognizes the same strings as ConfigParser above: https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.getboolean
    def getBool(self, key, is_secret=False):
        value = self.get(key, is_secret)
        if value.lower() in ["true", "on", "yes", "1"]:
            return True

        if value.lower() in ["false", "off", "no", "0"]:
            return False

        raise configparser.ValueError(message=f'Could not get boolean value from {value}')

    # This will throw a ValueError if the parameter doesn't contain an int
    def getFloat(self, key, is_secret=False):
        return float(self.get(key, is_secret))

    # This will throw a ValueError if the parameter doesn't contain a JSON-formatted array
    def getArray(self, key, is_secret=False):
        return json.loads(self.get(key, is_secret))

class ParameterNotFoundException(Exception):

    '''
    Raised when a particular parameter cannot be found
    '''

    def __init__(self, message):
        logging.warn(message) # The actual parameter value isn't logged in the stack trace, so if we want to see it we need to log it here
