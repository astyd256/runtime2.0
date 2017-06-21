
import settings


VDOM_CONFIG = {
    "SERVER-ID": settings.SERVER_ID,
    "DEFAULT-LANGUAGE": settings.DEFAULT_LANGUAGE, # "en"
    # "HTTP-ERROR-PAGES-DIRECTORY": "../errors",

    # managers directories
    # "FILE-ACCESS-DIRECTORY": settings.LOCAL_LOCATION, # "../app"
    # "XML-MANAGER-DIRECTORY": "../app"
    # "APPLICATION-XML-TEMPLATE": "../app/app_template.xml"
    # "SOURCE-MODULES-DIRECTORY": settings.MODULES_LOCATION, # "../app/objects"

    # server stuff
    "SERVER-ADDRESS": settings.SERVER_ADDRESS, # ""
    "SERVER-PORT": settings.SERVER_PORT, # 80
    "WATCHER-PORT": settings.WATCHER_PORT,
    # "SERVER-LOCALHOST-PORT": 2222,
    # "VDOM-MEMORY-SERVER-PORT": 3333,
    # "LOCALHOST-CARD-PORT": 4444,
    # "LOCALHOST-LOGGER-PORT": 5555,
    "SERVER-PIDFILE": settings.SERVER_PIDFILE_LOCATION, # "../app/server.pid"
    "LOGGER-PIDFILE": settings.LOGGER_PIDFILE_LOCATION, # "../app/logger.pid"
    # "SERVER-SOURCE-MANAGER-MEMORY-QUOTE": "10240",
    "AUTO-REMOVE-INCORRECT-APPLICATIONS": 0,

    # special URLs
    "MANAGEMENT-URL": "/system",
    "SOAP-POST-URL": "/SOAP",
    "WSDL-FILE-URL": "/vdom.wsdl",
    "WSDL-FILE-LOCATION": settings.TEMPORARY_LOCATION + "/vdom.wsdl",  # "../app/vdom.wsdl"

    # "SOURCE-TYPES-LOCATION": "../types",
    "TYPES-LOCATION": settings.TYPES_LOCATION, # "../app/types"

    # log
    "LOG-FILE-SIZE": 500000, # size of one log file
    "LOG-FILE-COUNT": 10, # max number of log files to store (history)

    # session stuff
    "SESSION-LIFETIME": settings.SESSION_LIFETIME, # 1200

    # timeouts
    "SCRIPT-TIMEOUT": settings.SCRIPT_TIMEOUT, # 30.1
    "COMPUTE-TIMEOUT": settings.COMPUTE_TIMEOUT, # 30.1
    "RENDER-TIMEOUT": settings.RENDER_TIMEOUT, # 30.1
    "WYSIWYG-TIMEOUT": settings.WYSIWYG_TIMEOUT, # 30.1

    # "APP-SAVE-TIMEOUT": MEMORY_WRITER_QUANTUM, # 30.1

    "STORAGE-DIRECTORY": settings.DATA_LOCATION, # "../app"
    "TEMP-DIRECTORY": settings.TEMPORARY_LOCATION, # "../app/temp"
    "FONT-DIRECTORY": settings.FONTS_LOCATION, # "../fonts"
    # "BACKUP-DIRECTORY": "../app/backup",
    # "SHARE-DIRECTORY": "../app/share",
    "FILE-STORAGE-DIRECTORY": settings.STORAGE_LOCATION, # "../app/storage"
    # "LIB-DIRECTORY": LIBRARIES_LOCATION, # "../app/lib"
    "LOG-DIRECTORY": settings.LOGS_LOCATION, # "../app/log"

    # storage keys
    "XML-MANAGER-TYPE-STORAGE-RECORD": "XML_TYPE_DATA",
    "XML-MANAGER-APP-STORAGE-RECORD": "XML_APPLICATION_DATA",
    "VIRTUAL-HOSTING-STORAGE-RECORD": "VIRTUAL_HOSTING_DATA",
    "FILE-MANAGER-INDEX-STORAGE-RECORD": "STORAGE_FILE_INDEX",
    "RESOURCE-MANAGER-INDEX-STORAGE-RECORD": "RESOURCE_FILE_INDEX",
    "DATABASE-MANAGER-INDEX-STORAGE-RECORD": "DATABASE_FILE_INDEX",
    "SCHEDULER-MANAGER-INDEX-STORAGE-RECORD": "SCHEDULER_INDEX",
    "BACKUP-STORAGE-DRIVER-INDEX-RECORD": "STORAGE_DRIVER_INDEX",
    "SOURCE-SWAP-FILE-INDEX-STORAGE-RECORD": "SWAP_FILE_INDEX",
    "USER-MANAGER-STORAGE-RECORD": "USER_INFO_DATA",
    "USER-MANAGER-ROOT-ID-STORAGE-RECORD": "ROOT_USER_ID",
    "USER-MANAGER-GUEST-ID-STORAGE-RECORD": "GUEST_USER_ID",
    "ACL-MANAGER-STORAGE-RECORD": "ACL_ARRAY_DATA",
    "BACKUP-STORAGE-RECORD": "BACKUP_CONFIG_DATA",
    "VDOM-CONFIG-1-RECORD": "CONFIG_1_DATA",

    # vscript
    "DISABLE-VSCRIPT": settings.DISABLE_VSCRIPT
}

VDOM_CONFIG_1 = {
    "DEBUG": "1",
    "DEBUG-ENABLE-TAGS": "0",
    "ENABLE-PAGE-DEBUG": "0",

    # email settings
    "SMTP-SENDMAIL-TIMEOUT": settings.SMTP_SENDMAIL_TIMEOUT, # 20.0
    "SMTP-SERVER-ADDRESS": settings.SMTP_SERVER_ADDRESS, # ""
    "SMTP-SERVER-PORT": settings.SMTP_SERVER_PORT, # 25
    "SMTP-SERVER-USER": settings.SMTP_SERVER_USER, # ""
    "SMTP-SERVER-PASSWORD": settings.SMTP_SERVER_PASSWORD, # ""

    # security
    "ROOT-PASSWORD": "root"
}
