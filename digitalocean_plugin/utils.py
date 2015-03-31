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


# Cloudify Imports
from cloudify.exceptions import NonRecoverableError

# from security import _load_digitalocean_account_token


def available_images():
    """ XXX
    image specifiers are used to provision Droplets. Note: Not all images are
    available in all regions
    :return: a list of available image specifiers
    """
    # TODO: Load from API: See
    # https://developers.digitalocean.com/#list-all-images
    return ['ubuntu-14-04-x64']


def available_regions():
    """ XXX
    region specifiers are used to provision Droplets in a particular data
    center ('region'). Note: Not all images or options are available on all
    regions.
    :return: a list of available region specifiers
    """
    # TODO Load from API: See
    # https://developers.digitalocean.com/#list-all-regions
    regions = ['nyc3', 'nyc1', 'nyc2']
    return regions


def available_slug_sizes():
    """ XXX
    :return: all available slug sizes
    """
    # TODO Load from API:
    # See https://developers.digitalocean.com/#list-all-regions
    sizes = ['512mb']
    return sizes


def get_droplet(droplet_id):
    """ XXX
    searches all droplets for the one with the given droplet_id
    :param droplet_id: the one we're looking for
    :return: that droplet, or None
    """
    def has_id(droplet):
        return droplet.id == droplet_id

    if droplet_id is None:
        raise NonRecoverableError("droplet_id is required.")
    raise NonRecoverableError("implement me")


def droplet_does_not_exist_for_operation(op, droplet_id):
    """ Creates an error message when Droplets are unexpectedly not found for
     some operation
    :param op: operation for which a Droplet does not exist
    :param droplet_id: id that we expected to find
    :return: a snotty message
    """
    return "Attempted to {0} a droplet with id '{1}', but no \
    such Droplet exists in the system.".format(op, droplet_id)
