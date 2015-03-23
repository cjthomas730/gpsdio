"""
The schema definitions are very long and make reading gpsd_format/schema.py difficult
"""


import datetime


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def datetime2str(datetime_obj):

    """
    Convert a datetime object to a normalized Benthos timestamp

    Parameters
    ----------
    datetime_obj : datetime.datetime
        A loaded datetime object
    """

    return datetime_obj.strftime(DATETIME_FORMAT)


def str2datetime(string):

    """
    Convert a normalized Benthos timestamp to a datetime object

    Parameters
    ----------
    string : str
        String to convert
    """

    ms = string[20:-1]
    ms += "000000"[:6 - len(ms)]
    return datetime.datetime(
        int(string[:4]),
        int(string[5:7]),
        int(string[8:10]),
        int(string[11:13]),
        int(string[14:16]),
        int(string[17:19]),
        int(ms))

VERSIONS = {
    1.0: {
        'course': {
            'default': 0.0,
            'type': float,
            'units': 'degrees',
            'description': 'Course over ground - degrees from north',
            # TODO: Should -90 be a valid value?  Maybe `-90 < x` instead?
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 359 or x == 3600,
            'good': 3600,
            'bad': 360
        },
        'heading': {
            'default': 0.0,
            'type': float,
            'units': 'degrees',
            'description': 'True heading - degrees from north',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 359 or x == 511,
            'good': 511,
            'bad': -102
        },
        'lat': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'description': 'North/South coordinate in WGS84 degrees',
            'test': lambda x: isinstance(x, float) and -90 <= x <= 90 or x == 91,
            'good': 91,
            'bad': -100
        },
        'lon': {
            'default': 0.0,
            'type': float,
            'units': 'WGS84 degrees',
            'description': 'East/West coordinate in WGS84 degrees',
             # TODO: Should -180 be a valid value?  Maybe `-180 < x` instead?
             'test': lambda x: isinstance(x, float) and -180 <= x <= 180 or x == 181,
             'good': 181,
             'bad': -180.1
        },
        'mmsi': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Mobile Marine Service Identifier',
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 30,
            'good': '12345678902345678',
            'bad': 1234
        },
        'timestamp': {
            'default': '1970-01-01T00:00:00.0Z',
            'type': datetime.datetime,
            'import': str2datetime,
            'export': datetime2str,
            'units': 'N/A',
            'description': 'Datetime format: {}'.format(DATETIME_FORMAT)
        },
        'eta': {
            'default': '1970-01-01T00:00:00.0Z',
            'type': datetime.datetime,
            'import': str2datetime,
            'export': datetime2str,
            'units': 'N/A',
            'description': 'Datetime format: {}'.format(DATETIME_FORMAT)
        },
        # FIXME: Confusion over type 1 / type 18 sog/speed
        'sog': {
            'test': lambda x: isinstance(x, float) and 0 <= x <= 102.2 or x == 1022,
            'good': 1022,
            'bad': 103
        },
        'speed': {
            'default': 0.0,
            'type': float,
            'units': 'kn/h',
            'description': 'Speed over ground in nautical miles per hour',
            'test': lambda x: isinstance(x, float) and 0 <= x <= 102.2 or x == 1022,
            'good': 1022,
            'bad': 103
        },
        'status': {
            'default': 'Not defined',
            'type': str,
            'units': 'N/A',
            'description': 'Navigation status (e.g. at anchor, moored, aground, etc.)',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 16),
            'good': 2,
            'bad': -10
        },
        'turn': {
            'default': None,
            'null': True,
            'type': float,
            'units': 'degrees/min',
            'description': 'Rate of turn',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(-127, 129),
            'good': 125,
            'bad': -1000
        },
        'type': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'description': 'NMEA message code',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(1, 28),
            'good': 5,
            'bad': -1            
        },
        'shipname': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel name',
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 120,
            'good': 'good value',
            'bad': False
        },
        'shiptype': {
            'default': 0,
            'type': int,
            'units': 'N/A',
            'description': 'Vessel type',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 100),
            'good': 87,
            'bad': str
        },
        'shiptype_text': {
            'default': 'Unknown',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel type'
        },
        'callsign': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'Vessel callsign',
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 42,
            'good': 'good',
            'bad': 123
        },
        'destination': {
            'default': '',
            'type': str,
            'units': 'N/A',
            'description': 'UN/LOCODE or ERI terminal code'
        },
        'assigned': {
            'default': False,
            'type': bool,
            'units': 'N/A',
            'description': 'Assigned-mode flag',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 1,
            'bad': -33
        },
        'to_port': {
            'default': 0,
            'type': int,
            'units': 'meters',
            'description': 'Dimension to port',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 6,
            'good': 1,
            'bad': -34
        },
        'accuracy': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 0,
            'bad': 2
        },
        'ack_required': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'acks': {
            'default': [],
            'description': '',
            'type': list,
            'units': ''
        },
        'aid_type': {
            'default': 'Type of Aid to Navigation not specified',
            'description': '',
            'type': str,
            'units': ''
        },
        'ais_version': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Should always be 0 right now.  The other vals are reserved.
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1, 2, 3),
            'good': 2,
            'bad': True
        },
        'alt': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'alt_sensor': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'aton_status': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'band': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 0,
            'bad': 4
        },
        'band_a': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'band_b': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'channel_a': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'channel_b': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'class': {
            'default': 'AIS',
            'description': '',
            'type': str,
            'units': ''
        },
        'cs': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            # Not bool - state
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 0,
            'bad': 7
        },
        'dac': {
            'default': 1,
            'description': '',
            'type': int,
            'units': ''
        },
        'dest_mmsi': {
            'default': '',
            'description': '',
            'type': str,
            'units': ''
        },
        'dest_mmsi_a': {
            'default': '',
            'description': '',
            'type': str,
            'units': ''
        },
        'dest_mmsi_b': {
            'default': '',
            'description': '',
            'type': str,
            'units': ''
        },
        'dest_msg_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'device': {
            'default': 'stdin',
            'description': '',
            'type': str,
            'units': ''
        },
        'display': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            # Not bool - state
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 1,
            'bad': 'j'
        },
        'draught': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 < x <= 2 ** 8,
            'good': 1,
            'bad': 2 ** 8 + 1
        },
        'dsc': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 1,
            'bad': -45
        },
        'dte': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # TODO: Switch to a more Pythonic bool if this is actually bolean and not a status
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 0,
            'bad': 8
        },
        'duration_minutes': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'epfd': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 9),
            'good': 8,
            'bad': 10
        },
        'fid': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'imo': {
            'default': '',
            'description': '',
            'type': str,
            'units': '',
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 30,
            'good': 'value',
            'bad': True,
        },
        'increment1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'increment2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'increment3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'increment4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'interval_raw': {
            'default': 11,
            'description': '',
            'type': int,
            'units': ''
        },
        'link_id': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'mmsi_1': {
            'default': '',
            'description': '',
            'type': str,
            'units': ''
        },
        'mmsi_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'mode': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'msg22': {
            'default': True,
            'description': '',
            'type': bool,
            'units': '',
            # TODO: Switch to a more Pythonic bool?
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 0,
            'bad': -2
        },
        'msg_1_1': {
            'default': 5,
            'description': '',
            'type': int,
            'units': ''
        },
        'msg_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'msg_seq': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'name': {
            'default': '',
            'description': 'Aid-to-Navigation name',
            'type': str,
            'units': ''
        },
        'ne_lat': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': ''
        },
        'ne_lon': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': ''
        },
        'notice_type': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'notice_type_str': {
            'default': 'Undefined',
            'description': '',
            'type': str,
            'units': ''
        },
        'number1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'number2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'number3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'number4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'off_position': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'offset1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'offset2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'offset3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'offset4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'part_num': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'power': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'quiet': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'raim': {
            'default': False,
            'description': '',
            'type': bool,
            'units': '',
            # TODO: bool is more Pythonic if the field is actually boolean and not state
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 0,
            'bad': -2
        },
        'received_stations': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'repeat': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 2,
            'good': 4,
            'bad': -1
        },
        'retransmit': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'scaled': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'second': {
            'default': 60,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in range(0, 64),
            'good': 63,
            'bad': 64
        },
        'seqno': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_number': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_offset': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_offset_1_1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_offset_1_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_offset_2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'slot_timeout': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'spare4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'maneuver': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (1, 2),
            'good': 2,
            'bad': 3
        },
        'station_type': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'sub_areas': {
            'default': [],
            'description': '',
            'type': list,
            'units': ''
        },
        'sw_lon': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': ''
        },
        'sync_state': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'timeout1': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'timeout2': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'timeout3': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'timeout4': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'to_bow': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            # FIXME: This test is incorrect. value can not be > 511 according to AIS spec; check to_stern etc too
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 9,
            'good': 1,
            'bad': -1
        },
        'to_starboard': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 6,
            'good': 0,
            'bad': False
        },
        'to_stern': {
            'default': 0,
            'description': '',
            'type': int,
            'units': '',
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and 0 <= x <= 2 ** 9,
            'good': 0,
            'bad': tuple
        },
        'transmission_ctl': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'txrx': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'type_and_cargo': {
            'default': 0,
            'description': '',
            'type': int,
            'units': ''
        },
        'unit': {
            'default': True,
            'description': '',
            'type': bool,
            'units': ''
        },
        'virtual_aid': {
            'default': False,
            'description': '',
            'type': bool,
            'units': ''
        },
        'y2': {
            'default': 0.0,
            'description': '',
            'type': float,
            'units': ''
        },
        'zonesize': {
            'default': 3,
            'description': '',
            'type': int,
            'units': ''
        },


        # Our own columns
        'track': {
            'default': -1,
            'description': 'Track id for despoofed tracks',
            'type': int,
            'units': ''
        },
        'measure_new_score': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        'measure_coursestddev': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        'measure_speedstddev': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        'measure_speedavg': {
            'default': 0.0,
            'description': 'Score',
            'type': float,
            'units': ''
        },
        # FIXME: Provide types etc for these
        'radio': {
            # TODO: What will this value be?
            'test': lambda x: x is None,
            'good': None,
            'bad': False
        },
        'reserved': {
            'test': lambda x: x is None,
            'good': None,
            'bad': 1
        },
        'regional': {
            'test': lambda x: x is None,
            'good': None,
            'bad': -1
        },

        # Pulled from type 24 GPSD spec
        'partno': { # FIXME: WHich one of this and partnum is the correct field name?
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),
            'good': 0,
            'bad': -1
        },
        'vendorid': {
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 18,
            'good': 'this is a gooooooooood value',
            'bad': int
        },
        'model': {
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 4,
            'good': 'something',
            'bad': 333
        },
        'serial': {
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 20,
            'good': 'pawoeiras',
            'bad': -1
        },
        'mothership_mmsi': {
            'test': lambda x: isinstance(x, str) and len(x) <= 2 ** 30,
            'good': 'done ... finally ...',
            'bad': -200
        },

        # Pulled from type 27 GPSD spec
        'gnss': {
            'test': lambda x: isinstance(x, int) and not isinstance(x, bool) and x in (0, 1),  # Not bool - state
            'good': 0,
            'bad': 3
        }
    }
}
