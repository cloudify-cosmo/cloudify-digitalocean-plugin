# #######
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
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


import digitalocean as ocean

from cloudify.exceptions import NonRecoverableError
from cloudify import ctx

from security import load_token


def available_images():
    """ XXX
    image specifiers are used to provision Droplets. Note: Not all images are available in all regions
    :return: a list of available image specifiers
    """
    # TODO: Load from API: See https://developers.digitalocean.com/#list-all-images
    return ['ubuntu-14-04-x64']


def available_regions():
    """ XXX
    region specifiers are used to provision Droplets in a particular data center ('region').
    Note: Not all images or options are available on all regions.
    :return: a list of available region specifiers
    """
    # TODO Load from API: See https://developers.digitalocean.com/#list-all-regions
    regions = ['nyc3', 'nyc1', 'nyc2']
    return regions


def available_slug_sizes():
    """ XXX
    :param region: region specifier for which to return slug sizes
    :return: all available slug sizes
    """
    # TODO Load from API: See https://developers.digitalocean.com/#list-all-regions
    sizes = ['512mb']
    return sizes


def get_droplet(droplet_id, **_):
    """ XXX
    searches all droplets for the one with the given droplet_id
    :param droplet_id: the one we're looking for
    :return: that droplet, or None
    """
    def has_id(droplet):
        return droplet.id == droplet_id

    if droplet_id is None:
        raise NonRecoverableError("droplet_id is required.")
    else:
        droplets = filter(has_id, ocean.Manager(token=load_token()).get_all_droplets())
        sz = len(droplets)
        if sz > 1:
            msg = droplet_does_not_exist_for_operation("get_droplet", droplet_id)
            ctx.logger.debug(msg)
            raise NonRecoverableError(msg)
        elif sz == 1:
            return droplets[0]
        else:
            return None


def droplet_does_not_exist_for_operation(op, droplet_id):
    """ Creates an error message when Droplets are unexpectedly not found for some operation
    :param op: operation for which a Droplet does not exist
    :param droplet_id: id that we expected to find
    :return: a snotty message
    """
    return "Attempted to {0} a droplet with id '{1}', but no \
    such Droplet exists in the system.".format(op, droplet_id)

# def save_key_pair(key_pair_object, ctx):
#     """ZZZ copy-paste hasn't been cleaned up - included for repo cut-over only
#     ZZZ actually broken ...
#      Saves the key pair to the file specified in the blueprint. """
#
#     ctx.logger.debug('Attempting to save the key_pair_object.')
#
#     try:
#         key_pair_object.save(ctx.node.properties['private_key_path'])
#     except (boto.exception.BotoClientError, OSError) as e:
#         raise NonRecoverableError('Unable to save key pair to file: {0}.'
#                                   'OS Returned: {1}'.format(ctx.node.properties['private_key_path'], str(e)))
#
#     path = os.path.expanduser(ctx.node.properties['private_key_path'])
#     key_path = os.path.join(path, '{0}{1}'.format(ctx.node.properties['resource_id'], '.pem'))
#
#     os.chmod(key_path, 0600)


# def delete_key_pair(ctx):
#     """ZZZ copy-paste hasn't been cleaned up - included for repo cut-over only
#     Deletes the key pair in the file specified in the blueprint. """

    # ctx.logger.debug('Attempting to save the key_pair_object.')

    # path = os.path.expanduser(ctx.node.properties['private_key_path'])
    # key_file = os.path.join(path, '{0}{1}'.format(ctx.node.properties['resource_id'], '.pem'))
    # if os.path.exists(key_file):
    #     try:
    #         os.remove(key_file)
    #     except OSError:
    #         raise NonRecoverableError('Unable to save key pair to file: {0}.'
    #                                   'OS Returned: {1}'.format(path,
    #                                                             str(OSError)))


# def search_for_key_file(ctx):
#     """ZZZ copy-paste hasn't been cleaned up - included for repo cut-over only
#     Indicates whether the file exists locally. """
#
#     path = os.path.expanduser(ctx.node.properties['private_key_path'])
#     key_file = os.path.join(path, '{0}{1}'.format(ctx.node.properties['resource_id'], '.pem'))
#     if os.path.exists(key_file):
#         return True
#     else:
#         return False
