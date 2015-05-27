"""
Commandline interface for `gpsdio`.
"""


import code
import datetime
import json
import logging
import os
import sys

import click
import six

import gpsdio
import gpsdio.drivers
import gpsdio.schema
import gpsdio.validate


logging.basicConfig()
logger = logging.getLogger('gpsdio_cli')


def _cb_key_val(ctx, param, value):

    """
    Some options like `-ro` take `key=val` pairs that need to be transformed
    into `{'key': 'val}`.  This function can be used as a callback to handle
    all options for a specific flag, for example if the user specifies 3 reader
    options like `-ro key1=val1 -ro key2=val2 -ro key3=val3` then `click` uses
    this function to produce `{'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}`.
    Parameters
    ----------
    ctx : click.Context
        Ignored
    param : click.Option
        Ignored
    value : tuple
        All collected key=val values for an option.
    Returns
    -------
    dict
    """

    output = {}
    for pair in value:
        if '=' not in pair:
            raise click.BadParameter("incorrect syntax for KEY=VAL argument: `%s'" % pair)
        else:
            key, val = pair.split('=')
            output[key] = val

    return output


@click.group()
@click.option(
    '--input-driver', metavar='NAME', default=None,
    help='Specify the input driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseDriver.by_name.keys()))
)
@click.option(
    '--output-driver', metavar='NAME', default=None,
    help='Specify the output driver.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseDriver.by_name.keys()))
)
@click.option(
    '--input-compression', metavar='NAME', default=None,
    help='Input compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseCompressionDriver.by_name.keys()))
)
@click.option(
    '--output-compression', metavar='NAME', default=None,
    help='Output compression format.  Normally auto-detected from file path.',
    type=click.Choice(list(gpsdio.drivers.BaseCompressionDriver.by_name.keys()))
)
@click.pass_context
def main(ctx, input_driver, output_driver, input_compression, output_compression):
    """
    A collection of tools for working with the GPSD JSON format (or the same format in a msgpack container)
    """

    ctx.obj = {
        'i_driver': input_driver,
        'o_driver': output_driver,
        'i_compression': input_compression,
        'o_compression': output_compression
    }


@main.command()
@click.argument("infile", metavar="INPUT_FILENAME")
@click.option(
    '--print-json', is_flag=True,
    help="Print serializable JSON instead of text"
)
@click.option(
    '--msg-hist', is_flag=True, default=False,
    help="Print a type histogram"
)
@click.option(
    '--mmsi-hist', is_flag=True, default=False,
    help="Print a MMSI histogram"
)
@click.option(
    '-v', '--verbose', is_flag=True,
    help="Print details on individual messages")
@click.pass_context
def validate(ctx, infile, print_json, verbose, msg_hist, mmsi_hist):

    """
    Print info about a GPSD format AIS/GPS file
    """

    if os.path.isdir(infile):
        files = [os.path.join(infile, name) for name in os.listdir(infile)]
    else:
        files = [infile]

    files.sort()

    stats = {}
    for name in files:
        logger.exception("Collecting stats for {infile} ...\n".format(infile=name))
        with gpsdio.open(name, "r", skip_failures=True, force_message=False) as f:
            if verbose:
                def error_cb(type, msg, exc=None, trace=None):
                    if exc:
                        logger.exception("%s: %s: %s: %s\n" % (name, type.title(), exc, msg))
                        if trace:
                            logger.exception("%s\n" % (trace,))
                    else:
                        logger.exception("%s: %s: %s\n" % (name, type.title(), msg))
            else:
                error_cb = None
            stats = gpsdio.validate.merge_info(stats, gpsdio.validate.collect_info(f, error_cb=error_cb))

    if print_json:
        for key, value in six.iteritems(stats):
            if isinstance(value, datetime.datetime):
                stats[key] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        stats['file'] = infile
        click.echo(json.dumps(stats) + "\n")
        sys.exit(0)
    else:
        click.echo("")
        click.echo("=== Report for %s ===" % infile)
        click.echo("  Number of rows: %s" % stats['num_rows'])
        click.echo("  Number of incomplete rows: %s" % stats['num_incomplete_rows'])
        click.echo("  Number of invalid rows: %s" % stats['num_invalid_rows'])
        click.echo("  All files are sorted: %s" % stats['is_sorted_files'])
        click.echo("  All rows are sorted: %s" % stats['is_sorted'])
        if stats['mmsi_declaration'] is not None:
            click.echo("  All rows match declared MMSI: %s" % stats['mmsi_declaration'])
        click.echo("  Number of unique MMSI's: %s" % len(stats['mmsi_hist']))
        click.echo("  Number of message types: %s" % len(stats['msg_type_hist']))
        click.echo("")
        click.echo("  X Min: %s" % stats['lon_min'])
        click.echo("  Y Min: %s" % stats['lat_min'])
        click.echo("  X Max: %s" % stats['lon_max'])
        click.echo("  Y Max: %s" % stats['lat_max'])
        click.echo("")
        if stats['min_timestamp'] is not None:
            _min_t = gpsdio.schema.datetime2str(stats['min_timestamp'])
        else:
            _min_t = None
        if stats['max_timestamp'] is not None:
            _max_t = gpsdio.schema.datetime2str(stats['max_timestamp'])
        else:
            _max_t = None
        click.echo("  Min timestamp: %s" % _min_t)
        click.echo("  Max timestamp: %s" % _max_t)
        if mmsi_hist:
            click.echo("")
            click.echo("  MMSI histogram:")
            for mmsi in sorted(stats['mmsi_hist'].keys()):
                click.echo("    %s -> %s" % (mmsi, stats['mmsi_hist'][mmsi]))
        if msg_hist:
            click.echo("")
            click.echo("  Message type histogram:")
            for msg_type in sorted(stats['msg_type_hist'].keys()):
                click.echo("    %s -> %s" % (msg_type, stats['msg_type_hist'][msg_type]))
        click.echo("")

    sys.exit(0)


@main.command()
@click.argument("infile", metavar="INPUT_FILENAME")
@click.argument("outfile", metavar="OUTPUT_FILENAME")
@click.pass_context
def convert(ctx, infile, outfile):

    """
    Converts between JSON and msgpack container formats
    """

    with gpsdio.open(infile) as reader:
        with gpsdio.open(outfile, 'w') as writer:
            for row in reader:
                writer.write(row)


@main.command()
@click.argument('infile', required=True)
@click.pass_context
def cat(ctx, infile):

    """
    Print messages to stdout as newline JSON.
    """

    with gpsdio.open(infile, driver=ctx.obj['i_driver'],
                     compression=ctx.obj['i_compression']) as src, \
            gpsdio.open('-', 'w', driver='NewlineJSON') as dst:
        for msg in src:
            dst.write(msg)


@main.command()
@click.argument('outfile', required=True)
@click.pass_context
def load(ctx, outfile):

    """
    Load newline JSON messages from stdin to a file.
    """

    with gpsdio.open('-', driver='NewlineJSON', compression=False) as src, \
            gpsdio.open(outfile, 'w', driver=ctx.obj['o_driver'],
                        compression=ctx.obj['o_compression']) as dst:
        for msg in src:
            dst.write(msg)


@main.command()
@click.argument('infile', required=True)
@click.option(
    '--no-ipython', 'use_ipython', is_flag=True, default=True,
    help="Don't use IPython, even if it is available."
)
@click.pass_context
def insp(ctx, infile, use_ipython):

    # A good idea borrowed from Fiona and Rasterio

    """
    Open a dataset in an interactive inspector.

    IPython will be used if it can be imported unless otherwise specified.

    Analogous to doing:

        \b
        >>> import gpsdio
        >>> with gpsdio.open(infile) as stream:
        ...     # Operations
    """

    header = os.linesep.join((
        "gpsdio %s Interactive Inspector Session (Python %s)"
        % (gpsdio.__version__, '.'.join(map(str, sys.version_info[:3]))),
        "Try `help(stream)` or `next(stream)`."
    ))

    with gpsdio.open(infile, driver=ctx.obj['i_driver'],
                     compression=ctx.obj['i_compression']) as src:

        scope = {
            'stream': src,
            'gpsdio': gpsdio
        }

        try:
            import IPython
        except ImportError:
            IPython = None

        if use_ipython and IPython is not None:
            IPython.embed(header=header, user_ns=scope)
        else:
            code.interact(header, local=scope)


@main.command()
@click.option(
    '--drivers', 'item', flag_value='drivers',
    help="List of registered drivers and their I/O modes."
)
@click.option(
    '--compression', 'item', flag_value='compression',
    help='List of registered compression drivers and their I/O modes.'
)
def env(item):

    """
    Information about the gpsdio environment.
    """

    if item == 'drivers':
        for name, driver in gpsdio.drivers.BaseDriver.by_name.items():
            click.echo("%s - %s" % (name, driver.io_modes))
    elif item == 'compression':
        for name, driver in gpsdio.drivers.BaseCompressionDriver.by_name.items():
            click.echo("%s - %s" % (name, driver.io_modes))
    else:
        raise click.BadParameter('A flag is required.')
