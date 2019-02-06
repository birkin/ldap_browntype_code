"""
Iterates through a file of usernames, and, for each:
- get the user's LDAP status
- update ILLiad with the user's status
"""

import logging, os


LOG_PATH = os.environ['LDP_BRNTP__LOG_PATH']
LOG_LEVEL = os.environ['LDP_BRNTP__LOG_LEVEL']
USER_FILEPATH = os.environ['LDP_BRNTP__USER_FILEPATH']
TRACKER_FILEPATH = os.environ['LDP_BRNTP__TRACKER_FILEPATH']

SKIP_TRACKER_BUILD = False




level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.info( '\n---\n' + 'starting\n' + '---\n' )



1/0
