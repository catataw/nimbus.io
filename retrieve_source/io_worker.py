# -*- coding: utf-8 -*-
"""
io_worker.py

One of a pool of io workers
"""
import logging
import os
import os.path
import sys
from threading import Event

import zmq

from tools.standard_logging import initialize_logging
from tools.zeromq_util import is_interrupted_system_call, \
        InterruptedSystemCall
from tools.process_util import set_signal_handler
from tools.event_push_client import EventPushClient, unhandled_exception_topic

from retrieve_source.internal_sockets import io_controller_router_socket_uri

_local_node_name = os.environ["NIMBUSIO_NODE_NAME"]
_log_path_template = "{0}/nimbusio_rs_io_worker_{1}_{2}_{3}.log"

def _send_work_request(dealer_socket, volume_name):
    """
    start the work cycle by notifying the controller that we are available
    """
    log = logging.getLogger("_send_initial_work_request")
    log.debug("sending initial request")
    message = {"message-type" : "ready-for-work",
               "volume-name"  : volume_name,}
    dealer_socket.send_json(message)

def _process_request(dealer_socket):
    """
    Wait for a reply to our last message from the controller.
    """
    log = logging.getLogger("_process_one_transaction")
    log.debug("waiting work request")
    try:
        request = dealer_socket.recv_json()
    except zmq.ZMQError as zmq_error:
        if is_interrupted_system_call(zmq_error):
            raise InterruptedSystemCall()
        raise
    assert dealer_socket.rcvmore

    segment_row = dealer_socket.recv_json()

def main():
    """
    main entry point
    returns 0 for normal termination (usually SIGTERM)
    """
    return_value = 0

    volume_name = sys.argv[1]
    worker_number = int(sys.argv[2])

    log_path = _log_path_template.format(os.environ["NIMBUSIO_LOG_DIR"], 
                                         volume_name,
                                         worker_number,
                                         _local_node_name)
    initialize_logging(log_path)
    log = logging.getLogger("main")
    log.info("program starts")

    halt_event = Event()
    set_signal_handler(halt_event)

    zeromq_context = zmq.Context()

    event_source_name = "rs_io_worker_{0}_{1}".format(volume_name, 
                                                      worker_number)
    event_push_client = EventPushClient(zeromq_context, event_source_name)

    dealer_socket = zeromq_context.socket(zmq.DEALER)
    dealer_socket.setsockopt(zmq.LINGER, 1000)
    log.debug("connecting to {0}".format(io_controller_router_socket_uri))
    dealer_socket.connect(io_controller_router_socket_uri)

    try:
        while not halt_event.is_set():
            _send_work_request(volume_name, dealer_socket)
            _process_request(dealer_socket)
    except InterruptedSystemCall:
        if halt_event.is_set():
            log.info("program teminates normally with interrupted system call")
        else:
            log.exception("zeromq error processing request")
            event_push_client.exception(unhandled_exception_topic,
                                        "Interrupted zeromq system call",
                                        exctype="InterruptedSystemCall")
            return_value = 1
    except Exception as instance:
        log.exception("error processing request")
        event_push_client.exception(unhandled_exception_topic,
                                    str(instance),
                                    exctype=instance.__class__.__name__)
        return_value = 1
    else:
        log.info("program teminates normally")
    finally:
        dealer_socket.close()
        event_push_client.close()
        zeromq_context.term()

    return return_value

if __name__ == "__main__":
    sys.exit(main())
