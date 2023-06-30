from __future__ import print_function

import os
import sys
import subprocess
import locale
try:
    from shlex import quote
except ImportError:
    from pipes import quote


def exec_in_env(conda_prefix, env_path, *command):
    # Run the standard conda activation script, and print the
    # resulting environment variables to stdout for reading.
    is_current_env = env_path == sys.prefix
    if sys.platform.startswith('win'):
        if is_current_env:
            subprocess.Popen(list(command)).wait()
        else:
            activate = os.path.join(conda_prefix, 'Scripts', 'activate.bat')
            ecomm = [os.environ['COMSPEC'], '/S', '/U', '/C', '@echo', 'off', '&&',
                    'chcp', '65001', '&&', 'call', activate, env_path, '&&',
                    '@echo', 'CONDA_PREFIX=%CONDA_PREFIX%', '&&',] + list(command)
            subprocess.Popen(ecomm).wait()
    else:
        quoted_command = [quote(c) for c in command]
        if is_current_env:
            os.execvp(quoted_command[0], quoted_command)
        else:
            activate = os.path.join(conda_prefix, 'bin', 'activate')
            global_act_file = os.path.join(os.path.dirname(os.path.dirname(env_path)), 'global-activate.sh')
            global_act = f"source {global_act_file}" if os.path.exists(global_act_file) else None

            ecomm = ". '{}' '{}' && echo CONDA_PREFIX=$CONDA_PREFIX && exec {}".format(activate, env_path, ' '.join(quoted_command))
            if global_act:
                ecomm = f"{global_act} && {ecomm}"

            ecomm = ['sh' if 'bsd' in sys.platform else 'bash', '-c', ecomm]
            os.execvp(ecomm[0], ecomm)


if __name__ == '__main__':
    exec_in_env(*(sys.argv[1:]))
