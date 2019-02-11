"""
Iterates through a file of usernames, and, for each:
- get the user's LDAP status
- update ILLiad with the user's status
"""

import datetime, json, logging, os, pprint, subprocess, time


LOG_PATH = os.environ['LDP_BRNTP__LOG_PATH']
LOG_LEVEL = os.environ['LDP_BRNTP__LOG_LEVEL']
USER_FILEPATH = os.environ['LDP_BRNTP__USERNAMES_FILEPATH']
TRACKER_FILEPATH = os.environ['LDP_BRNTP__TRACKER_FILEPATH']
LDAP_SCRIPT_PATH = os.environ['LDP_BRNTP__LDAP_SCRIPT_PATH']

BUILD_TRACKER = False
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
        return

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
        self.load_tracker_dct()
        count = 0
        while count < MAX_RECORDS_TO_PROCESS:
            entry_dct = self.grab_next_entry()
            ldap_status = self.grab_ldap_status( list(entry_dct.keys())[0] )
            processed_entry_dct = self.run_update( entry_dct, ldap_status )  # hits illiad-api if necessary
            self.write_tracker_update( processed_entry_dct )
            count += 1
            time.sleep( .5 )
        log.debug( 'process_names still under construction' )
        return

    def load_tracker_dct( self ):
        """ Preps dct from json file if necessary.
            Called by process_names() """
        # log.debug( 'dct, ```%s```' % self.tracker_dct )
        if self.tracker_dct is None:
            with open( TRACKER_FILEPATH, 'r', encoding='utf-8' ) as f:
                self.tracker_dct = json.loads( f.read() )
            log.debug( 'tracker loaded' )
        else:
            log.debug( 'tracker already loaded' )
        return

    def grab_next_entry( self ):
        """ Grabs the next unprocessed entry.
            Example return: ```{ 'the_username': {'ldap_status': None, 'update_result': None, 'update_timestamp': None} }```
            TODO: perhaps add an update_timestamp check other than None.
            Called by process_names() """
        entry_to_check_next = None
        names = list( self.tracker_dct['names'].keys() )
        for name in names:
            entry_to_check_next = { name: self.tracker_dct['names'][name] }
            if entry_to_check_next[name]['update_timestamp'] is None:
                break
        log.debug( 'entry_to_check_next, `%s`' % entry_to_check_next )
        return entry_to_check_next

    def grab_ldap_status( self, username ):
        """ Assigns current ldap status to name-dct.
            Called by process_names() """
        command = 'php %s -u %s' % ( LDAP_SCRIPT_PATH, username )
        log.debug( 'command, `%s`' % command )
        ldap_response = self.check_ldap( command )
        status = self.process_ldap_response( ldap_response, username )
        return status

    def check_ldap( self, command ):
        """ Hits ldap script.
            Called by grab_ldap_status() """
        ldap_response = 'init'
        try:
            ldap_response = subprocess.check_output( [command, '-1'], stderr=subprocess.STDOUT, shell=True )
        except subprocess.CalledProcessError as e:
            log.error( 'subprocess exception e, ```%s```' % repr(e) )
            log.error( 'e.output, `%s`' % e.output )
        except Exception as f:
            log.error( 'other exception f, ```%s```' % repr(f) )
        log.debug( 'type(ldap_response), `%s`; ldap_response, ```%s```' % (type(ldap_response), ldap_response) )
        return ldap_response

    def process_ldap_response( self, ldap_response, username ):
        """ Grabs status.
            Called by grab_ldap_status() """
        if ldap_response == 'init':
            status = 'problem, response still `init`; see logs for username, `%s`' % username
        else:
            try:
                ldap_jdct = json.loads( ldap_response )
            except Exception as e:
                status = 'problem loading json; see logs for username, `%s`' % username
            try:
                status = ldap_jdct['info']['browntype']  # note, could be `null/None` -- odd but true
            except Exception as f:
                status = 'problem getting `browntype`; json response:```%s```' % json.loads( ldap_response )
        log.debug( 'status, ```%s```' % status )
        return status

    def run_update( self, entry_dct, ldap_status ):
        """ Hits illiad-status-update api if necessary, then builds and returns entry_dct.
            Called by process_names() """
        username = list( entry_dct.keys() )[0]
        if ldap_status is None:
            entry_dct = { username: {'ldap_status': None, 'update_result': 'Not updated, no ldap status found.', 'update_timestamp': datetime.datetime.now().isoformat()} }
        elif ldap_status[0:7] == 'problem':
            entry_dct = { username: {'ldap_status': None, 'update_result': 'Not updated, %s' % ldap_status, 'update_timestamp': datetime.datetime.now().isoformat()} }
        else:
            api_response = self.hit_illiad_api( username, ldap_status )
            entry_dct = self.process_api_response( username, ldap_status, api_response )
        log.debug( 'processed_entry_dct, ```%s```' % entry_dct )
        return entry_dct

    def hit_illiad_api( self, username, ldap_status ):
        """ Hits illiad-api to update status.
            Called by run_update() """
        return 'foo'

    def process_api_response( self, username, ldap_status, api_response ):
        """ Prepares entry_dct based on api response.
            Called by run_update() """
        return 'bar'

    def write_tracker_update( self, processed_entry_dct ):
        """ Updates local_dct instance-attribute, and writes to tracker-file.
            Called by process_names() """
        try:
            username = list( processed_entry_dct.keys() )[0]
            self.tracker_dct['names'][username] = processed_entry_dct[username]
            with open( TRACKER_FILEPATH, 'w', encoding='utf-8' ) as f:
                f.write( json.dumps(self.tracker_dct, sort_keys = True, indent = 2) )
            log.debug( 'tracker updated and written' )
        except Exception as e:
            log.error( 'exception updating and writing tracker file, ```%s```' % repr(e) )
        return

    ## end class Processor()


if __name__ == '__main__':
    prcssr = Processor()
    prcssr.manage_process()
