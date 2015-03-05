# #######
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
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
from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from security import load_token
from utils import available_images, available_regions, available_slug_sizes, get_droplet, droplet_does_not_exist_for_operation


def generate_droplet_name():
    """ XXX
    :return: a name for droplets where they're not provided from the recipe
    """
    return "Cloudify-Droplet"


@operation
def create(droplet_name=None, region=None, image=None, size_slug='512mb', backups=False, **_):
    """
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

    _image = first_unless_none(image, available_images)
    _region = first_unless_none(region, available_regions)
    _size_slug = first_unless_none(size_slug, available_slug_sizes)  # works even if user passes None

    ctx.logger.debug("Computed values for name = '{0}', image = '{1}', region = '{2}', size_slug = '{3}.'".format(_name, _image, _region, _size_slug))

    d = ocean.Droplet(token=load_token(), name=_name, image=_image, region=_region,
                      size_slug=_size_slug, backups=backups)
    d.create()
    # TODO need to check back later to see that the start operation has failed or succeeded or is still processing
    pass


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
        d = get_droplet(droplet_id, **_)
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
    d = get_droplet(droplet_id, **_)
    if d is None:
        msg = droplet_does_not_exist_for_operation("stop", droplet_id)
        ctx.logger.debug(msg)
        raise NonRecoverableError(msg)
    else:
        ctx.logger.info("Stopping droplet with droplet id = '{0}'.".format(droplet_id))
        d.destroy()
    # TODO need to check back later to see that the start operation has failed or succeeded or is still processing
    pass
