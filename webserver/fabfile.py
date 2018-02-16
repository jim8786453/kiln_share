# -*- coding: utf-8 -*-
import os

from fabric.api import run, local, env, settings, cd, task, put, execute
from fabric.contrib.files import exists, upload_template
from fabric.operations import _prefix_commands, _prefix_env_vars, require, sudo


env.use_ssh_config = True


LOCAL_HOST = os.environ.get('LOCAL_HOST')
LOCAL_USER = os.environ.get('LOCAL_USER')
LOCAL_PASSWORD =  os.environ.get('LOCAL_PASSWORD')
LOCAL_SERVER_NAME = os.environ.get('LOCAL_SERVER_NAME')
LOCAL_JWT_SECRET = os.environ.get('LOCAL_JWT_SECRET')


WWW_HOST = os.environ.get('WWW_HOST')
WWW_USER = os.environ.get('WWW_USER')
WWW_PASSWORD =  os.environ.get('WWW_PASSWORD')
WWW_SERVER_NAME = os.environ.get('WWW_SERVER_NAME')
WWW_JWT_SECRET = os.environ.get('WWW_JWT_SECRET')


STAGES = {
    'local': {
        'hosts': [LOCAL_HOST],
        'user': LOCAL_USER,
        'pasword': LOCAL_PASSWORD,
        'server_name': LOCAL_SERVER_NAME,
        'jwt_secret': LOCAL_JWT_SECRET
    },
    'www': {
        'hosts': [WWW_HOST],
        'user': WWW_USER,
        'server_name': WWW_SERVER_NAME,
        'jwt_secret': WWW_JWT_SECRET
    }
}


def stage_set(stage_name='local'):
    """Utility function to set an environment up for Fabric.

    """
    env.stage = stage_name
    for option, value in STAGES[env.stage].items():
        setattr(env, option, value)


def stage_require():
    """Ensure a valid stage is enabled.

    """
    require('stage', provided_by=(
        local,
        www))


@task
def local():
    """Use the local environment.

    """
    stage_set('local')


@task
def www():
    """Use the live environment.

    """
    stage_set('www')


@task
def check_sudo():
    """Run a command that uses sudo.

    """
    stage_require()
    sudo("date")


@task
def install():
    """Install all kilnshare.co.uk webserver components.

    """
    stage_require()
    remove()
    setup_dirs()
    install_openresty()
    install_lua()
    install_nginxjwt()
    install_modules()
    configure_firewall()
    configure_certs()
    configure_openresty()
    restart()


@task
def install_light():
    """Install everything except OpenResty and Lua.

    """
    stage_require()
    remove()
    setup_dirs()
    install_nginxjwt()
    install_modules()
    configure_firewall()
    configure_certs()
    configure_openresty()
    restart()


@task
def remove():
    stage_require()
    sudo('rm -Rf /home/%s/deploy' % env.user)
    sudo('rm -Rf /usr/local/openresty/')


@task
def setup_dirs():
    stage_require()
    run('mkdir -p /home/%s/deploy' % env.user)
    run('mkdir -p /home/%s/deploy/bin' % env.user)
    run('mkdir -p /home/%s/deploy/config' % env.user)
    run('mkdir -p /home/%s/deploy/downloads' % env.user)
    run('mkdir -p /home/%s/deploy/scripts' % env.user)
    run('mkdir -p /home/%s/deploy/www' % env.user)


@task
def install_openresty():
    """

    """
    stage_require()
    put('scripts/install_openresty.sh',
        '/home/%s/deploy/scripts/install_openresty.sh' % env.user,
        mode=0755)
    sudo('/home/%s/deploy/scripts/install_openresty.sh' % env.user)


@task
def install_lua():
    """Install and configure Lua and dependencies.

    """
    stage_require()
    upload_template(
        'scripts/install_lua.sh',
        '/home/%s/deploy/scripts/install_lua.sh' % env.user,
        context=env,
        use_jinja=True,
        mode=0755,
        backup=False)
    sudo('/home/%s/deploy/scripts/install_lua.sh' % env.user)


@task
def install_nginxjwt():
    """Install and configure Lua and dependencies.

    """
    stage_require()
    upload_template(
        'scripts/install_nginxjwt.sh',
        '/home/%s/deploy/scripts/install_nginxjwt.sh' % env.user,
        context=env,
        use_jinja=True,
        mode=0755,
        backup=False)
    sudo('/home/%s/deploy/scripts/install_nginxjwt.sh' % env.user)


@task
def install_modules():
    """

    """
    stage_require()
    put('modules/kiln_share.lua', '/home/%s/deploy/bin/kiln_share.lua'
        % env.user, use_sudo=True)


@task
def configure_firewall():
    """Configure Ubuntu firewall.

    """
    stage_require()
    sudo('ufw allow http')
    sudo('ufw allow https')


@task
def configure_certs():
    """Create SSL certificates.

    - Uses Letsencypt for all non local environments.

    """
    stage_require()

    if not env.stage == 'local':
        upload_template(
            'templates/letsencrypt.sh',
            '/home/%s/deploy/scripts/letsencrypt.sh' % env.user,
            context=env,
            use_jinja=True,
            mode=0755,
            backup=False)

        sudo('/home/%s/deploy/scripts/letsencrypt.sh' % env.user)
        return

    # local.kilnshare.co.uk does not have a DNS entry so we can't use
    # Letsencrypt. Self sign instead.
    sudo('mkdir -p /etc/letsencrypt/live/local.kilnshare.co.uk/')
    sudo('cp /etc/ssl/certs/ssl-cert-snakeoil.pem /etc/letsencrypt/live/local.kilnshare.co.uk/fullchain.pem')
    sudo('cp /etc/ssl/private/ssl-cert-snakeoil.key /etc/letsencrypt/live/local.kilnshare.co.uk/privkey.pem')
    sudo('openssl dhparam -out ~/deploy/dhparams.pem 2048')


@task
def configure_openresty():
    """Upload Openresty configuration files.

    - Make logging directories
    - Configure systemctl

    """
    stage_require()
    sudo('mkdir -p /var/log/openresty')
    sudo('mkdir -p /usr/local/openresty/nginx/sites')
    upload_template(
        'templates/openresty.service',
        '/etc/systemd/system/openresty.service',
        context=env,
        use_jinja=True,
        use_sudo=True,
        backup=False)
    upload_template(
        'templates/nginx.conf',
        '/usr/local/openresty/nginx/conf/nginx.conf',
        context=env,
        use_jinja=True,
        use_sudo=True,
        backup=False)
    upload_template(
        'templates/default.conf',
        '/usr/local/openresty/nginx/sites/default.conf',
        context=env,
        use_jinja=True,
        use_sudo=True,
        backup=False)
    sudo('sudo systemctl daemon-reload')
    sudo('sudo systemctl enable openresty')


@task
def start():
    """Start Openresty webserver.

    """
    stage_require()
    sudo('systemctl start openresty')


@task
def stop():
    """Stop Openresty webserver.

    """
    stage_require()
    sudo('systemctl stop openresty')


@task
def restart():
    """Restart Openresty webserver.

    """
    stage_require()
    sudo('systemctl restart openresty')
