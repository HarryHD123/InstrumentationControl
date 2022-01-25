from IClib import functions

def test_connect_instrument():

    assert functions.connect_instrument('TCPIP0::192.168.1.2::inst0::INSTR')