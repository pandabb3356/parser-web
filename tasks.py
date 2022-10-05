import os

from invoke import Collection

from task import misc


def get_project_root(path=__file__):
    directory = os.path.dirname(path)

    while directory != '/':
        p = os.path.join(directory, 'requirements.txt')
        if os.path.isfile(p):
            return directory
        else:
            directory = os.path.dirname(directory)

    return None


from task import pkg, db

ns = Collection.from_module(misc)
for module in [pkg, db]:
    ns.add_collection(Collection.from_module(module))
