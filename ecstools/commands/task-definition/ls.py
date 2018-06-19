import click
import sys

from botocore.exceptions import ClientError

import ecstools.lib.utils as utils


@click.command(short_help='List tasks definitions families / revisions')
@click.argument('name', required=False)
@click.option('-n', '--num', type=int, default=3, help='Number of results')
@click.option('-A', '--arn', is_flag=True, help='Show ARN')
@click.option('-R', '--repo', is_flag=True, help='Show repo URI for images')
@click.option('-D', '--no-details', is_flag=True, default=False, help='Disable revision details')
@click.pass_context
def cli(ctx, name, arn, num, no_details, repo):
    """List families / revisions

        |\b
        $ ecs def

        |\b
        $ ecs def <taks-definition-family>

        |\b
        $ ecs def <taks-definition-family>:<revision>
    """
    ecs = ctx.obj['ecs']

    if not name:
        print_task_definition_families(ecs)
    else:
        print_task_definition_revisions(ecs, name, arn, num, no_details, repo)


def print_task_definition_families(ecs):
    res = ecs.list_task_definition_families()
    for family in res['families']:
        click.echo(family)


def print_task_definition_revisions(ecs, name, arn, num, no_details, repo):
    # Task definition revision was specified
    if ':' in name:
        definitions = [name]
    else:
        res = ecs.list_task_definitions(
            familyPrefix=name,
            sort='DESC',
            maxResults=num
        )
        definitions = res['taskDefinitionArns']

    if not arn:
        definitions = map(lambda x: x.split('/')[-1], definitions)

    for d in definitions:
        if no_details:
            click.echo(d)
            continue
        print_task_definition_info(ecs, repo, d)


def print_task_definition_info(ecs, repo, td_name):
    td = utils.describe_task_definition(ecs, td_name)
    click.secho('%s cpu: %s memory: %s' % (td_name,
                                           td.get('cpu', '-'),
                                           td.get('memory', '-')
                                           ), fg='blue')
    print_containers_info(repo, td['containerDefinitions'])


def print_containers_info(repo, containers):
    for c in containers:
        # Include the repo URI if the repo flag is set
        image = (repo and c['image'] or c['image'].split('/')[-1])
        click.echo('  - %s %s %s %s' % (c['name'],
                                        c.get('cpu', '-'),
                                        c.get('memory', '-'),
                                        image))
