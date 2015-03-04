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
from cloudify.exceptions import NonRecoverableError


def save_key_pair(key_pair_object, ctx):
    """ZZZ copy-paste hasn't been cleaned up - included for repo cut-over only
    ZZZ actually broken ...
     Saves the key pair to the file specified in the blueprint. """

    ctx.logger.debug('Attempting to save the key_pair_object.')

    try:
        key_pair_object.save(ctx.node.properties['private_key_path'])
    except (boto.exception.BotoClientError, OSError) as e:
        raise NonRecoverableError('Unable to save key pair to file: {0}.'
                                  'OS Returned: {1}'.format(ctx.node.properties['private_key_path'], str(e)))

    path = os.path.expanduser(ctx.node.properties['private_key_path'])
    key_path = os.path.join(path, '{0}{1}'.format(ctx.node.properties['resource_id'], '.pem'))

    os.chmod(key_path, 0600)


def delete_key_pair(ctx):
    """ZZZ copy-paste hasn't been cleaned up - included for repo cut-over only
    Deletes the key pair in the file specified in the blueprint. """

    ctx.logger.debug('Attempting to save the key_pair_object.')

    path = os.path.expanduser(ctx.node.properties['private_key_path'])
    key_file = os.path.join(path, '{0}{1}'.format(ctx.node.properties['resource_id'], '.pem'))
    if os.path.exists(key_file):
        try:
            os.remove(key_file)
        except OSError:
            raise NonRecoverableError('Unable to save key pair to file: {0}.'
                                      'OS Returned: {1}'.format(path,
                                                                str(OSError)))


def search_for_key_file(ctx):
    """ZZZ copy-paste hasn't been cleaned up - included for repo cut-over only
    Indicates whether the file exists locally. """

    path = os.path.expanduser(ctx.node.properties['private_key_path'])
    key_file = os.path.join(path, '{0}{1}'.format(ctx.node.properties['resource_id'], '.pem'))
    if os.path.exists(key_file):
        return True
    else:
        return False
