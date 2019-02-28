"""
Iterates through the tracker file to make counts. """

import datetime, json, logging, os, pprint, time


LOG_PATH = os.environ['LDP_BRNTP__LOG_PATH']
LOG_LEVEL = os.environ['LDP_BRNTP__LOG_LEVEL']
TRACKER_FILEPATH = os.environ['LDP_BRNTP__TRACKER_FILEPATH']


level_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
logging.basicConfig(
    filename=LOG_PATH, level=level_dct[LOG_LEVEL],
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s', datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.info( '\n---\n' + 'starting\n' + '---' )


class Analyzer( object ):

    def __init__( self ):
        self.tracker_dct = None
        self.counts_dct = {}
        self.counts_lst = []

    def manage_process( self ):
        log.debug( 'starting manage_process()' )
        self.load_tracker_dct()
        names = list( self.tracker_dct['names'].keys() )
        for name in names:
            self.make_counts_dct( name )
        log.debug( 'counts_dct, ```%s```' % pprint.pformat(self.counts_dct) )
        print( '---\nsorted alphabetically\n---' )
        pprint.pprint( self.counts_dct )
        self.make_counts_lst()
        return

    # def check_print( self, count ):
    #     """ Outputs count if necessary.
    #         Called by process_names() """
    #     time.sleep( .3 )
    #     if count % 100 == 0:
    #         timestamp = datetime.datetime.now().isoformat()
    #         print( '`%s` records processed; timestamp, `%s`' % (count, timestamp) )
    #     return

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

    def make_counts_dct( self, name ):
        """ Updates self.counts_dct
            Called by process_names() """
        data_dct = self.tracker_dct['names'][name]
        update_result = data_dct['update_result']
        update_result = self.massage_update_result( update_result )
        if update_result in self.counts_dct.keys():
            self.counts_dct[update_result] += 1
        else:
            self.counts_dct[update_result] = 1
        return

    def massage_update_result( self, update_result ):
        if '''not found in directory''' in update_result:
            update_result = '''Not updated, not found in directory'''
        elif '''Not updated, problem getting `browntype`''' in update_result:
            # update_result = '''"Not updated, problem getting `browntype`; json response:```{'info': {'eppn': None,'''
            update_result = '''Not updated, problem getting `browntype`'''
        return update_result

    # def massage_update_result( self, update_result ):
    #     if '''Not updated, problem getting `browntype`''' in update_result:
    #         # update_result = '''"Not updated, problem getting `browntype`; json response:```{'info': {'eppn': None,'''
    #         update_result = '''Not updated, problem getting `browntype`'''
    #     elif '''not found in directory''' in update_result:
    #         update_result = '''not found in directory'''
    #     return update_result

    def make_counts_lst( self ):
        from operator import itemgetter
        counts = sorted( self.counts_dct.items(), key=itemgetter(1), reverse=True )
        print( '---\nsorted by count\n---' )
        pprint.pprint( counts )
        return


    ## end class Analyzer()


if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.manage_process()
