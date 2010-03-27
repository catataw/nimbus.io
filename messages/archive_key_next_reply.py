# -*- coding: utf-8 -*-
"""
archive_key_next_reply.py

ArchiveKeyNextReply message
"""
import struct

from tools.marshalling import marshall_string, unmarshall_string

# 32s - request-id 32 char hex uuid
# B   - result: 0 = success 
_header_format = "!32sB"
_header_size = struct.calcsize(_header_format)

class ArchiveKeyNextReply(object):
    """AMQP message to archive an entire key"""
   
    successful = 0
    error_invalid_duplicate = 1
    error_exception = 2
    error_out_of_sequence = 3

    def __init__(self, request_id, result, error_message=""):
        self.request_id = request_id
        self.result = result
        self.error_message = error_message

    @property
    def error(self):
        return self.result != ArchiveKeyNextReply.successful

    @classmethod
    def unmarshall(cls, data):
        """return a DatabaseKeyInsert message"""
        pos = 0
        request_id, result, = struct.unpack(
            _header_format, data[pos:pos+_header_size]
        )
        pos += _header_size

        if result == 0:
            return ArchiveKeyNextReply(request_id, result)

        (error_message, pos) = unmarshall_string(data, pos)

        return ArchiveKeyNextReply(
            request_id, result, error_message
        )

    def marshall(self):
        """return a data string suitable for transmission"""
        error_message_size = len(self.error_message)
        header = struct.pack(
            _header_format, 
            self.request_id, 
            self.result 
        )
        packed_error_message = marshall_string(self.error_message)
         
        return "".join([header, packed_error_message, ])
