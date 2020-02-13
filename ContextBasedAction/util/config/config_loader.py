import configargparse
import argparse
import configparser


default_config_file = 'config.ini'


def print_parser_info():

    print("\n\nValues for ICE Deep learning configuration params"
          "\n==========================================")
    print(parser.format_values())

    if unknowns:
        print('Unused arguments for ICE Deep learning' \
              '\n===============================')
        print(unknowns)
        print('\n')


def load_app_config_file(config_file, prsr):
    config = configparser.RawConfigParser()
    config.read(config_file)

    current_configs = dict()
    for sec in config.sections():
        current_configs.update(config.items(sec))
    for param in current_configs:
        try:
            prsr.add('--%s' % param, env_var='idl_% s' % param)
        except argparse.ArgumentError:
            continue

parser = configargparse.ArgParser(default_config_files=[default_config_file])
parser.add('--config_file', is_config_file=True, help='Config file path', env_var='idl_config_file')
parser.add('--celery_broker', env_var="celery_broker")
parser.add('--celery_backend', env_var="celery_backend")
parser.add('--mongo_db_host', env_var="mongo_db_host")
parser.add('--mongo_db_user', env_var="mongo_db_user")
parser.add('--mongo_db_password', env_var="mongo_db_password")

load_app_config_file(default_config_file, parser)

idl_options, unknowns = parser.parse_known_args()
print_parser_info()




