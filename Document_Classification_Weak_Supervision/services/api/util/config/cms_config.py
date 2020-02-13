from services.api.util.config import config_access as config


class CMSConfig:
    # [Keys]
    company_extensions = config.get_config('company_extensions')
    party_exclude_keywords = config.get_config('party_exclude_keywords')
    fp_start_keywords = config.get_config('fp_start_keywords')
    sp_start_keywords = config.get_config('sp_start_keywords')
    states = config.get_config('states')
    payment_term_start_patterns = config.get_config('payment_term_start_patterns')
    payment_term_end_patterns = config.get_config('payment_term_end_patterns')
    termination_term_start_patterns = config.get_config('termination_term_start_patterns')
    termination_term_end_patterns = config.get_config('termination_term_end_patterns')
    warranties_term_start_patterns = config.get_config('warranties_term_start_patterns')
    warranties_term_end_patterns = config.get_config('warranties_term_end_patterns')
    indemnification_term_start_patterns = config.get_config('indemnification_term_start_patterns')
    indemnification_term_end_patterns = config.get_config('indemnification_term_end_patterns')

    # [Mongo]
    dbname = config.get_config('dbname')

    def __init__(self):
        pass


cms_config = CMSConfig()



