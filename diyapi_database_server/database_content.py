# -*- coding: utf-8 -*-
"""
database_content.py

DatabaseContent, with marshalling and unmarshalling code
"""
from collections import namedtuple
import struct

from diyapi_tools.marshalling import marshall_string, unmarshall_string

# I - format-version
# ? - is_tombstone
# d - timestamp
# I - version_number
# B - segment_number
# I - segment size
# I - segment count
# Q - total_size
# L - adler32
#16s- md5 
# H - userid
# H - groupid
# H - permissions
_content_template = "I?dIBIIQL16sHHH"
_content_template_size = struct.calcsize(_content_template)
_current_format_version = 1

create_content =  namedtuple(
    "DatabaseContent", [
        "format_version",
        "is_tombstone", 
        "timestamp", 
        "version_number",
        "segment_number", 
        "segment_count",
        "segment_size", 
        "total_size", 
        "adler32",
        "md5",
        "userid",
        "groupid",
        "permissions",
        "file_name",
    ]
)

def factory(**kwdargs):
    return create_content(
        format_version = _current_format_version,
        is_tombstone = kwdargs["is_tombstone"], 
        timestamp = kwdargs["timestamp"], 
        version_number = kwdargs["version_number"],
        segment_number = kwdargs["segment_number"], 
        segment_count = kwdargs["segment_count"],
        segment_size = kwdargs["segment_size"],
        total_size = kwdargs["total_size"], 
        adler32 = kwdargs["adler32"],
        md5 = kwdargs["md5"],
        file_name = kwdargs["file_name"],
        userid = 0,
        groupid = 0,
        permissions = 0
    )

def create_tombstone(timestamp, version_number, segment_number):
    """create a 'tombstone' database entry with a specified timestamp"""
    return create_content(
        format_version = _current_format_version,
        is_tombstone = True, 
        timestamp = timestamp, 
        version_number = version_number,
        segment_number = segment_number, 
        segment_count = 0,
        segment_size = 0 ,
        total_size = 0, 
        adler32 = 0,
        md5 = "",
        file_name = "",
        userid = 0,
        groupid = 0,
        permissions = 0
    )

def marshall(content):
    """
    return a string of marshalled content
    encode the segment number in the first byte
    """
    packed_content = struct.pack(
        _content_template,
        content.format_version & 0xFFFF,
        content.is_tombstone & 0xFF, 
        content.timestamp, 
        content.version_number & 0xFFFFFFFF, 
        content.segment_number & 0xFF,
        content.segment_count & 0xFFFFFFFF,
        content.segment_size & 0xFFFFFFFF, 
        content.total_size, 
        content.adler32 & 0xFFFFFFFF,
        content.md5,
        content.userid & 0xFFFF,
        content.groupid & 0xFFFF,
        content.permissions & 0xFFFF
    )
    packed_file_name = marshall_string(content.file_name)
    return "".join([packed_content, packed_file_name, ])

def unmarshall(data, pos):
    """
    unmarshall DatabaseContent tuple
    return (DatabaseContent, pos)
    with pos pointing one character after the marshalled tuple
    """
    content = struct.unpack(
        _content_template, data[pos:pos+_content_template_size]
    )
    assert content[0] == _current_format_version, content
    pos += _content_template_size
    (file_name, pos, ) = unmarshall_string(data, pos)
    total_content = list(content)
    total_content.append(file_name)
    return (create_content._make(total_content), pos)

