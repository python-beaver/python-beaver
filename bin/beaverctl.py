import click
import pdb

from beaver.utils import parse_args
from beaver.stubfactory import StubFactory
from beaver.config import BeaverConfig
from beaver.utils import setup_custom_logger, REOPEN_FILES



client = StubFactory.create_beaverctl_client()
args = parse_args()
logger = setup_custom_logger('beaverctl', args)

beaver_config = BeaverConfig(args, logger=logger)
beaverctl_socket_path = beaver_config.get('beaverctl_socket_path')

@click.group()
def cli():
    """Provides command line beaver monitor."""
    pass

@cli.command("backlog")
def queue_size():
    """Number of logs to be processed."""
    backlog = client.make_remote_call(method="get_queue_size")
    if backlog.is_error == False:
        error = backlog.get_error()
        click.echo("There was an error getting backlog data: ")
        click.echo(backlog.get_error())
    else:
        click.echo("The current backlog contains " + backlog.get_response() + \
        " events")

@cli.command("is-connected")
def get_connection_status():
    """Is beaver shipping logs."""
    status = client.make_remote_call(method="get_connection_status")
    #pdb.set_trace()
    if status.is_error == False:
        click.echo("There was an error getting connection status: ")
        click.echo(status.get_error())
    else:
        click.echo("The connection is " + 'connected' if status.get_response() \
          else 'disconected')
