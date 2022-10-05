import os
from invoke import task

from tasks import get_project_root

OUTPUT_PATH = '~/kenTest/projects_loc'


@task
def pkg(ctx, p='parser-web-clean'):
    project_root = get_project_root()
    user_home = os.path.expanduser('~')

    project_name = p

    output_path = os.path.expanduser(OUTPUT_PATH)

    proj_dir = '{output_path}/{project_name}'.format(**locals())

    if os.path.exists(proj_dir):
        ctx.run('rm -r {}'.format(proj_dir))

    ctx.run('mkdir -p {} '.format(proj_dir))

    modules = (
        'scripts',
        'migrations',
        'web',
        'run.py',
        'run_worker.py',
        'prod-requirements.txt',
        'Dockerfile',
        'sources.list',
    )

    # copy required modules
    for module in modules:
        ctx.run('cp -r {module} {proj_dir}/'.format(**locals()))

    # build image
    # image_version = os.environ.get('version', 'latest')
    # ctx.run(f'docker build -t="parser-web:{image_version}" {proj_dir}')
