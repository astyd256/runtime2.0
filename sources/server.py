#!/usr/bin/python

import startup.server
import managers

from logs import VDOM_log_manager
from storage import VDOM_storage
from file_access import VDOM_file_manager # VDOM_share
from resource import VDOM_resource_manager, VDOM_resource_editor
from database import VDOM_database_manager
from security import VDOM_acl_manager, VDOM_user_manager
from scripting import VDOM_compiler, VDOM_dispatcher
from memory import VDOM_memory

from server import VDOM_server
from request import VDOM_request_manager
from engine import VDOM_engine
# from mailing import VDOM_email_manager
from session import VDOM_session_manager
from module import VDOM_module_manager


managers.register("log_manager", VDOM_log_manager)
managers.register("storage", VDOM_storage)
managers.register("file_manager", VDOM_file_manager)
# managers.register("file_share", VDOM_share)
managers.register("resource_manager", VDOM_resource_manager)
managers.register("resource_editor", VDOM_resource_editor)
managers.register("database_manager", VDOM_database_manager)
managers.register("acl_manager", VDOM_acl_manager)
managers.register("user_manager", VDOM_user_manager)
managers.register("dispatcher", VDOM_dispatcher)
managers.register("compiler", VDOM_compiler)
managers.register("memory", VDOM_memory)

managers.register("request_manager", VDOM_request_manager)
managers.register("session_manager", VDOM_session_manager)
managers.register("engine", VDOM_engine)
# managers.register("scheduler_manager", VDOM_scheduler_manager)
# managers.register("email_manager", VDOM_email_manager)
managers.register("module_manager", VDOM_module_manager)
managers.register("server", VDOM_server)

managers.server.start()
