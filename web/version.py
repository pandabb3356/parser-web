MAJOR = 1
MINOR = 1
PATCH = 'dev'
REVISION = '@'
VERSION = '{}.{}.{}-{}'.format(MAJOR, MINOR, PATCH, REVISION)


def sem_ver():
    return VERSION
