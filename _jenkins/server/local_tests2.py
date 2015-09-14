# -*- coding: utf-8 -*-
import time
import signal
import sys
from threading import Event
import os
#


output = """
Started by user Paweł Nogieć
[EnvInject] - Loading node environment variables.
Building remotely on tl99_test in workspace /home/ute/workspace/test_on_tl99_test
[test_on_tl99_test] $ /bin/sh -xe /tmp/hudson7071240286760041662.sh
+ . /home/ute/virtualenvs/ute/bin/activate
+ deactivate nondestructive
+ unset pydoc
+ [ -n  ]
+ [ -n  ]
+ [ -n  -o -n  ]
+ [ -n  ]
+ unset VIRTUAL_ENV
+ [ ! nondestructive = nondestructive ]
+ VIRTUAL_ENV=/home/ute/virtualenvs/ute
+ export VIRTUAL_ENV
+ _OLD_VIRTUAL_PATH=/opt/ute/python/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games:/opt/ute/jython/bin
+ PATH=/home/ute/virtualenvs/ute/bin:/opt/ute/python/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games:/opt/ute/jython/bin
+ export PATH
+ [ -n  ]
+ [ -z  ]
+ _OLD_VIRTUAL_PS1=$
+ [ x != x ]
+ basename /home/ute/virtualenvs/ute
+ [ ute = __ ]
+ basename /home/ute/virtualenvs/ute
+ PS1=(ute)$
+ export PS1
+ alias pydoc=python -m pydoc
+ [ -n  -o -n  ]
+ python /home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/CRT/ivk_pybot.py -S /home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465 -c /home/ute/moj_config.yaml -L DEBUG -d /home/ute/logs/tl99_test_2015-08-31_12-45-33
 - 12:45:35 31/08/2015 -
==============================================================================
LTE2465
==============================================================================
LTE2465.Tests
==============================================================================
LTE2465.Tests.LTE2465 A a
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_a/LTE2465_A_a_AC_1_SIB1_and_SIB9_broadcast_with_CSG_disabled_then_enabled.robot': Initializing test library 'LTE2465.resources.LTE2465_A_a_AC_1.LTE2465_A_a_AC_1' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_a_AC_1.py", line 10, in __init__
    super(LTE2465_A_a_AC_1, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 1 SIB1 and SIB9 broadcast with CSG...
==============================================================================
[1]LTE2465-A-a-1.1_SIB1_and_SIB9_broadcast_with_CSG_disabled_then_... | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 1 SIB1 and SIB9 broadcast... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_a/LTE2465_A_a_AC_2_SIB1_broadcast_with_CSG_heNBName_not_set.robot': Initializing test library 'LTE2465.resources.LTE2465_A_a_AC_2.LTE2465_A_a_AC_2' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_a_AC_2.py", line 9, in __init__
    super(LTE2465_A_a_AC_2, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 2 SIB1 broadcast with CSG heNBName...
==============================================================================
[1]LTE2465-A-a-1.2_SIB1_and_broadcast_with_CSG_enabled_no_heNBName    | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 2 SIB1 broadcast with CSG... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_a/LTE2465_A_a_AC_3_SIB1_and_SIB9_changed_csgId_and_hENBName.robot': Initializing test library 'LTE2465.resources.LTE2465_A_a_AC_3.LTE2465_A_a_AC_3' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_a_AC_3.py", line 10, in __init__
    super(LTE2465_A_a_AC_3, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 3 SIB1 and SIB9 changed csgId and ...
==============================================================================
[1]LTE2465-A-a-1.3_SIB1_and_SIB9_changes_after_csgId_and_heNBName_... | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 3 SIB1 and SIB9 changed c... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_a/LTE2465_A_a_AC_4_SIB1_and_SIB9_broadcast_CSG_enabled_then_disabled.robot': Initializing test library 'LTE2465.resources.LTE2465_A_a_AC_4.LTE2465_A_a_AC_4' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_a_AC_4.py", line 10, in __init__
    super(LTE2465_A_a_AC_4, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 4 SIB1 and SIB9 broadcast CSG enab...
==============================================================================
[1]LTE2465-A-a-1.4_SIB1_and_SIB9_broadcast_CSG_enabled_then_disabled  | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A a.LTE2465 A a AC 4 SIB1 and SIB9 broadcast... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A a                                             | FAIL |
4 critical tests, 0 passed, 4 failed
4 tests total, 0 passed, 4 failed
==============================================================================
LTE2465.Tests.LTE2465 A b
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_b/LTE2465_A_b_Call_Setup_Failure_to_CSG.robot': Initializing test library 'LTE2465.resources.LTE2465_A_b_Call_Setup_Failure_to_CSG.LTE2465_A_b_Call_Setup_Failure_to_CSG' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_b_Call_Setup_Failure_to_CSG.py", line 10, in __init__
    super(LTE2465_A_b_Call_Setup_Failure_to_CSG, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A b.LTE2465 A b Call Setup Failure to CSG
==============================================================================
[1]LTE2465-A-b-2_Call_Setup_Failure_to_CSG                            | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A b.LTE2465 A b Call Setup Failure to CSG       | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_b/LTE2465_A_b_Connection_Setup_to_CSG.robot': Initializing test library 'LTE2465.resources.LTE2465_A_b_Connection_Setup_to_CSG.LTE2465_A_b_Connection_Setup_to_CSG' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_b_Connection_Setup_to_CSG.py", line 10, in __init__
    super(LTE2465_A_b_Connection_Setup_to_CSG, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A b.LTE2465 A b Connection Setup to CSG
==============================================================================
[1]LTE2465-A-b-1_Connection_Setup_to_CSG                              | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A b.LTE2465 A b Connection Setup to CSG         | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_b/LTE2465_A_b_Connection_Setup_to_CSG_changed_csgId_reattach.robot': Initializing test library 'LTE2465.resources.LTE2465_A_b_Connection_Setup_to_CSG_changed_csgId_reattach.LTE2465_A_b_Connection_Setup_to_CSG_changed_csgId_reattach' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_b_Connection_Setup_to_CSG_changed_csgId_reattach.py", line 10, in __init__
    super(LTE2465_A_b_Connection_Setup_to_CSG_changed_csgId_reattach, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A b.LTE2465 A b Connection Setup to CSG changed csgId...
==============================================================================
[1]LTE2465-A-b-3.1_Connection_Setup_to_CSG_changed_csgId_reattach     | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A b.LTE2465 A b Connection Setup to CSG chan... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_b/LTE2465_A_b_Connection_Setup_to_CSG_emergency.robot': Initializing test library 'LTE2465.resources.LTE2465_A_b_Connection_Setup_to_CSG_emergency.LTE2465_A_b_Connection_Setup_to_CSG_emergency' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_b_Connection_Setup_to_CSG_emergency.py", line 10, in __init__
    super(LTE2465_A_b_Connection_Setup_to_CSG_emergency, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A b.LTE2465 A b Connection Setup to CSG emergency
==============================================================================
[1]LTE2465-A-b-3.2_Connection_Setup_to_CSG_emergency                  | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A b.LTE2465 A b Connection Setup to CSG emer... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A b                                             | FAIL |
4 critical tests, 0 passed, 4 failed
4 tests total, 0 passed, 4 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_c': Initializing test library 'LTE2465.resources.LTE2465_A_c_configuration.LTE2465_A_c_configuration' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_c_configuration.py", line 7, in __init__
    super(LTE2465_A_c_configuration, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A c
==============================================================================
LTE2465.Tests.LTE2465 A c.LTE2465 A c AC 1 S1 Setup for CSG eNB
==============================================================================
[1]C-Pln_LTE2465-A-c-1.1_Inclusion of CSG Id in S1SetupRequest (se... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A c.LTE2465 A c AC 1 S1 Setup for CSG eNB       | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A c                                             | FAIL |
Suite setup failed:
No keyword with name 'Setup_for_robot' found.

Also suite teardown failed:
No keyword with name 'Teardown_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_d': Initializing test library 'LTE2465.resources.LTE2465_A_d_common' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_d_common.py", line 13, in __init__
    super(LTE2465_A_d_common, self).__init__(id)
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A d
==============================================================================
LTE2465.Tests.LTE2465 A d.LTE2465 A d AC 1 Inclusion of CSG Id in X2AP mess...
==============================================================================
[1]LTE2465_A_d_Inclusion_of_CSG_Id_in_X2AP_messages                   | FAIL |
Parent suite setup failed:
No keyword with name 'setup_tests' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A d.LTE2465 A d AC 1 Inclusion of CSG Id in ... | FAIL |
Parent suite setup failed:
No keyword with name 'setup_tests' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A d.LTE2465 A d AC 2 Exclusion of CSG Id in X2AP mess...
==============================================================================
[1]LTE2465_A_d_Exclusion_of_CSG_Id_in_X2AP_messages                   | FAIL |
Parent suite setup failed:
No keyword with name 'setup_tests' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A d.LTE2465 A d AC 2 Exclusion of CSG Id in ... | FAIL |
Parent suite setup failed:
No keyword with name 'setup_tests' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A d                                             | FAIL |
Suite setup failed:
No keyword with name 'setup_tests' found.

Also suite teardown failed:
No keyword with name 'teardown_tests' found.

2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
LTE2465.Tests.LTE2465 A e
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_e/LTE2465_A_e_AC_1_block_incoming_X2_handover_to_CSG_cell.robot': Initializing test library 'LTE2465.resources.LTE2465_A_e_AC_1.LTE2465_A_e_AC_1' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_e_AC_1.py", line 14, in __init__
    super(LTE2465_A_e_AC_1, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A e.LTE2465 A e AC 1 block incoming X2 handover to CS...
==============================================================================
[1]LTE2465_A_e_Block_incoming_X2_HO_to_CSG_cell                       | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A e.LTE2465 A e AC 1 block incoming X2 hando... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_e/LTE2465_A_e_AC_2_block_incoming_intra-eNB_inter-cell_handover_to_CSG_cell.robot': Initializing test library 'LTE2465.resources.LTE2465_A_e_AC_2.LTE2465_A_e_AC_2' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_e_AC_2.py", line 11, in __init__
    super(LTE2465_A_e_AC_2, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A e.LTE2465 A e AC 2 block incoming intra-eNB inter-c...
==============================================================================
[1]LTE2465_A_e_Block_incoming_intra-eNB_HO_to_CSG_cell                | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A e.LTE2465 A e AC 2 block incoming intra-eN... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A e                                             | FAIL |
2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_f': Initializing test library 'LTE2465.resources.LTE2465_A_f_common.LTE2465_A_f_common' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_f_common.py", line 14, in __init__
    super(LTE2465_A_f_common, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A f
==============================================================================
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 1 intra eNB reestablishment from n...
==============================================================================
[1]LTE2465_A_f_1_intra_eNB_reestablishment_from_non_CSG_cell_to_CS... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 1 intra eNB reestablishme... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 2 intra eNB reestablishment betwee...
==============================================================================
[1]LTE2465_A_f_2_intra_eNB_reestablishment_between_CSG_cells_with_... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 2 intra eNB reestablishme... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 3 intra eNB reestablishment betwee...
==============================================================================
[1]LTE2465_A_f_3_intra_eNB_reestablishment_between_CSG_cells_with_... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 3 intra eNB reestablishme... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 4 intra eNB reestablishment from C...
==============================================================================
[1]LTE2465_A_f_4_intra_eNB_reestablishment_from_CSG_cell_to_nonCSG... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A f.LTE2465 A f AC 4 intra eNB reestablishme... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A f                                             | FAIL |
Suite setup failed:
No keyword with name 'Setup_for_robot' found.

Also suite teardown failed:
Several failures occurred:

1) No keyword with name 'Teardown_for_robot' found.

2) No keyword with name 'Teardown_for_robot_trg' found.

4 critical tests, 0 passed, 4 failed
4 tests total, 0 passed, 4 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_g': Initializing test library 'LTE2465.resources.LTE2465_A_f_common.LTE2465_A_f_common' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_f_common.py", line 14, in __init__
    super(LTE2465_A_f_common, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A g
==============================================================================
LTE2465.Tests.LTE2465 A g.LTE2465 A g AC 1 inter eNB reestablishment from n...
==============================================================================
[1]LTE2465_A_g_AC_1_inter_eNB_reestablishment_from_non_CSG_neighbo... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A g.LTE2465 A g AC 1 inter eNB reestablishme... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A g.LTE2465 A g AC 3 inter eNB reestablishment from C...
==============================================================================
[1]LTE2465_A_g_AC_3_inter_eNB_reestablishment_from_CSG_cell_to_CSG... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A g.LTE2465 A g AC 3 inter eNB reestablishme... | FAIL |
Parent suite setup failed:
No keyword with name 'Setup_for_robot' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A g                                             | FAIL |
Suite setup failed:
No keyword with name 'Setup_for_robot' found.

2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
LTE2465.Tests.LTE2465 A h
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_h/LTE2465_A_h_AC_1_Inclusion_of_CSG_Id_in_S1AP_eNBConfigurationUpdate.robot': Initializing test library 'LTE2465.resources.LTE2465_A_h_AC_1.LTE2465_A_h_AC_1' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_h_AC_1.py", line 13, in __init__
    super(LTE2465_A_h_AC_1, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A h.LTE2465 A h AC 1 Inclusion of CSG Id in S1AP eNBC...
==============================================================================
[1]LTE2465_A_h_Inclusion_of_CSG_Id_in_S1_eNBConfigurationUpdate       | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A h.LTE2465 A h AC 1 Inclusion of CSG Id in ... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/home/ute/virtualenvs/ute/lib/python2.7/site-packages/Crypto/Util/number.py:57: PowmInsecureWarning: Not using mpz_powm_sec.  You should rebuild using libgmp >= 5 to avoid timing attack vulnerability.
  _warn("Not using mpz_powm_sec.  You should rebuild using libgmp >= 5 to avoid timing attack vulnerability.", PowmInsecureWarning)

/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_A_h/LTE2465_A_h_AC_2_Exclusion_of_CSG_Id_in_S1AP_eNBConfigurationUpdate.robot': Initializing test library 'LTE2465.resources.LTE2465_A_h_AC_2.LTE2465_A_h_AC_2' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_A_h_AC_2.py", line 12, in __init__
    super(LTE2465_A_h_AC_2, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 A h.LTE2465 A h AC 2 Exclusion of CSG Id in S1AP eNBC...
==============================================================================
[1]LTE2465_A_h_Exclusion_of_CSG_Id_in_S1_eNBConfigurationUpdate       | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 A h.LTE2465 A h AC 2 Exclusion of CSG Id in ... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 A h                                             | FAIL |
2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
LTE2465.Tests.LTE2465 B a
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_B_a/LTE2465_B_a_2_Incoming_S1_Handover_to_CSG_cell_with_CSGMembershipStatus_set_to_member.robot': Initializing test library 'LTE2465.resources.LTE2465_B_a_AC_2.LTE2465_B_a_AC_2' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_B_a_AC_2.py", line 14, in __init__
    super(LTE2465_B_a_AC_2, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 B a.LTE2465 B a 2 Incoming S1 Handover to CSG cell wi...
==============================================================================
[1]LTE2465_B_a_Incoming_S1_HO_to_CSG_cell_with_status_member          | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 B a.LTE2465 B a 2 Incoming S1 Handover to CS... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_B_a/LTE2465_B_a_3_Incoming_S1_Handover_Failure_to_CSG_cell_CSGMembershipStatus_set_to_non_member.robot': Initializing test library 'LTE2465.resources.LTE2465_B_a_AC_3.LTE2465_B_a_AC_3' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_B_a_AC_3.py", line 14, in __init__
    super(LTE2465_B_a_AC_3, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 B a.LTE2465 B a 3 Incoming S1 Handover Failure to CSG...
==============================================================================
[1]LTE2465_B_a_Incoming_S1_HO_Failure_to_CSG_cell_not_member          | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 B a.LTE2465 B a 3 Incoming S1 Handover Failu... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 B a                                             | FAIL |
2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
LTE2465.Tests.LTE2465 B b
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_B_b/LTE2465_B_b_1_Incoming_S1_Handover_to_CSG_cell_emergency_call_csgMembershipsStatus_set_to_non_member.robot': Initializing test library 'LTE2465.resources.LTE2465_B_b_AC_1.LTE2465_B_b_AC_1' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_B_b_AC_1.py", line 16, in __init__
    super(LTE2465_B_b_AC_1, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 B b.LTE2465 B b 1 Incoming S1 Handover to CSG cell em...
==============================================================================
[1]LTE2465_B_b_Incoming_S1_HO_to_CSG_cell_with_status_not_member      | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 B b.LTE2465 B b 1 Incoming S1 Handover to CS... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_B_b/LTE2465_B_b_4_Incoming_S1_Handover_Failure_to_CSG_cell_CSGId_do_not_match.robot': Initializing test library 'LTE2465.resources.LTE2465_B_b_AC_4.LTE2465_B_b_AC_4' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_B_b_AC_4.py", line 14, in __init__
    super(LTE2465_B_b_AC_4, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 B b.LTE2465 B b 4 Incoming S1 Handover Failure to CSG...
==============================================================================
[1]LTE2465_B_b_Incoming_S1_HO_Failure_to_CSG_cell_incorrect_CSGId     | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 B b.LTE2465 B b 4 Incoming S1 Handover Failu... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
/usr/bin/xterm Xt error: Can't open display:
/usr/bin/xterm:  DISPLAY is not set
[ ERROR ] Error in file '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/tests/LTE2465_B_b/LTE2465_B_b_5_Incoming_S1_Handover_Failure_to_CSG_cell_emergency_call_CSGId_not_included.robot': Initializing test library 'LTE2465.resources.LTE2465_B_b_AC_5.LTE2465_B_b_AC_5' with no arguments failed: ErrTafNoRpc: No RPC towards TAF server has been created and registered under name 'taf_server'
Traceback (most recent call last):
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465_B_b_AC_5.py", line 16, in __init__
    super(LTE2465_B_b_AC_5, self).__init__()
  File "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTE2465/resources/LTE2465.py", line 31, in __init__
    ruff.init(rpc_connection_name='taf_server', port=9854, host='localhost')
  File "/home/ute/auto/ruff/ruff/__init__.py", line 22, in init
    TMgr.set_default_rpc(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/testmanager.py", line 238, in set_default_rpc
    self.rpc = ruff.registry.rpc_client(rpc_connection_name)
  File "/home/ute/auto/ruff/ruff/registry.py", line 89, in rpc_client
    raise ErrTafNoRpc(rpc_connection_name)
LTE2465.Tests.LTE2465 B b.LTE2465 B b 5 Incoming S1 Handover Failure to CSG...
==============================================================================
[1]LTE2465_B_b_Incoming_S1_HO_Failure_to_CSG_cell_without_CSGId       | FAIL |
Parent suite setup failed:
No keyword with name 'setup' found.
------------------------------------------------------------------------------
LTE2465.Tests.LTE2465 B b.LTE2465 B b 5 Incoming S1 Handover Failu... | FAIL |
Suite setup failed:
No keyword with name 'setup' found.

Also suite teardown failed:
No keyword with name 'teardown' found.

1 critical test, 0 passed, 1 failed
1 test total, 0 passed, 1 failed
==============================================================================
LTE2465.Tests.LTE2465 B b                                             | FAIL |
3 critical tests, 0 passed, 3 failed
3 tests total, 0 passed, 3 failed
==============================================================================
LTE2465.Tests                                                         | FAIL |
26 critical tests, 0 passed, 26 failed
26 tests total, 0 passed, 26 failed
==============================================================================
LTE2465                                                               | FAIL |
26 critical tests, 0 passed, 26 failed
26 tests total, 0 passed, 26 failed
==============================================================================
Output:  /home/ute/logs/tl99_test_2015-08-31_12-45-33/output.xml
Log:     /home/ute/logs/tl99_test_2015-08-31_12-45-33/log.html
Report:  /home/ute/logs/tl99_test_2015-08-31_12-45-33/report.html
 - 12:46:39 31/08/2015 -
Elapsed time: 00:01:04.2
+ sshpass -p Motorola scp -r /home/ute/logs/tl99_test_2015-08-31_12-45-33 ltebox@10.83.200.35:public_html/logs/
+ rm -rf /home/ute/logs/tl99_test_2015-08-31_12-45-33
Notifying upstream projects of job completion
Finished: SUCCESS
"""

output2 = """
Started by user Paweł Nogieć
[EnvInject] - Loading node environment variables.
Building remotely on tl99_test in workspace /home/ute/workspace/test_on_tl99_test
[test_on_tl99_test] $ /bin/sh -xe /tmp/hudson8826255891226937753.sh
+ . /home/ute/virtualenvs/ute/bin/activate
+ deactivate nondestructive
+ unset pydoc
+ [ -n  ]
+ [ -n  ]
+ [ -n  -o -n  ]
+ [ -n  ]
+ unset VIRTUAL_ENV
+ [ ! nondestructive = nondestructive ]
+ VIRTUAL_ENV=/home/ute/virtualenvs/ute
+ export VIRTUAL_ENV
+ _OLD_VIRTUAL_PATH=/opt/ute/python/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games:/opt/ute/jython/bin
+ PATH=/home/ute/virtualenvs/ute/bin:/opt/ute/python/bin:/usr/local/bin:/usr/bin:/bin:/usr/bin/X11:/usr/games:/opt/ute/jython/bin
+ export PATH
+ [ -n  ]
+ [ -z  ]
+ _OLD_VIRTUAL_PS1=$
+ [ x != x ]
+ basename /home/ute/virtualenvs/ute
+ [ ute = __ ]
+ basename /home/ute/virtualenvs/ute
+ PS1=(ute)$
+ export PS1
+ alias pydoc=python -m pydoc
+ [ -n  -o -n  ]
+ python /home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/CRT/ivk_pybot.py -S /home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTEXYZ -c /home/ute/moj_config.yaml -L DEBUG -d /home/ute/logs/tl99_test_2015-09-02_08-05-00
 - 08:05:03 02/09/2015 -
==============================================================================
LTEXYZ
==============================================================================
LTEXYZ.Tests
==============================================================================
LTEXYZ.Tests.LTEXYZ-a-1
==============================================================================
<<<<<<< HEAD                                                          | FAIL |
Test case contains no keywords.
------------------------------------------------------------------------------
=======                                                               | FAIL |
Test case contains no keywords.
------------------------------------------------------------------------------
LTEXYZ.Tests.LTEXYZ-a-1                                               | FAIL |
2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
LTEXYZ.Tests                                                          | FAIL |
2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
LTEXYZ                                                                | FAIL |
2 critical tests, 0 passed, 2 failed
2 tests total, 0 passed, 2 failed
==============================================================================
Output:  /home/ute/logs/tl99_test_2015-09-02_08-05-00/output.xml
Log:     /home/ute/logs/tl99_test_2015-09-02_08-05-00/log.html
Report:  /home/ute/logs/tl99_test_2015-09-02_08-05-00/report.html
 - 08:05:53 02/09/2015 -
Elapsed time: 00:00:50.1
+ sshpass -p Motorola scp -r /home/ute/logs/tl99_test_2015-09-02_08-05-00 ltebox@10.83.200.35:public_html/logs/
+ rm -rf /home/ute/logs/tl99_test_2015-09-02_08-05-00
Notifying upstream projects of job completion
Finished: SUCCESS
"""
# import re
#
# import datetime
# # # print time.gmtime()
# add = '2015-08-31 10:48:22.429329'
# end = '2015-08-31 15:48:22.429329'
# # print datetime.datetime.utcnow()
# add = datetime.datetime.strptime(add.split('.')[0],"%Y-%m-%d %H:%M:%S")
# end = datetime.datetime.strptime(end.split('.')[0],"%Y-%m-%d %H:%M:%S")
#
# print end.replace(hour=end.hour+2)


# olddict = {'a' : 'b', 'c' : 'd', 'e' : 'f', 'g' : 'h', 'i' : 'j', 'k' : 'l'}
# # newdict = olddict.copy()
# # newdict['a'] = 'f'
# # print "old = \n{}".format(olddict)
# # print "new = \n{}".format(newdict)
# for record in olddict.keys():
#     if record == 'g':
#         olddict.pop(record)
# print olddict



# a = 0
# for i in range(500):
#     if a%5 == 0:
#         print a
#     a += 1

# import json
# name="testing_testing"
# suite = "LTE1"
# with open(name, 'rb+') as fff:
#     lines = fff.readlines()
#     fff.seek(0)
#     fff.truncate(0)
#     for line in lines:
#         if suite in json.loads(line):
#             lines.remove(line)
#     [fff.writelines('{}\n'.format(json.dumps(json.loads(line)))) for line in lines]
import json
# from server_reservation_dispatcher.utilities.TL_map import TL_map
TL_map = []
TL_map.append({'tl99_test' : 'wmp-tl99.lab0.krk-lab.nsn-rdnet.net'})
TL_map.append({'TL99' : 'wmp-tl99.lab0.krk-lab.nsn-rdnet.net'})
TL_map.append({'TL63' : 'wmp-tl63.lab0.krk-lab.nsn-rdnet.net'})
TL_map.append({'TL88' : 'iav-kra-tl088.lab0.krk-lab.nsn-rdnet.net'})

path = os.path.join('.','utilities','TL_name_to_address_map')

'''
with open(path, 'wb') as fff:
    for TL in TL_map:
        fff.writelines('{}\n'.format(json.dumps(TL)))
'''

TLname = "TL1"
with open("pliczek", 'wb') as output:
    TL = ["TL15", "TL99", "TL33"]
    for tl in TL:
        output.write('{}\n'.format(tl))

with open("/home/ute/PycharmProjects/projekty/Internship-15/_jenkins/server/pliczek", "rb+") as fff:
    # blacklist = []
    # a = [line.strip() for line in fff.readlines() if line.strip() == TLname]
    lines = fff.readlines()
    fff.seek(0)
    fff.truncate(0)
    [fff.writelines('{}'.format(line)) for line in lines if not line.strip() == TLname]
    # [blacklist.append(line) for line in fff.readlines() if not line.strip() == TLname]

    # [fff.writelines('{}'.format(line)) for line in blacklist]



#
# with open(path, 'rb+') as fff:
#     TL_map = {}
#     for lines in fff.readlines():
#         if not lines == '':
#             TL_map.update(json.loads(lines))
#     if not TLname in TL_map:
#         TL_map[TLname] = "jakis addr"
#
#     fff.seek(0)
#     fff.truncate(0)
#
#     for TLname in TL_map:
#         print TLname
#         fff.writelines(json.dumps({TLname : TL_map[TLname]}) + "\n")
    '''
    _found = False
    for v in lines:
        if TLname in v:
            _found = True
    if not _found:
            lines.append({TLname : 'addr'})

    print [line for line in lines]
    '''
# if not os.path.exists(path):
#     os.mknod(path)
# TL_map = []

# with open(path, "rb+") as TL_map_file:
#     for line in TL_map_file:
#         TL_map.append(json.loads(line))
#     if not TLname in TL_map:
#         print "tak"


# TL_map.update({'TL99' : "jakis_addr"})
# TL_map.
# print TL_map


"""
{"IAV_WRO_CLOUD1001": {"job": "", "id": 75891, "cloud": "CLOUD_F"}}
{"IAV_WRO_CLOUD116": {"job": "", "id": 75924, "cloud": "CLOUD_F"}}
{"IAV_WRO_CLOUD1004": {"job": "", "id": 75962, "cloud": "CLOUD_F"}}
"""


# import datetime
#
#
# def from_unicode_to_datetime(unicode):
#     date = datetime.datetime.strptime(unicode.split('.')[0],"%Y-%m-%d %H:%M:%S")
#     return date
#
#
# def from_datetime_to_unicode(date):
#     unicode = u'{}'.format(date.strftime("%Y-%m-%d %H:%M:%S"))
#     return unicode
#
# unicode = u"2015-09-10 05:36:17.162139"
#
# date = from_unicode_to_datetime(unicode)
# print date.__class__
# uni = from_datetime_to_unicode(date)
# print uni.__class__

#
# lines = {'LTE1' : 3,
#          'LTE2' : 5}

# with open(name, 'wb') as fff:
#     fff.seek(0)
#     fff.truncate(0)
#     for record in lines:
#         fff.writelines(json.dumps({record : lines[record]}) + "\n")
# #
#
#
# def write_new(suite):
#     with open(name, 'rb+') as fff:
#         _found = False
#         to_write = []
#         for line in fff.readlines():
#             line = json.loads(line.strip())
#             if suite in line:
#                 _found = True
#                 line[suite] += 1
#                 to_write.append(line)
#             else:
#                 to_write.append(line)
#         if not _found:
#             to_write.append({suite : 1})
#         fff.seek(0)
#         fff.truncate(0)
#         [fff.writelines('{}\n'.format(json.dumps(line))) for line in to_write]
#
# suite = "LTE3"
# write_new(suite)



        # else:
        #     print "n"
        #     to_write.append({suite : 1})
        #
        # fff.writelines(json.dumps(line))

        # for test in line:
        # print test
        #     print line
        # line = json.loads(lines)
        # for test in line:
        #     if line[test]:
        #         line[test] += 1
        #
        # fff.writelines(json.dumps({test : line[test]}) + "\n")






# import datetime
# name="testing_testing"
# import tl_reservation
# reserv = tl_reservation.TestLineReservation(74819)
# add_date = reserv.get_reservation_details()['add_date']
# print add_date
# TLadd_date = datetime.datetime.strptime(add_date.split('.')[0],"%Y-%m-%d %H:%M:%S")
# print TLadd_date
# now = datetime.datetime.utcnow()
# print now
# if isinstance(now, datetime.datetime):
#     print "tak"
#
# import json
# print (now-TLadd_date).total_seconds()
#
# TLadd_date = TLadd_date.strftime("%Y-%m-%d %H:%M:%S")
# print TLadd_date
# if isinstance(TLadd_date, str):
#     print "jest str"
# a = {'add_date' : TLadd_date}
# print a['add_date'].__class__
# with open(name,"wb") as bbb:
#     bbb.writelines(json.dumps(a))
#
# with open(name, "rb") as bbb:
#     for line in bbb.readlines():
#         add_date = json.loads(line)
#
# if isinstance(add_date['add_date'], str):
#     print "tez str"
# else:
#     print add_date['add_date'].__class__
#     print "co to?"
#
# add_date['add_date'] = datetime.datetime.strptime(add_date['add_date'], "%Y-%m-%d %H:%M:%S")
# print add_date['add_date'] - now


# try:
#     os.mknod(name)
# except:
#     pass
# reservations_dictionary = {}
# TLinfoo = []
# TLinfoo.append({u'status': 2, u'ute_build': u'1.0', u'add_date': u'2015-09-08 05:58:34.385475',
#           u'testline': {u'address': u'10.42.48.81', u'site': u'Wroclaw',
#                         u'name': u'IAV_WRO_CLOUD103'},
#           u'sysimage_build': u'utevm_debian7_64bit_201507271546.qcow2.tar.gz',
#           u'robotlte_revision': u'HEAD', u'enb_build': u'FL15A_ENB_0107_001114_000000',
#           u'testline_type': u'CLOUD_F', u'id': 74797, u'user': u'app_lmts'})
# TLinfoo.append({u'status': 2, u'ute_build': u'1.0', u'add_date': u'2015-09-08 05:57:28.294966',
#            u'testline': {u'address': u'10.42.48.82', u'site': u'Wroclaw',
#                          u'name': u'IAV_WRO_CLOUD104'},
#            u'sysimage_build': u'utevm_debian7_64bit_201507271546.qcow2.tar.gz',
#            u'robotlte_revision': u'HEAD', u'enb_build': u'FL15A_ENB_0107_001114_000000',
#            u'testline_type': u'CLOUD_F', u'id': 74796, u'user': u'app_lmts'})
#
# for TLinfo in TLinfoo:
#     TLname = TLinfo['testline']['name']
#     TLadd_date = datetime.datetime.strptime(TLinfo['add_date'].split('.')[0],"%Y-%m-%d %H:%M:%S")
# #TLend_date = datetime.datetime.strptime(TLinfo['end_date'].split('.')[0],"%Y-%m-%d %H:%M:%S")
#     # print TLname
#     ID = TLinfo['id']
#     TLend_date = TLadd_date.replace(hour=TLadd_date.hour + 8)
#     reservations_dictionary[TLname] = {'id' : ID,
#                                           'job' : '',
#                                           'add_date' : TLadd_date,
#                                           'end_date' : TLend_date,
#                                           'was_extended' : False
#                                           }
# # print reservations_dictionary['IAV_WRO_CLOUD104']['add_date'].strftime("%Y-%m-%d %H:%M:%S")
# # print reservations_dictionary
# import json
# tmp_dictionary = reservations_dictionary.copy()
# with open(name, 'wb') as backup:
#     for TLname in tmp_dictionary:
#         tmp_dictionary[TLname]['add_date'] = tmp_dictionary[TLname]['add_date'].strftime("%Y-%m-%d %H:%M:%S")
#         tmp_dictionary[TLname]['end_date'] = tmp_dictionary[TLname]['end_date'].strftime("%Y-%m-%d %H:%M:%S")
#         # TLname['add_date'] = TLname['add_date'].strftime("%Y-%m-%d %H:%M:%S")
#         # TLname['end_date'] = TLname['end_date'].strftime("%Y-%m-%d %H:%M:%S")
#         # print {TLname : tmp_dictionary[TLname]}
#         backup.writelines(json.dumps({TLname : tmp_dictionary[TLname]}) + "\n")
#         # json.dump({TLname : tmp_dictionary[TLname]},backup)
# tmp_dict = {}
# with open(name, 'rb') as backup:
#     for line in backup.readlines():
#         tmp2_dict = json.loads(line)
#         tmp_dict.update(tmp2_dict)
#
# print tmp_dict
# for TLname in tmp_dict:
#     print tmp_dict[TLname]

#
# for TLname in tmp2_dict:
#     print tmp2_dict[TLname]

# # print datetime.timedelta(end-add)
# tdelta = datetime.datetime.utcnow()-add
# # print tdelta
# # print tdelta.total_seconds()
# # print tdelta.date().min

# if (datetime.datetime.utcnow()-add).total_seconds() > 60*30:
#     print "tak"
# else:
#     print "nie"
#
#



# print os.path.join("cos","dalej")

# lista = {
#     "cos" : {
#         "tam" : 'a'
#     },
#     "dalej" : {
#         "tam" : 'b'},
#     'x' : {
#         "tam" : None}
#     }
#
# for l in lista:
#     if not lista[l]['tam']:
#         print l




# import paramiko
# SSHClient = paramiko.SSHClient()
# SSHClient.load_system_host_keys()
# SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# SSHClient.connect('wmp-tl99.lab0.krk-lab.nsn-rdnet.net', username='ute', password='ute')
# SFTP = SSHClient.open_sftp()
# file = SFTP.file("/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/LTEXYZ/tests/LTEXYZ-a-1.robot","r+")
# print file.readlines()


# for _ in range(10):
#     try:
#         print "cos" #os.remove(path_with_filename)
#         break
#     except:
#         time.sleep(0.1)

# start = time.time()
# try:
#     os.mknod('pliczek')
# except:
#     pass
# stop = time.time()
# print stop-start
#
# start = time.time()
# if not os.path.exists('pliiczek'):
#     os.mknod('pliiczek')
# stop = time.time()
#
# print stop-start


#
# lista = [{'a' : 'b',
#           'c' : 'd',
#           'e' : 'f',
#           'g' : 'h'}]
# l2 = ['cos','ala','ma','kota']
#
# for l in l2:
#     print l2.index(l)
# # for a,b  in enumerate(lista):
# #    print a
# #    print b


#
# import re
# regex = r'\=\s(.*)\s\=\W*.*FAIL'
# test_name = "LTE2465"
# job_filenames_failed_tests=[]
# try:
#     matches = re.findall(regex,output2)
#
#     for match in matches:
#         match = re.sub(" +", "_", match)  #changing " " to "_" - pybot thinks it's the same, i don't
#         if match[-3:] == '...': match = match[:-3]  #cutting last "..."
#         elif match[-1:] == '_': match = match[:-1]    #cutting last "_"
#         try:
#             match = re.search('\w*\.Tests\.{}.*\.(.*)'.format(test_name), match).group(1)
#             job_filenames_failed_tests.append(match)
#         except:
#             try:
#                 match = re.search('\w*\.Tests\.(.*)', match).group(1)
#                 job_filenames_failed_tests.append(match)
#             except:
#                 match = re.search('\w*\.(.*)', match).group(1)
#                 job_filenames_failed_tests.append(match)
#         # logger.info("Regex found fails in output of {}".format(self.jenkins_info['job_name']))
# except:
#     pass
#     # logger.debug("Regex did not find fails in output of {}".format(self.jenkins_info['job_name']))
# finally:
#     print job_filenames_failed_tests
#     # self.job_filenames_failed_tests = job_filenames_failed_tests

#
# import jenkinsapi.api as j
#
# api = j.Jenkins('http://plkraaa-jenkins.emea.nsn-net.net:8080', username='nogiec', password='!salezjanierlz3!')
# api.build_job('test_on_tl99_test', params={})
#
#
# once = False
# while not once:
#     print "x"
#     time.sleep(1)










from os import walk
# directory = mypath = "/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/"
# fnames = []
# dnames = []
# dpath = []
# for (dirpath, dirnames, filenames) in walk(mypath):
#     fnames.extend(filenames)
#     dpath.append(dirpath)
#     dnames.append(dirnames)
#     break
# print fnames
# print dpath
# print dnames

# filenames_and_paths = []
# for root, dirs, files in os.walk(directory):
#     for file in files:
#         if file.endswith('.txt') or file.endswith('.robot'):
#             filenames_and_paths.append({'path' : root, 'filename' : file})
#
# for line in filenames_and_paths:
#     print line



# import re
# regex = r'\=\s(.*)\s\=\W*.*FAIL'
# matches = re.findall(regex,output2)
# for match in matches:
#     match = re.sub(" +", "_", match)  #changing " " to "_" - pybot thinks it's the same, i don't
#     # if match[-3:] == '...': match = match[:-3]
#     # if match[-1:] == '_': match = match[:-1]
#     print match
# try:
#     os.mknod("pliczek.txt")
# except:
#     pass
# with open("pliczek.txt","rb+") as fff:
#     lines = fff.readlines()
#     fff.seek(0)
#     fff.truncate()
#     for line in lines:
#         if line == "ala ma kota, 5 ":
#             fff.write("")
#         else:
#             fff.write(line)
import string
# import random
# if not os.path.exists("pliczek.txt"):
#     print "tak"
# else:
#     print "nie"
#
# alphabet = string.letters+string.digits
# ''.join(random.choice(alphabet) for _ in range(3))
# print alphabet




#
# a = ["cos", "tam"]
#
# for b in a:
#     print a.index(b)



####for supervisor testing
'''
from supervisor import supervisor
if __name__ == '__main__':
    import os
    from threading import Thread
    dir_list = []
    path = '/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/'
    [dir_list.append(dir) for dir in os.listdir(path) if os.path.isdir(os.path.join(path,dir))]

    """ ['LTE1819', 'LTE2351', 'LTE738', 'LTE1841', 'LTE2465', 'CRT', 'LTE1899', 'LTE2209',
    'LBT1558', 'LTE1905', 'LTE1879', 'LTEXYZ-new', 'LTE2275', 'LTE1638', 'LTEXYZ',
    'LBT2762_LBT2763', 'LTE1321', 'LTE1509', 'LTE2384', 'LTE2324', 'LTE1536', 'LTE648',
    'LTE2149', 'LTE1130', 'LTE1731', 'LTE1406', 'SHB', 'LTE1749', 'LTE1569', 'LTE1469',
    'LTE2161', 'LTE2014', 'LBT2989', 'LTE825', 'LBT2180', 'LTE2302']"""




    i = 0
    for dir in dir_list:
        thread1 = Thread(target=supervisor, args=[i,
            {
                'testline_type' : 'CLOUD_F',
                'duration' : 600
            },
            {},
            {
                'parameters' :
                    {
                        'name' : dir
                    }
            },
            None,
            68880])
        i += 1
        thread1.start()
        thread1.join()


'''















# # def signal_SIGINT_handler(_signo, frame):   #nowa obsluga SIGINT
# #     try:
# #         print "Dziecko zlapalo SIGINT. koncze dzialanie"
# #     except:
# #         pass
# #     finally:
# #         sys.exit(0)
#
# # def Event():
# #
# #     print "rozumiem, koncze"
# #     sys.exit(1)
#
# _readyy = None
# def signal_SIGINT_handler(_signo, frame):
#     try:
#         if _readyy.is_set():
#             print "koncze"
#     except:
#         pass
#     finally:
#         sys.exit(1)
#
#
# def main(i, _ready, dict):
#     # signal.signal(signal.SIGINT, signal_SIGINT_handler)
#     dict[i] = os.getpid()
#     # print os.getgid()
#     # os.setgid(1001)
#     # signal.signal(signal.SIGINT, signal_SIGINT_handler)
#     global _readyy
#     _readyy = _ready
#     while True:
#         print "dziecko {}, jeszcze nie".format(i)
#         time.sleep(2)
#     # while not _ready.is_set():
#     #     print "dziecko {}, jeszcze nie".format(i)
#     #     time.sleep(2)
#     # print "koniec {}".format(i)
#         # _ready.wait()
#         # event = Event()
#         # while not event.is_set():
#         # print "tu dziecko, koncze"
#         # time.sleep(2)
#         # break
#         # event = Event()
#         # event.wait()
#         # if event.is_set:
#         #     Event()
