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
import os
import digitalocean as ocean
from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


def load_token():
    """ XXX
    This will load a security token from a local file called token.txt
    A token can be obtained from DigitalOcean by Registering a New Developer or Authorized Application.
    :return: the security token, as a string
    :raises: NonRecoverableError if token is not present
    """
    cwd = os.path.dirname(__file__)
    token_path = os.path.join(cwd, 'token.txt')
    if not os.path.isfile(token_path):
        msg = 'Missing security token file "%s".' % token_path
        ctx.logger.debug(msg)
        raise NonRecoverableError(msg)
    with open(token_path, 'r') as f:
        return f.read()


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


def available_slug_sizes(region):
    """ XXX
    :param region: region specifier for which to return slug sizes
    :return: all available slug sizes
    """
    # TODO Load from API: See https://developers.digitalocean.com/#list-all-regions
    sizes = ['512mb']
    return sizes


def generate_droplet_name():
    """ XXX
    :return: a name for droplets where they're not provided from the recipe
    """
    return "Cloudify-Droplet"


@operation
def create(droplet_name=None, region=None, image=None, size_slug='512mb', backups=False, **_):
    """ XXX
    Tell the API to create a droplet. Note that not all combinations of options are possible
    :param droplet_name: formal name
    :param region: region to choose
    :param image: image to use
    :param size_slug: size slug - this value determines RAM, CPU, bandwidth, and cost of the Droplet.
    :param backups: whether to use a backup
    :return: None
    """
    def first_unless_none(param, load_func):
        if param is None:
            return load_func()[0]
        return param

    ctx.logger.info("Creating a new DigitalOcean droplet.")
    ctx.logger.debug("Create operation executing with params: droplet_name = '{0}', region = '{1}', image = '{2}', size_slug = '{3}', backups = '{4}'.".format(droplet_name, region, image, size_slug, backups))

    if droplet_name is not None:
        _name = droplet_name
    else:
        _name = generate_droplet_name()

    _image = first_unless_none(image, available_images())
    _region = first_unless_none(region, available_regions())
    _size_slug = first_unless_none(size_slug, available_slug_sizes())  # works even if user passes None

    ctx.logger.debug("Computed values for name = '{0}', image = '{1}', region = '{2}', size_slug = '{3}.'".format(_name, _image, _region, _size_slug))

    d = ocean.Droplet(token=load_token(), name=_name, image=_image, region=_region,
                      size_slug=_size_slug, backups=backups)
    d.create()
    # TODO need to check back later to see that the start operation has failed or succeeded or is still processing
    pass


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
    else:
        droplets = filter(has_id, ocean.Manager(token=load_token()).get_all_droplets())
        sz = len(droplets)
        if sz > 1:
            msg = droplet_does_not_exist_for_operation("retrieve", droplet_id)
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


@operation
def start(droplet_id=None, **_):
    """ XXX
    Starts a new Droplet, if it exists, otherwise creates a new one and starts it. does not check back for success.
    :param droplet_id:
    :return: None
    """
    def start_droplet(droplet):
        for action in droplet.get_actions():
            action.load()
            ctx.logger.debug("Executing action '{0}' for droplet '{1}'..." % [str(action), str(droplet)])

    if droplet_id is None:
        ctx.logger.info("Creating, then starting a new droplet.")
        start_droplet(create())
    else:
        ctx.logger.info("Starting existing droplet. Droplet id = '{0}'.".format(droplet_id))
        d = get_droplet(droplet_id)
        if d is not None:
            start_droplet(d)
        else:
            msg = droplet_does_not_exist_for_operation("start", droplet_id)
            ctx.logger.debug(msg)
            raise NonRecoverableError(msg)
    # TODO need to check back later to see that the start operation has failed or succeeded or is still processing
    pass


@operation
def stop(droplet_id, **_):
    """ XXX
    Asks the API to destroy a droplet, if it exists. Does not check back for success.
    :param droplet_id:
    :return: None
    """
    d = get_droplet(droplet_id)
    if d is None:
        msg = droplet_does_not_exist_for_operation("stop", droplet_id)
        ctx.logger.debug(msg)
        raise NonRecoverableError(msg)
    else:
        ctx.logger.info("Stopping droplet with droplet id = '{0}'.".format(droplet_id))
        d.destroy()
    # TODO need to check back later to see that the start operation has failed or succeeded or is still processing
    pass


def main():
    create()


if __name__ == '__main__':
    main()