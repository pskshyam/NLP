import configargparse
import argparse
import configparser


default_config_file = 'config.ini'


def print_parser_info():

    print("\n\nValues for CMS configuration params"
          "\n==========================================")
    print(parser.format_values())

    if unknowns:
        print('Unused arguments for CMS \n===============================')
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
            prsr.add('--%s' % param, env_var='cms_% s' % param)
        except argparse.ArgumentError:
            continue

parser = configargparse.ArgParser(default_config_files=[default_config_file])
parser.add_argument('--config_file', is_config_file=True, help='Config file path', env_var='cms_config_file')
parser.add_argument('--company_extensions', env_var="cms_company_extensions", nargs='+')
parser.add_argument('--party_exclude_keywords', env_var="cms_party_exclude_keywords", nargs='+')
parser.add_argument('--fp_start_keywords', env_var="cms_fp_start_keywords", nargs='+')
parser.add_argument('--sp_start_keywords', env_var="cms_sp_start_keywords", nargs='+')
parser.add_argument('--states', env_var="cms_states", nargs='+')
parser.add_argument('--dbname', env_var="cms_dbname")
parser.add_argument('--payment_term_start_patterns', env_var="payment_term_start_patterns", nargs='+')
parser.add_argument('--payment_term_end_patterns', env_var="payment_term_end_patterns", nargs='+')
parser.add_argument('--termination_term_start_patterns', env_var="termination_term_start_patterns", nargs='+')
parser.add_argument('--termination_term_end_patterns', env_var="termination_term_end_patterns", nargs='+')
parser.add_argument('--warranties_term_start_patterns', env_var="warranties_term_start_patterns", nargs='+')
parser.add_argument('--warranties_term_end_patterns', env_var="warranties_term_end_patterns", nargs='+')
parser.add_argument('--indemnification_term_start_patterns', env_var="indemnification_term_start_patterns", nargs='+')
parser.add_argument('--indemnification_term_end_patterns', env_var="indemnification_term_end_patterns", nargs='+')

load_app_config_file(default_config_file, parser)

cms_options, unknowns = parser.parse_known_args()
print_parser_info()




