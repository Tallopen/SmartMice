# uncompyle6 version 3.8.0
# Python bytecode 3.8.0 (3413)
# Decompiled from: Python 3.9.13 (main, Aug 25 2022, 23:51:50) [MSC v.1916 64 bit (AMD64)]
# Embedded file name: E:\文字文章\科研\Projects\Project 9 Smartmice 2\core\runner.py
# Compiled at: 2022-11-11 21:02:25
# Size of source mod 2**32: 7841 bytes
import core.record as record
import threading, time
from PyQt6.QtCore import QThread

class MyThread(QThread):

    def __init__(self, target, args):
        super(QThread, self).__init__()
        self._foo = target
        self.args = args

    def run(self):
        (self._foo)(*self.args)


class Runner:

    def __init__(self, interface, gui_main):
        self._compiled = False
        self._entrance = None
        self._interface = interface
        self.guiMain = gui_main
        self._record = None
        self._is_running = False
        self._is_pausing = False
        self._start_time = 0
        self._t1 = None

    def fsa_compile--- This code section failed: ---

 L.  56         0  LOAD_GLOBAL              dict
                2  CALL_FUNCTION_0       0  ''
                4  STORE_FAST               '_compiled_nodes'

 L.  57         6  LOAD_GLOBAL              dict
                8  CALL_FUNCTION_0       0  ''
               10  STORE_FAST               '_compiled_variables'

 L.  60        12  BUILD_LIST_0          0 
               14  STORE_FAST               '_quoted_variables'

 L.  61        16  LOAD_FAST                'fsa'
               18  LOAD_STR                 'node'
               20  BINARY_SUBSCR    
               22  LOAD_METHOD              items
               24  CALL_METHOD_0         0  ''
               26  GET_ITER         
               28  FOR_ITER             70  'to 70'
               30  UNPACK_SEQUENCE_2     2 
               32  STORE_FAST               '_'
               34  STORE_FAST               '_node'

 L.  62        36  LOAD_FAST                '_node'
               38  LOAD_STR                 'var'
               40  BINARY_SUBSCR    
               42  LOAD_METHOD              values
               44  CALL_METHOD_0         0  ''
               46  GET_ITER         
               48  FOR_ITER             68  'to 68'
               50  STORE_FAST               '_v'

 L.  63        52  LOAD_FAST                '_quoted_variables'
               54  LOAD_METHOD              append
               56  LOAD_FAST                '_v'
               58  LOAD_STR                 'name'
               60  BINARY_SUBSCR    
               62  CALL_METHOD_1         1  ''
               64  POP_TOP          
               66  JUMP_BACK            48  'to 48'
               68  JUMP_BACK            28  'to 28'

 L.  64        70  LOAD_GLOBAL              list
               72  LOAD_GLOBAL              set
               74  LOAD_FAST                '_quoted_variables'
               76  CALL_FUNCTION_1       1  ''
               78  CALL_FUNCTION_1       1  ''
               80  STORE_FAST               '_quoted_variables'

 L.  67        82  LOAD_FAST                '_quoted_variables'
               84  GET_ITER         
               86  FOR_ITER            202  'to 202'
               88  STORE_FAST               '_var_name'

 L.  68        90  SETUP_FINALLY       132  'to 132'

 L.  69        92  LOAD_FAST                'var_class'
               94  LOAD_FAST                'variable_dict'
               96  LOAD_FAST                '_var_name'
               98  BINARY_SUBSCR    
              100  LOAD_STR                 'type'
              102  BINARY_SUBSCR    
              104  BINARY_SUBSCR    

 L.  70       106  LOAD_FAST                'variable_dict'
              108  LOAD_FAST                '_var_name'
              110  BINARY_SUBSCR    
              112  LOAD_STR                 'value'
              114  BINARY_SUBSCR    

 L.  71       116  LOAD_FAST                '_var_name'

 L.  69       118  LOAD_CONST               ('value', '_name')
              120  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              122  LOAD_FAST                '_compiled_variables'
              124  LOAD_FAST                '_var_name'
              126  STORE_SUBSCR     
              128  POP_BLOCK        
              130  JUMP_BACK            86  'to 86'
            132_0  COME_FROM_FINALLY    90  '90'

 L.  73       132  DUP_TOP          
              134  LOAD_GLOBAL              Exception
              136  COMPARE_OP               exception-match
              138  POP_JUMP_IF_FALSE   198  'to 198'
              140  POP_TOP          
              142  STORE_FAST               'e'
              144  POP_TOP          
              146  SETUP_FINALLY       186  'to 186'

 L.  74       148  LOAD_CONST               False
              150  LOAD_STR                 'Error in variable '
              152  LOAD_FAST                '_var_name'
              154  FORMAT_VALUE          0  ''
              156  LOAD_STR                 ': '
              158  LOAD_FAST                'e'
              160  LOAD_ATTR                args
              162  LOAD_CONST               0
              164  BINARY_SUBSCR    
              166  FORMAT_VALUE          0  ''
              168  BUILD_STRING_4        4 
              170  BUILD_TUPLE_2         2 
              172  ROT_FOUR         
              174  POP_BLOCK        
              176  POP_EXCEPT       
              178  CALL_FINALLY        186  'to 186'
              180  ROT_TWO          
              182  POP_TOP          
              184  RETURN_VALUE     
            186_0  COME_FROM           178  '178'
            186_1  COME_FROM_FINALLY   146  '146'
              186  LOAD_CONST               None
              188  STORE_FAST               'e'
              190  DELETE_FAST              'e'
              192  END_FINALLY      
              194  POP_EXCEPT       
              196  JUMP_BACK            86  'to 86'
            198_0  COME_FROM           138  '138'
              198  END_FINALLY      
              200  JUMP_BACK            86  'to 86'

 L.  75       202  LOAD_FAST                '_compiled_variables'
              204  LOAD_METHOD              items
              206  CALL_METHOD_0         0  ''
              208  GET_ITER         
            210_0  COME_FROM           258  '258'
              210  FOR_ITER            270  'to 270'
              212  UNPACK_SEQUENCE_2     2 
              214  STORE_FAST               '_'
              216  STORE_FAST               '_variable'

 L.  76       218  LOAD_FAST                '_variable'
              220  LOAD_ATTR                requirements
              222  LOAD_STR                 'variable'
              224  BINARY_SUBSCR    
              226  POP_JUMP_IF_FALSE   234  'to 234'

 L.  77       228  LOAD_FAST                '_compiled_variables'
              230  LOAD_FAST                '_variable'
              232  STORE_ATTR               variable
            234_0  COME_FROM           226  '226'

 L.  78       234  LOAD_FAST                '_variable'
              236  LOAD_ATTR                requirements
              238  LOAD_STR                 'runner'
              240  BINARY_SUBSCR    
              242  POP_JUMP_IF_FALSE   250  'to 250'

 L.  79       244  LOAD_FAST                'self'
              246  LOAD_FAST                '_variable'
              248  STORE_ATTR               runner
            250_0  COME_FROM           242  '242'

 L.  80       250  LOAD_FAST                '_variable'
              252  LOAD_ATTR                requirements
              254  LOAD_STR                 'interface'
              256  BINARY_SUBSCR    
              258  POP_JUMP_IF_FALSE   210  'to 210'

 L.  81       260  LOAD_FAST                'self'
              262  LOAD_ATTR                _interface
              264  LOAD_FAST                '_variable'
              266  STORE_ATTR               interface
              268  JUMP_BACK           210  'to 210'

 L.  84       270  BUILD_LIST_0          0 
              272  STORE_FAST               '_start_nodes'

 L.  85       274  BUILD_LIST_0          0 
              276  STORE_FAST               '_end_nodes'

 L.  86       278  LOAD_FAST                'fsa'
              280  LOAD_STR                 'node-index'
              282  BINARY_SUBSCR    
              284  GET_ITER         
            286_0  COME_FROM           482  '482'
              286  FOR_ITER            504  'to 504'
              288  STORE_FAST               '_node_name'

 L.  87       290  LOAD_GLOBAL              dict
              292  CALL_FUNCTION_0       0  ''
              294  STORE_FAST               '_var_dict'

 L.  88       296  LOAD_FAST                'fsa'
              298  LOAD_STR                 'node'
              300  BINARY_SUBSCR    
              302  LOAD_FAST                '_node_name'
              304  BINARY_SUBSCR    
              306  LOAD_STR                 'var'
              308  BINARY_SUBSCR    
              310  LOAD_METHOD              items
              312  CALL_METHOD_0         0  ''
              314  GET_ITER         
              316  FOR_ITER            388  'to 388'
              318  UNPACK_SEQUENCE_2     2 
              320  STORE_FAST               '_ph_name'
              322  STORE_FAST               '_var_term'

 L.  89       324  LOAD_FAST                '_var_term'
              326  LOAD_STR                 'name'
              328  BINARY_SUBSCR    
              330  LOAD_CONST               None
              332  COMPARE_OP               is
          334_336  POP_JUMP_IF_FALSE   368  'to 368'

 L.  90       338  LOAD_CONST               False
              340  LOAD_STR                 "There is a vacant placeholder '"
              342  LOAD_FAST                '_ph_name'
              344  FORMAT_VALUE          0  ''
              346  LOAD_STR                 "' in node '"
              348  LOAD_FAST                '_node_name'
              350  FORMAT_VALUE          0  ''
              352  LOAD_STR                 "'."
              354  BUILD_STRING_5        5 
              356  BUILD_TUPLE_2         2 
              358  ROT_TWO          
              360  POP_TOP          
              362  ROT_TWO          
              364  POP_TOP          
              366  RETURN_VALUE     
            368_0  COME_FROM           334  '334'

 L.  91       368  LOAD_FAST                '_compiled_variables'
              370  LOAD_FAST                '_var_term'
              372  LOAD_STR                 'name'
              374  BINARY_SUBSCR    
              376  BINARY_SUBSCR    
              378  LOAD_FAST                '_var_dict'
              380  LOAD_FAST                '_ph_name'
              382  STORE_SUBSCR     
          384_386  JUMP_BACK           316  'to 316'

 L.  92       388  LOAD_FAST                'node_class'
              390  LOAD_FAST                'fsa'
              392  LOAD_STR                 'node'
              394  BINARY_SUBSCR    
              396  LOAD_FAST                '_node_name'
              398  BINARY_SUBSCR    
              400  LOAD_STR                 'type'
              402  BINARY_SUBSCR    
              404  BINARY_SUBSCR    

 L.  94       406  LOAD_FAST                '_var_dict'

 L.  95       408  LOAD_FAST                '_node_name'

 L.  93       410  LOAD_CONST               ('var', 'name')
              412  BUILD_CONST_KEY_MAP_2     2 

 L.  92       414  LOAD_CONST               ('runtime_dict',)
              416  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              418  LOAD_FAST                '_compiled_nodes'
              420  LOAD_FAST                '_node_name'
              422  STORE_SUBSCR     

 L.  98       424  LOAD_FAST                'node_class'
              426  LOAD_FAST                'fsa'
              428  LOAD_STR                 'node'
              430  BINARY_SUBSCR    
              432  LOAD_FAST                '_node_name'
              434  BINARY_SUBSCR    
              436  LOAD_STR                 'type'
              438  BINARY_SUBSCR    
              440  BINARY_SUBSCR    
              442  LOAD_ATTR                has_input
          444_446  POP_JUMP_IF_TRUE    464  'to 464'

 L.  99       448  LOAD_FAST                '_start_nodes'
              450  LOAD_METHOD              append
              452  LOAD_FAST                '_compiled_nodes'
              454  LOAD_FAST                '_node_name'
              456  BINARY_SUBSCR    
              458  CALL_METHOD_1         1  ''
              460  POP_TOP          
              462  JUMP_BACK           286  'to 286'
            464_0  COME_FROM           444  '444'

 L. 100       464  LOAD_FAST                'fsa'
              466  LOAD_STR                 'node'
              468  BINARY_SUBSCR    
              470  LOAD_FAST                '_node_name'
              472  BINARY_SUBSCR    
              474  LOAD_STR                 'type'
              476  BINARY_SUBSCR    
              478  LOAD_STR                 'EndNode'
              480  COMPARE_OP               ==
          482_484  POP_JUMP_IF_FALSE   286  'to 286'

 L. 101       486  LOAD_FAST                '_end_nodes'
              488  LOAD_METHOD              append
              490  LOAD_FAST                '_compiled_nodes'
              492  LOAD_FAST                '_node_name'
              494  BINARY_SUBSCR    
              496  CALL_METHOD_1         1  ''
              498  POP_TOP          
          500_502  JUMP_BACK           286  'to 286'

 L. 103       504  LOAD_GLOBAL              len
              506  LOAD_FAST                '_start_nodes'
              508  CALL_FUNCTION_1       1  ''
              510  LOAD_CONST               1
              512  COMPARE_OP               !=
          514_516  POP_JUMP_IF_FALSE   538  'to 538'

 L. 104       518  LOAD_CONST               False
              520  LOAD_STR                 'There should be 1 start nodes in one FSA; found '
              522  LOAD_GLOBAL              len
              524  LOAD_FAST                '_start_nodes'
              526  CALL_FUNCTION_1       1  ''
              528  FORMAT_VALUE          0  ''
              530  LOAD_STR                 '.'
              532  BUILD_STRING_3        3 
              534  BUILD_TUPLE_2         2 
              536  RETURN_VALUE     
            538_0  COME_FROM           514  '514'

 L. 105       538  LOAD_GLOBAL              len
              540  LOAD_FAST                '_end_nodes'
              542  CALL_FUNCTION_1       1  ''
              544  LOAD_CONST               0
              546  COMPARE_OP               ==
          548_550  POP_JUMP_IF_FALSE   556  'to 556'

 L. 106       552  LOAD_CONST               (False, 'There should be at least 1 end nodes in one FSA.')
              554  RETURN_VALUE     
            556_0  COME_FROM           548  '548'

 L. 109       556  LOAD_FAST                'fsa'
              558  LOAD_STR                 'node-index'
              560  BINARY_SUBSCR    
              562  GET_ITER         
              564  FOR_ITER            686  'to 686'
              566  STORE_FAST               '_node_name'

 L. 110       568  LOAD_GLOBAL              dict
              570  CALL_FUNCTION_0       0  ''
              572  STORE_FAST               '_link_jump'

 L. 111       574  LOAD_FAST                'fsa'
              576  LOAD_STR                 'node'
              578  BINARY_SUBSCR    
              580  LOAD_FAST                '_node_name'
              582  BINARY_SUBSCR    
              584  LOAD_STR                 'out-link'
              586  BINARY_SUBSCR    
              588  LOAD_METHOD              items
              590  CALL_METHOD_0         0  ''
              592  GET_ITER         
              594  FOR_ITER            668  'to 668'
              596  UNPACK_SEQUENCE_2     2 
              598  STORE_FAST               '_key'
              600  STORE_FAST               '_link_id'

 L. 112       602  LOAD_FAST                '_link_id'
              604  LOAD_CONST               None
              606  COMPARE_OP               is
          608_610  POP_JUMP_IF_FALSE   640  'to 640'

 L. 113       612  LOAD_CONST               False
              614  LOAD_STR                 "Unlinked output '"
              616  LOAD_FAST                '_key'
              618  FORMAT_VALUE          0  ''
              620  LOAD_STR                 "' detected in node "
              622  LOAD_FAST                '_node_name'
              624  FORMAT_VALUE          0  ''
              626  BUILD_STRING_4        4 
              628  BUILD_TUPLE_2         2 
              630  ROT_TWO          
              632  POP_TOP          
              634  ROT_TWO          
              636  POP_TOP          
              638  RETURN_VALUE     
            640_0  COME_FROM           608  '608'

 L. 114       640  LOAD_FAST                '_compiled_nodes'
              642  LOAD_FAST                'fsa'
              644  LOAD_STR                 'link'
              646  BINARY_SUBSCR    
              648  LOAD_FAST                '_link_id'
              650  BINARY_SUBSCR    
              652  LOAD_STR                 'to'
              654  BINARY_SUBSCR    
              656  BINARY_SUBSCR    
              658  LOAD_FAST                '_link_jump'
              660  LOAD_FAST                '_key'
              662  STORE_SUBSCR     
          664_666  JUMP_BACK           594  'to 594'

 L. 115       668  LOAD_FAST                '_link_jump'
              670  LOAD_FAST                '_compiled_nodes'
              672  LOAD_FAST                '_node_name'
              674  BINARY_SUBSCR    
              676  LOAD_ATTR                runtime
              678  LOAD_STR                 'jump'
              680  STORE_SUBSCR     
          682_684  JUMP_BACK           564  'to 564'

 L. 117       686  LOAD_FAST                '_start_nodes'
              688  LOAD_CONST               0
              690  BINARY_SUBSCR    
              692  LOAD_FAST                'self'
              694  STORE_ATTR               _entrance

 L. 118       696  LOAD_CONST               True
              698  LOAD_FAST                'self'
              700  STORE_ATTR               _compiled

 L. 119       702  LOAD_CONST               True
              704  LOAD_FAST                '_compiled_variables'
              706  BUILD_TUPLE_2         2 
              708  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `ROT_TWO' instruction at offset 180

    def _run_func--- This code section failed: ---

 L. 123         0  LOAD_CONST               False
                2  STORE_FAST               '_erroneous'

 L. 124         4  LOAD_STR                 ''
                6  STORE_FAST               '_error_message'

 L. 126         8  LOAD_FAST                'self'
               10  LOAD_ATTR                _interface
               12  LOAD_ATTR                run_begin
               14  LOAD_METHOD              emit
               16  CALL_METHOD_0         0  ''
               18  POP_TOP          

 L. 128        20  LOAD_CONST               True
               22  LOAD_FAST                'self'
               24  STORE_ATTR               _is_running

 L. 129        26  LOAD_FAST                'self'
               28  LOAD_ATTR                _entrance
               30  STORE_FAST               '_current_node'

 L. 130        32  LOAD_FAST                'self'
               34  LOAD_ATTR                _entrance
               36  LOAD_ATTR                runtime
               38  LOAD_STR                 'name'
               40  BINARY_SUBSCR    
               42  STORE_FAST               '_current_node_name'

 L. 131        44  LOAD_CONST               None
               46  STORE_FAST               '_output'

 L. 132        48  LOAD_GLOBAL              threading
               50  LOAD_ATTR                Thread
               52  LOAD_FAST                'self'
               54  LOAD_ATTR                _tic
               56  LOAD_CONST               ('target',)
               58  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               60  LOAD_METHOD              start
               62  CALL_METHOD_0         0  ''
               64  POP_TOP          

 L. 133        66  SETUP_FINALLY       258  'to 258'

 L. 134        68  LOAD_GLOBAL              time
               70  LOAD_METHOD              time
               72  CALL_METHOD_0         0  ''
               74  LOAD_FAST                'self'
               76  STORE_ATTR               _start_time

 L. 135        78  LOAD_FAST                '_record'
               80  LOAD_METHOD              set_start_time
               82  LOAD_FAST                'self'
               84  LOAD_ATTR                _start_time
               86  CALL_METHOD_1         1  ''
               88  POP_TOP          

 L. 136        90  LOAD_FAST                '_record'
               92  LOAD_METHOD              log
               94  LOAD_STR                 'System Event'
               96  LOAD_STR                 'Start Running'
               98  LOAD_GLOBAL              str
              100  LOAD_FAST                'self'
              102  LOAD_ATTR                _start_time
              104  CALL_FUNCTION_1       1  ''
              106  CALL_METHOD_3         3  ''
              108  POP_TOP          

 L. 137       110  LOAD_FAST                'self'
              112  LOAD_ATTR                _is_running
              114  POP_JUMP_IF_FALSE   196  'to 196'

 L. 138       116  LOAD_FAST                'self'
              118  LOAD_ATTR                _is_pausing
              120  POP_JUMP_IF_FALSE   134  'to 134'

 L. 139       122  LOAD_GLOBAL              time
              124  LOAD_METHOD              sleep
              126  LOAD_CONST               0.1
              128  CALL_METHOD_1         1  ''
              130  POP_TOP          
              132  JUMP_BACK           110  'to 110'
            134_0  COME_FROM           120  '120'

 L. 141       134  LOAD_FAST                'self'
              136  LOAD_ATTR                _interface
              138  LOAD_ATTR                run_evoke
              140  LOAD_METHOD              emit
              142  LOAD_FAST                '_current_node'
              144  LOAD_ATTR                runtime
              146  LOAD_STR                 'name'
              148  BINARY_SUBSCR    
              150  CALL_METHOD_1         1  ''
              152  POP_TOP          

 L. 142       154  LOAD_FAST                '_current_node'
              156  LOAD_METHOD              run
              158  LOAD_FAST                '_record'
              160  CALL_METHOD_1         1  ''
              162  STORE_FAST               '_output'

 L. 143       164  LOAD_FAST                '_output'
              166  LOAD_CONST               None
              168  COMPARE_OP               is
              170  POP_JUMP_IF_FALSE   180  'to 180'

 L. 144       172  LOAD_CONST               False
              174  LOAD_FAST                'self'
              176  STORE_ATTR               _is_running
              178  JUMP_BACK           110  'to 110'
            180_0  COME_FROM           170  '170'

 L. 146       180  LOAD_FAST                '_output'
              182  STORE_FAST               '_current_node'

 L. 147       184  LOAD_FAST                '_current_node'
              186  LOAD_ATTR                runtime
              188  LOAD_STR                 'name'
              190  BINARY_SUBSCR    
              192  STORE_FAST               '_current_node_name'
              194  JUMP_BACK           110  'to 110'
            196_0  COME_FROM           114  '114'

 L. 148       196  LOAD_FAST                '_record'
              198  LOAD_METHOD              log
              200  LOAD_STR                 'System Event'
              202  LOAD_STR                 'Running Ends'
              204  LOAD_STR                 ''
              206  CALL_METHOD_3         3  ''
              208  POP_TOP          

 L. 149       210  LOAD_GLOBAL              time
              212  LOAD_METHOD              time
              214  CALL_METHOD_0         0  ''
              216  LOAD_FAST                'self'
              218  LOAD_ATTR                _start_time
              220  BINARY_SUBTRACT  
              222  LOAD_FAST                '_record'
              224  STORE_ATTR               time_length

 L. 150       226  LOAD_FAST                '_record'
              228  LOAD_METHOD              save
              230  CALL_METHOD_0         0  ''
              232  POP_TOP          

 L. 151       234  LOAD_CONST               False
              236  LOAD_FAST                'self'
              238  STORE_ATTR               _is_running

 L. 152       240  LOAD_FAST                'self'
              242  LOAD_ATTR                _interface
              244  LOAD_ATTR                run_end
              246  LOAD_METHOD              emit
              248  CALL_METHOD_0         0  ''
              250  POP_TOP          

 L. 153       252  POP_BLOCK        
              254  LOAD_CONST               (True, None)
              256  RETURN_VALUE     
            258_0  COME_FROM_FINALLY    66  '66'

 L. 154       258  DUP_TOP          
              260  LOAD_GLOBAL              Exception
              262  COMPARE_OP               exception-match
          264_266  POP_JUMP_IF_FALSE   378  'to 378'
              268  POP_TOP          
              270  STORE_FAST               'e'
              272  POP_TOP          
              274  SETUP_FINALLY       366  'to 366'

 L. 155       276  LOAD_CONST               True
              278  STORE_FAST               '_erroneous'

 L. 156       280  LOAD_FAST                'e'
              282  LOAD_ATTR                args
              284  LOAD_CONST               0
              286  BINARY_SUBSCR    
              288  STORE_FAST               '_error_message'

 L. 157       290  LOAD_CONST               False
              292  LOAD_FAST                'self'
              294  STORE_ATTR               _is_running

 L. 158       296  LOAD_FAST                '_record'
              298  LOAD_METHOD              log
              300  LOAD_STR                 'System Event'
              302  LOAD_STR                 'Error Encountered'
              304  LOAD_FAST                'e'
              306  LOAD_ATTR                args
              308  LOAD_CONST               0
              310  BINARY_SUBSCR    
              312  CALL_METHOD_3         3  ''
              314  POP_TOP          

 L. 159       316  LOAD_FAST                '_record'
              318  LOAD_METHOD              save
              320  CALL_METHOD_0         0  ''
              322  POP_TOP          

 L. 161       324  LOAD_FAST                'self'
              326  LOAD_ATTR                _interface
              328  LOAD_ATTR                run_end
              330  LOAD_METHOD              emit
              332  CALL_METHOD_0         0  ''
              334  POP_TOP          

 L. 162       336  LOAD_CONST               False
              338  LOAD_STR                 "Error at '"
              340  LOAD_FAST                '_current_node_name'
              342  FORMAT_VALUE          0  ''
              344  LOAD_STR                 "': \n"
              346  LOAD_FAST                '_error_message'
              348  FORMAT_VALUE          0  ''
              350  LOAD_STR                 ', running aborted.'
              352  BUILD_STRING_5        5 
              354  BUILD_TUPLE_2         2 
              356  ROT_FOUR         
              358  POP_BLOCK        
              360  POP_EXCEPT       
              362  CALL_FINALLY        366  'to 366'
              364  RETURN_VALUE     
            366_0  COME_FROM           362  '362'
            366_1  COME_FROM_FINALLY   274  '274'
              366  LOAD_CONST               None
              368  STORE_FAST               'e'
              370  DELETE_FAST              'e'
              372  END_FINALLY      
              374  POP_EXCEPT       
              376  JUMP_FORWARD        380  'to 380'
            378_0  COME_FROM           264  '264'
              378  END_FINALLY      
            380_0  COME_FROM           376  '376'

Parse error at or near `RETURN_VALUE' instruction at offset 256

    def run(self, record_dict, _compiled_variables):
        """
        run the compiled FSA
        :param record_dict: the dictionary of designated record
        :param _compiled_variables: what was returned in self.compile()
        :return:
        (True, None) - run successful
        (False, "Message") - error encountered, message returned
        """
        if not self._is_running:
            if self._compiled:
                self._record = record.Record(self._interface, record_dict)
                for _variable in _compiled_variables.values():
                    _variable.set_recordself._record
                else:
                    self._t1 = MyThread(target=(self._run_func), args=(self._record,))
                    self._t1.start()
                    return (True, None)

            return (False, 'No FSA is compiled.')
        else:
            return (False, 'There is currently a program running.')

    def time(self):
        return time.time() - self._start_time

    def _tic(self):
        while self._is_running:
            self._interface.tick.emit(time.time() - self._start_time)
            time.sleep0.05

    def pause(self):
        if self._is_running:
            self._is_pausing = True
            self._record.log'System Event''Pause'''

    def continue_run(self):
        if self._is_running:
            self._is_pausing = False
            self._record.log'System Event''Continue'''

    def is_running(self):
        return self._is_running