import subprocess

class GitUtils:
    @staticmethod
    def get_git_revision_short_hash() -> str:
        '''Return the short hash of the current git commit, like `c1da0a2` as a string

        Calls out to Git at the command line so will not work if it's not present'''
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()