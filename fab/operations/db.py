import datetime
import time

from fabric.context_managers import cd, settings
from fabric.api import roles, sudo

from ..exceptions import PreindexNotFinished
from ..const import ROLES_DB_ONLY


def preindex_views(code_root, virtualenv_root, user):
    with cd(code_root):
        sudo((
            'echo "{virtualenv_root}/bin/python '
            '{code_root}/manage.py preindex_everything '
            '8 {user}" --mail | at -t `date -d "5 seconds" '
            '+%m%d%H%M.%S`'
        ).format(
            virtualenv_root=virtualenv_root,
            code_root=code_root,
            user=user,
        ))


def _ensure_preindex_completion():
    max_wait = datetime.timedelta(minutes=5)
    pause_length = datetime.timedelta(seconds=5)
    start = datetime.datetime.utcnow()

    _is_preindex_complete()

    done = False
    while not done and datetime.datetime.utcnow() - start < max_wait:
        time.sleep(pause_length.seconds)
        if _is_preindex_complete():
            done = True
        pause_length *= 2

    if not done:
        raise PreindexNotFinished()


@roles(ROLES_DB_ONLY)
def _is_preindex_complete(code_root, virtualenv_root, user):
    with settings(warn_only=True):
        return sudo(
            ('{virtualenv_root}/bin/python '
            '{code_root}/manage.py preindex_everything '
            '--check').format(
                virtualenv_root=virtualenv_root,
                code_root=code_root,
                user=user,
            ),
        ).succeeded
