import subprocess
import platform

class strip:

    def apply(self, outfile: str) -> None:
        if platform.system() == 'Linux':
            result = subprocess.run(['strip', '--strip-all', f'{outfile}'])
        if result.returncode == 0:
            return 1
        else:
            return 0