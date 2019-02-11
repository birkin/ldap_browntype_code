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
            entry = self.grab_next_entry()
            entry = self.grab_ldap_status( entry )
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

    def grab_ldap_status( self, entry ):
        """ Assigns current ldap status to name-dct.
            Called by process_names() """
        # command = 'java -cp %s net.sf.saxon.Transform -t -s:"%s" -xsl:"%s" -o:"%s"' % (
        #     settings_app.SAXON_CLASSPATH, temp_xml_path, temp_xsl_path, temp_output_path )

        username = list( entry.keys() )[0]
        command = 'php %s -u %s' % ( LDAP_SCRIPT_PATH, username )
        log.debug( 'command, `%s`' % command )

        try:
            subprocess.check_output( [command, '-1'], stderr=subprocess.STDOUT, shell=True )
            temp_output_file_reference.flush()
            transformed_xml = temp_output_file_reference.read().decode('utf-8')  # saxon produces byte-string output
        except subprocess.CalledProcessError as e:
            log.error( 'exception, ```%s```' % unicode(repr(e)) )
            log.error( 'e.output, `%s`' % e.output )
            # log.error( 'e.__dict__, ```%s```' % pprint.pformat(e.__dict__) )
            transformed_xml = 'Error on transformation; see log at `%s`' % unicode( datetime.datetime.now() )
        log.debug( 'type(transformed_xml), `%s`; transformed_xml, ```%s```' % (type(transformed_xml), transformed_xml) )
        return transformed_xml



    ## end class Processor()


if __name__ == '__main__':
    prcssr = Processor()
    prcssr.manage_process()
