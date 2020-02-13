from services.api.util.config import config_access as config


class CMSConfig:
    # [Celery]
    celery_broker = config.get_config('celery_broker')
    celery_backend = config.get_config('celery_backend')

    # [Keys]
    fp_start_keywords = config.get_config('fp_start_keywords')
    sp_start_keywords = config.get_config('sp_start_keywords')
    fp_end_keywords = config.get_config('fp_end_keywords')
    sp_end_keywords = config.get_config('sp_end_keywords')
    date_start_keywords = config.get_config('date_start_keywords')
    date_end_keywords = config.get_config('date_end_keywords')
    sow_keywords = config.get_config('sow_keywords')
    msa_keywords = config.get_config('msa_keywords')
    party_exclude_keywords = config.get_config('party_exclude_keywords')
    contract_keywords = config.get_config('contract_keywords')
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



