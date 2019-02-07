"""
Iterates through a file of usernames, and, for each:
- get the user's LDAP status
- update ILLiad with the user's status
"""

import datetime, json, logging, os, pprint


LOG_PATH = os.environ['LDP_BRNTP__LOG_PATH']
LOG_LEVEL = os.environ['LDP_BRNTP__LOG_LEVEL']
USER_FILEPATH = os.environ['LDP_BRNTP__USER_FILEPATH']
TRACKER_FILEPATH = os.environ['LDP_BRNTP__TRACKER_FILEPATH']

BUILD_TRACKER = True


level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.info( '\n---\n' + 'starting\n' + '---' )


class Processor( object ):

    def __init__( self ):
        pass

    def manage_process( self ):
        log.debug( 'starting manage_process()' )
        if BUILD_TRACKER is True:
            self.setup_tracker()
        self.process_names()
        1/0

    def setup_tracker( self ):
        """ Prepares tracker.
            Called by manage_process() """
        with open( USER_FILEPATH, 'r', encoding='utf-8' ) as f1:
            names = f1.readlines()
            log.debug( 'names, ```%s```' % pprint.pformat(names) )
        names = [ x.strip() for x in names ]
        tracker_dct = { 'names': {}, 'tracker_timestamp': str( datetime.datetime.now() ) }
        for name in names:
            tracker_dct['names'][name] = { 'processed': None, 'result': None, 'entry_timestamp': None }
        jsn = json.dumps( tracker_dct, sort_keys=True, indent=2 )
        log.debug( 'type(jsn), `%s`' % type(jsn) )
        with open( TRACKER_FILEPATH, 'w', encoding='utf-8' ) as f2:
            f2.write( jsn )
        return

    def process_names( self ):
        print( 'will process_names' )

    ## end class Processor()


if __name__ == '__main__':
    prcssr = Processor()
    prcssr.manage_process()
