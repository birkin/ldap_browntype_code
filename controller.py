"""
Iterates through a file of usernames, and, for each:
- get the user's LDAP status
- update ILLiad with the user's status
"""

import datetime, json, logging, os, pprint, time


LOG_PATH = os.environ['LDP_BRNTP__LOG_PATH']
LOG_LEVEL = os.environ['LDP_BRNTP__LOG_LEVEL']
USER_FILEPATH = os.environ['LDP_BRNTP__USER_FILEPATH']
TRACKER_FILEPATH = os.environ['LDP_BRNTP__TRACKER_FILEPATH']

BUILD_TRACKER = True
MAX_RECORDS_TO_PROCESS = 2  # for testing; total 2019-07 count 30,410


level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.info( '\n---\n' + 'starting\n' + '---' )


class Processor( object ):

    def __init__( self ):
        self.tracker_dct = None

    def manage_process( self ):
        log.debug( 'starting manage_process()' )
        if BUILD_TRACKER is True:
            self.setup_tracker()
        else:
            log.debug( 'skipping tracker setup' )
        self.process_names()

    def setup_tracker( self ):
        """ Prepares tracker.
            Called by manage_process() """
        with open( USER_FILEPATH, 'r', encoding='utf-8' ) as f1:
            names = f1.readlines()
        names = [ x.lower().strip() for x in names ]
        tracker_dct = { 'names': {}, 'tracker_timestamp': datetime.datetime.now().isoformat() }
        for name in names:
            tracker_dct['names'][name] = { 'ldap_status': None, 'update_result': None, 'update_timestamp': None }
        jsn = json.dumps( tracker_dct, sort_keys=True, indent=2 )
        with open( TRACKER_FILEPATH, 'w', encoding='utf-8' ) as f2:
            f2.write( jsn )
        log.debug( 'tracker created' )
        return

    def process_names( self ):
        """ Loads tracker,
            - finds next-entry to process,
            - calls update-status-api,
            - updates and saves tracker.
            Called by: manage_process() """
        self.tracker_dct = self.load_tracker_dct()
        count = 0
        while count < MAX_RECORDS_TO_PROCESS:
            entry = self.grab_next_entry()
            count += 1
            time.sleep( .5 )
        log.debug( 'process_names still under construction' )
        return

    def load_tracker_dct( self ):
        """ Preps dct from json file if necessary.
            Called by process_names() """
        if self.tracker_dct is None:
            with open( TRACKER_FILEPATH, 'r', encoding='utf-8' ) as f:
                self.tracker_dct = json.loads( f.read() )
            log.debug( 'tracker loaded' )
        else:
            log.debug( 'tracker already loaded' )
        return

    def grab_next_entry( self ):
        """ Grabs the next unprocessed entry.
            TODO: perhaps add an update_timestamp check other than None.
            Called by process_names() """
        entry = 'foo'
        log.debug( 'entry, `%s`' % entry )
        return entry


    ## end class Processor()


if __name__ == '__main__':
    prcssr = Processor()
    prcssr.manage_process()
