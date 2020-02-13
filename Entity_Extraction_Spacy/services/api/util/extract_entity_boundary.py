from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

class Extract_Entity_Boundary(object):

    def __init__(self, filename):
        self.filename = filename

    def extract_entity_boundary(self, text, tag, start):
        ent_label = None
        preceding_text = None
        succeeding_text = None
        try:
            (ent_name, ent_start, ent_end, ent_label) = tag
            preceding_text = text[start:ent_start].lower()
            succeeding_text = text[ent_end:].lower()
            if len(preceding_text.split()) >= 20:
                preceding_text = ' '.join(preceding_text.split()[-20:])
            if len(succeeding_text.split()) >= 15:
                succeeding_text = ' '.join(succeeding_text.split()[:15])
        except Exception as ex:
            logger.error('[{}] Exception raised - {}'.format(self.filename, ex))
        return (ent_label, preceding_text, succeeding_text)