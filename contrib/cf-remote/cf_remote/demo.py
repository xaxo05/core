import os
import json

from cf_remote import log
from cf_remote.paths import cf_remote_dir
from cf_remote.utils import save_file
from cf_remote.ssh import scp, ssh_sudo, auto_connect


@auto_connect
def agent_run(host, *, connection=None):
    print("Triggering an agent run on: '{}'".format(host))
    command = "/var/cfengine/bin/cf-agent -Kf update.cf"
    output = ssh_sudo(connection, command)
    log.debug(output)
    command = "/var/cfengine/bin/cf-agent -K"
    output = ssh_sudo(connection, command)
    log.debug(output)


def disable_password_dialog(host):
    print("Disabling password change on hub: '{}'".format(host))
    api = "https://{}/api/user/admin".format(host)
    d = json.dumps({"password": "password"})
    creds = "admin:admin"
    c = "curl -X POST  -k {} -u {}  -H 'Content-Type: application/json' -d '{}'".format(
        api, creds, d)
    log.debug(c)
    os.system(c)


def def_json(call_collect=False):
    d = {
        "classes": {
            "mpf_augments_control_enabled": ["any"],
            "services_autorun": ["any"],
            "cfengine_internal_purge_policies": ["any"]
        },
        "vars": {
            "control_hub_exclude_hosts": ["0.0.0.0/0"],
            "acl": ["0.0.0.0/0", "::/0"],
            "default_data_select_host_monitoring_include": [".*"],
            "default_data_select_policy_hub_monitoring_include": [".*"],
            "control_executor_splaytime": "1"
        }
    }

    if call_collect:
        d["classes"]["client_initiated_reporting_enabled"] = ["any"]
        d["vars"]["control_server_call_collect_interval"] = "1"
        d["vars"]["mpf_access_rules_collect_calls_admit_ips"] = ["0.0.0.0/0"]

    return d


@auto_connect
def install_def_json(host, *, connection=None, call_collect=False):
    print("Transferring def.json to hub: '{}'".format(host))
    data = json.dumps(def_json(call_collect), indent=2)
    path = os.path.join(cf_remote_dir("json"), "def.json")
    save_file(path, data)
    scp(path, host, connection=connection)
    ssh_sudo(connection, "cp def.json /var/cfengine/masterfiles/def.json")
