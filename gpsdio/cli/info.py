"""
gpsdio info
"""


from collections import OrderedDict
import logging
import json

import click

import gpsdio
import gpsdio.schema
import gpsdio.validate
from gpsdio.cli import options


logger = logging.getLogger('gpsdio')


@click.command(name='info')
@click.argument('infile')
@click.option(
    '--bounds', 'meta_member', flag_value='bounds',
    help="Print only the boundary coordinates as xmin, ymin, xmax, ymax.")
@click.option(
    '--count', 'meta_member', flag_value='count',
    help="Print only the number of messages in the datasource.")
@click.option(
    '--mmsi-hist', 'meta_member', flag_value='mmsi_histogram',
    help="Print only the MMSI histogram.")
@click.option(
    '--type-hist', 'meta_member', flag_value='type_histogram',
    help="Print only the type histogram.")
@click.option(
    '--field-hist', 'meta_member', flag_value='field_histogram',
    help="Print only the field histogram.")
@click.option(
    '--with-mmsi-hist', is_flag=True,
    help="Include a histogram of MMSI counts.")
@click.option(
    '--with-type-hist', is_flag=True,
    help="Include a histogram of message type counts.")
@click.option(
    '--with-field-hist', is_flag=True,
    help="Include a histogram of field names and message counts.")
@click.option(
    '--min-timestamp', 'meta_member', flag_value='min_timestamp',
    help="Print only the minimum timestamp.")
@click.option(
    '--max-timestamp', 'meta_member', flag_value='max_timestamp',
    help="Print only the maximum timestamp.")
@click.option(
    '--sorted', 'meta_member', flag_value='sorted',
    help="Print only whether or not the datasource is sorted by timestamp.")
@click.option(
    '--num-unique-mmsi', 'meta_member', flag_value='num_unique_mmsi',
    help="Print only the number of unique MMSI numbers.")
@click.option(
    '--num-unique-type', 'meta_member', flag_value='num_unique_type',
    help="Print only the number of unique message types.")
@click.option(
    '--num-unique-field', 'meta_member', flag_value='num_unique_field',
    help="Print only the number of unique fields.")
@click.option(
    '--with-all', is_flag=True,
    help="Print all available metrics.")
@click.option(
    '--sort-field', metavar='NAME', default='timestamp', show_default=True,
    help="Check if data is sorted by this field.  Output is placed in the 'sorted' key.")
@options.indent_opt
@options.input_driver
@options.input_driver_opts
@options.input_compression
@options.input_compression_opts
@click.pass_context
def info(
        ctx,
        infile, indent, meta_member, sort_field,
        with_mmsi_hist, with_type_hist, with_field_hist, with_all,
        input_driver, input_driver_opts, input_compression, input_compression_opts):

    """
    Print metadata about a datasource as JSON.

    Can optionally print a single item as a string.

    One caveat of this tool is that JSON does not support integer keys, which
    means that the keys of items like `type_histogram` and `mmsi_histogram`
    have been converted to a string when in reality they should be integers.
    Tools reading the JSON output will need account for this when parsing.
    """

    logger.setLevel(ctx.obj['verbosity'])
    logger.debug('Starting info')

    if meta_member == 'mmsi_histogram':
        with_mmsi_hist = True
    if meta_member == 'type_histogram':
        with_type_hist = True
    if meta_member == 'field_histogram':
        with_field_hist = True

    xmin = ymin = xmax = ymax = None
    ts_min = ts_max = None
    mmsi_hist = {}
    msg_typehist = {}
    field_hist = {}
    is_sorted = True
    prev_ts = None

    with gpsdio.open(
            infile,
            driver=input_driver,
            compression=input_compression,
            do=input_driver_opts,
            co=input_compression_opts,
            **ctx.obj['idefine']) as src:

        idx = 0  # In case file is empty
        for idx, msg in enumerate(src):

            # ts = msg.get('timestamp')
            x = msg.get('lon')
            y = msg.get('lat')
            mmsi = msg.get('mmsi')
            msg_type = msg.get('type')
            sort_val = msg.get(sort_field)

            for key in msg.keys():
                field_hist.setdefault(key, 0)
                field_hist[key] += 1

            if sort_val is not None:

                # Adjust min and max timestamp
                if ts_min is None or sort_val < ts_min:
                    ts_min = sort_val
                if ts_max is None or sort_val > ts_max:
                    ts_max = sort_val

                # Figure out if the data is sorted by time
                if prev_ts is None:
                    prev_ts = sort_val
                elif (sort_val and prev_ts) and sort_val < prev_ts:
                    is_sorted = False

            if x is not None and y is not None:

                # Adjust bounding box
                if xmin is None or x < xmin:
                    xmin = x
                if ymin is None or y < ymin:
                    ymin = y
                if xmax is None or x > xmax:
                    xmax = x
                if ymax is None or y > ymax:
                    ymax = y

            # Type histogram
            msg_typehist.setdefault(msg_type, 0)
            msg_typehist[msg_type] += 1

            # MMSI histogram
            mmsi_hist.setdefault(mmsi, 0)
            mmsi_hist[mmsi] += 1

    stats = {
        'bounds': (xmin, ymin, xmax, ymax),
        'count': idx + 1,
        'min_timestamp': gpsdio.validate.datetime2str(ts_min),
        'max_timestamp': gpsdio.validate.datetime2str(ts_max),
        'sorted': is_sorted,
        'num_unique_mmsi': len(set(mmsi_hist.keys())),
        'num_unique_type': len(set(msg_typehist.keys())),
        'num_unique_field': len(set(field_hist.keys()))
    }

    if with_all or with_mmsi_hist:
        stats['mmsi_histogram'] = OrderedDict(
            ((k, mmsi_hist[k]) for k in sorted(mmsi_hist.keys())))
    if with_all or with_type_hist:
        stats['type_histogram'] = OrderedDict(
            ((k, msg_typehist[k]) for k in sorted(msg_typehist.keys())))
    if with_all or with_field_hist:
        stats['field_histogram'] = OrderedDict(
            ((k, field_hist[k]) for k in sorted(field_hist.keys())))

    stats = OrderedDict((k, stats[k]) for k in sorted(stats.keys()))

    if meta_member:
        if isinstance(stats[meta_member], (tuple, list)):
            click.echo(" ".join((map(str, stats[meta_member]))))
        elif isinstance(stats[meta_member], (dict, bool)):
            click.echo(json.dumps(stats[meta_member], indent=indent))
        else:
            click.echo(stats[meta_member])
    else:
        click.echo(json.dumps(stats, indent=indent))
