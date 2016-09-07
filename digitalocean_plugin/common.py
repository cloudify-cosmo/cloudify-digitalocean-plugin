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

import yaml

from cloudify import ctx


# TODO: Move to plugins-common
def _get_credentials(provider, credentials_file_path=None):
    """Return a set of credentials for a specific provider given a credentials file

    The file should look somewhat like this:

    ```
    digitalocean:
        token: mylongtoken

    aws:
        aws_secret_key: mysecretkey
        aws_secret_key_id: mysecretkeyid
    ```
    """
    # If a user provided a file, use it.
    # If not, iterate through a list of potential file locations
    # Open the file and look for the provider's specific settings.
    # If it wasn't found, move to the next file.
    # If credentials for that provider weren't found, abort, else return them.
    # TODO: Allow to pass a parser function to parse the file.

    credentials_file_paths = [credentials_file_path] or CREDENTIALS_FILE_PATHS
    provider_credentials = {}
    for path in credentials_file_paths:
        if os.path.isfile(path):
            credentials = _load_credentials_file()
            try:
                provider_credentials = credentials[provider]
                # Only return if provider credentials are not nothing
                if provider_credentials:
                    ctx.logger.info(
                        'Credentials for {0} found under {1}'.format(
                            provider, path))
                    return provider_credentials
            except ValueError:
                ctx.logger.debug(
                    'Credentials for {0} were not found under {1}'.format(
                        provider, path))
    return {}


def _load_credentials_file(path):
    with open(path) as credentials_file:
        try:
            return yaml.safe_load(credentials_file.read())
        except IOError as ex:
            ctx.abort_operation(
                'Credentials file {0} is not accessible ({1})'.format(
                    path, ex))
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as ex:
            ctx.abort_operation('{0} must be a valid YAML file ({1})'.format(
                path, ex))
