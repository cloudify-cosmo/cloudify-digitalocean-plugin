# #######
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import digitalocean

from cloudify import ctx
from cloudify.decorators import operation
# from cloudify.exceptions import RecoverableError

from . import common


CREDENTIALS_FILE_PATHS = [
    os.path.join(os.path.expanduser('~'), '.cloudify', 'credentials'),
    os.path.join(os.sep, 'etc', 'cloudify', 'credentials')
]


# Allow, in plugin.yaml, to provide the number of retries and retry interval
# (and maybe logic) for an operation. This should be in Cloudify


@operation
def create(args, **_):
    """Create a droplet

    if existing resource provided:
        if the resource actually exists:
            use it
        else:
            if create if missing:
                create the resource
            else:
                fail since it doesn't exist but should
    else:
        assert quota if possible
        create resource even if one already exists of the same name(property)
        verify created
        use the created resource
    set the resource's context (the resource will have a uuid, instance_id, node_id, deployment_id and blueprint_id)  # NOQA
    set the resource's properties
    """
    # TODO: look for an available droplet of the same type if it exists
    # and use that instead if a property is provided where the user asks
    # to `find_existing_resource`

    # TODO: should this be abstracted?
    credentials = _get_credentials(args)

    droplet = _create_droplet(args, credentials)
    if not _droplet_created(droplet):
        ctx.abort_operation('Failed to create resource')
    _use_resource(droplet.id)
    _set_droplet_context()
    _set_droplet_properties(droplet)


@operation
def delete(args, **_):
    """Destroy a droplet

    if the resource wasn't created by us:
        if user asks to delete externally provisioned resources:
            delete resource
    else:
        get the resource
        delete it
        verify that it was deleted
    """
    credentials = _get_credentials(args)

    resource_id = ctx.instance.runtime_properties['resource_id']
    _delete_droplet(resource_id, credentials)


@operation
def stop(args, **_):
    """Shutdown a droplet

    get the resource
    stop it
    verify that it's stopped
    """
    credentials = _get_credentials(args)

    resource_id = ctx.instance.runtime_properties['resource_id']
    _stop_droplet(resource_id, credentials)
    # TODO: try power_off if shutdown is not successful


@operation
def start(args, **_):
    """Power a droplet on

    get the resource
    stop it
    verify that it's stopped
    """
    credentials = _get_credentials(args)

    resource_id = ctx.instance.runtime_properties['resource_id']
    _start_droplet(resource_id, credentials)


def _create_droplet(args, token):
    ctx.logger.info('Creating Droplet...')
    ctx.logger.debug('Droplet arguments: {0}'.format(args))

    droplet = digitalocean.Droplet(
        token=token,
        name=args.get('name', _generate_name()),
        region=args['region'],
        image=args['image'],
        size_slug=args['size_slug'],
        backups=args.get('backups', True))
    droplet.create()

    return droplet


def _delete_droplet(resource_id, credentials):
    ctx.logger.info('Destroying droplet...')
    droplet = _get_droplet(resource_id, credentials)
    if droplet:
        droplet.destroy()
        _assert_completed(droplet)
    if _get_droplet(resource_id, credentials):
        raise ctx.abort_operation('Droplet not destroyed')
    else:
        ctx.logger.info('Droplet destroyed successfully')


def _stop_droplet(resource_id, credentials):
    ctx.logger.info('Shutting droplet down...')
    droplet = _get_droplet(resource_id, credentials)
    if droplet:
        droplet.shutdown()
        _assert_completed(droplet)


def _start_droplet(resource_id, credentials):
    ctx.logger.info('Powering droplet on...')
    droplet = _get_droplet(resource_id, credentials)
    if droplet:
        droplet.power_on()
        _assert_completed(droplet)


def _use_resource(resource_id):
    ctx.logger.info('Using resource {0}...'.format(resource_id))
    ctx.instance.runtime_properties['resource_id'] = resource_id


def _get_droplet(resource_id, token):
    manager = digitalocean.Manager(token=token)
    for droplet in manager.get_all_droplets():
        if droplet.id == resource_id:
            return droplet
    return None


def _droplet_created(droplet, args):
    return _assert_completed(droplet)


def _set_droplet_context():
    ctx.logger.debug('Setting droplet context...')
    ctx.instance.runtime_properties['resource_context'] = dict(
        uuid=str(uuid.uuid4()),
        node_instance_id=ctx.node_instance.id,
        node_id=ctx.node.id,
        deployment_id=ctx.deployment.id,
        blueprint_id=ctx.blueprint.id,
    )


def _set_droplet_properties(droplet):
    ctx.logger.debug('Setting droplet properties...')
    # TODO: Make this idempotent (well.. it is.. but.. really)
    ctx.instance.runtime_properties['resource_properties'] = dict(
        # The id is assigned above. Even though it's a property of
        # the resource, we shouldn't have two sources or truth
        name=droplet.name,
        image=droplet.image,
        size=droplet.size,
        region=droplet.region['name'],
        disk=droplet.disk,
        memory=droplet.memory,
        vcpus=droplet.vcpus,
        ssh_keys=droplet.ssh_keys,
        tags=droplet.tags,
        token=droplet.token,
        created_at=droplet.created_at,
        backups=droplet.backups)


def _assert_completed(droplet):
    droplet_status = _get_droplet_status(droplet)
    if droplet_status == 'in-progress':
        ctx.operation.retry(
            message='Waiting for operation to complete. Retrying...',
            retry_after=30)
    elif droplet_status == 'completed':
        ctx.logger.info('Droplet shutdown successfully')
    elif droplet_status == 'errored':
        ctx.abort_operation('Droplet shutdown failed')


def _get_droplet_status(droplet):
    for action in droplet.get_actions():
        return action.status


def _get_credentials(args):
    credentials = args.get('token')
    credentials = credentials or \
        common._get_credentials('digitalocean').get('token')
    if not credentials:
        ctx.abort_operation(
            'Could not retrieve credentials. '
            'You should either supply credentials in the blueprint, '
            'provide a credentials file to look in or have credential files '
            'under one of: {0}'.format(CREDENTIALS_FILE_PATHS))


def _generate_name():
    return 'test-droplet'
