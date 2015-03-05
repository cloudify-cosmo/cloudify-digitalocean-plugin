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

import os

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError


def load_token(**_):
    """
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