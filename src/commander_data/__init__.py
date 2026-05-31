"""Build command lines for subprocess.

Use
:code:`COMMAND`
to create commandlines
that can be passed directly
to
:code:`subprocess.run`
or similar.

For example,

.. code::

    subprocess.run(COMMAND.git.commit(all=None, message="quick commit"))

Each operation on
:code:`COMMAND`
gives a sub-command that adds more items to the command:

* :code:`.<attribute>`: Add the name of the attribute. Underscores become dashes.
* :code:`(arg1, arg2, ..., key=value, ...)`: Add `--key <value>`.

  * Underscores in :code:`key` become dashes.
  * A value of :code:`None` results in a flag.
  * A list results in ``--key <first value> --key <second value> ..``
  * Non-keyword arguments are added last.

Those are composable in any order.
"""

import importlib.metadata
from .api import COMMAND, run_all

__version__ = importlib.metadata.version(__name__)

__all__ = ["COMMAND", "__version__", "run_all"]
