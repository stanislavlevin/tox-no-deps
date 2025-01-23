import logging

from tox.config.loader.memory import MemoryLoader
from tox.plugin import impl


logger = logging.getLogger(__name__)


@impl
def tox_add_option(parser):
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="skip the installation of test env's deps",
    )


@impl
def tox_add_env_config(env_conf, state):
    if not all(
        (
            state.conf.options.no_deps,
            "runner" in env_conf,  # only tests environments
        )
    ):
        return

    logger.info("relaxing dependencies for test env: %s", env_conf.env_name)

    override = {"deps": [], "extras": [], "dependency_groups": []}
    env_conf.loaders.insert(0, MemoryLoader(**override))
