
import string
import base64

from collections import defaultdict, OrderedDict
from uuid import uuid4

import managers

from utils.structure import VDOM_structure
from utils.parsing import ParsingException, \
    SectionMustPrecedeError, MissingSectionError, \
    UnexpectedElementValueError, UnexpectedAttributeValueError, \
    MissingElementError, MissingAttributeError
# from vscript.engine import vcompile

from ..constants import VSCRIPT_LANGUAGE, SCRIPT_CONTEXT


def application_builder(parser, callback=None):
    "legacy"  # select legacy builder mode
    # TODO: Check attributes values for validity
    def document_handler(name, attributes):
        if name == u"Application":
            # <Application>
            application = managers.memory.applications.new_sketch()
            containers = {}
            objects = {}
            bindings = {}
            actions = {}
            events = set()
            libraries = set()
            sections = {}
            def application_handler(name, attributes):
                sections[name] = True
                if name == u"Information":
                    # <Information>
                    def information_handler(name, attributes):
                        if name == u"ID" or name == u"ExtRef":
                            # <ID>
                            def id_handler(value): application.id = value.lower()
                            parser.handle_value(name, attributes, id_handler)
                            # </ID>
                        elif name == u"Name":
                            # <Name>
                            def name_handler(value): application.name = value
                            parser.handle_value(name, attributes, name_handler)
                            # </Name>
                        elif name == u"Description":
                            # <Description>
                            def description_handler(value): application.description = value
                            parser.handle_value(name, attributes, description_handler)
                            # </Description>
                        elif name == u"Version":
                            # <Version>
                            def version_handler(value): application.version = value
                            parser.handle_value(name, attributes, version_handler)
                            # </Version>
                        elif name == u"Owner":
                            # <Owner>
                            def owner_handler(value): application.owner = value
                            parser.handle_value(name, attributes, owner_handler)
                            # </Owner>
                        elif name == u"Password":
                            # <Password>
                            def password_handler(value): application.password = value
                            parser.handle_value(name, attributes, password_handler)
                            # </Password>
                        elif name == u"Active":
                            # <Active>
                            def active_handler(value):
                                try:
                                    application.active = int(value)
                                except ValueError:
                                    raise UnexpectedElementValueError(name)
                            parser.handle_value(name, attributes, active_handler)
                            # </Active>
                        elif name == u"Index":
                            # <Index>
                            def index_handler(value): application.index = value
                            parser.handle_value(name, attributes, index_handler)
                            # </Index>
                        elif name == u"Icon":
                            # <Icon>
                            def icon_handler(value): application.icon = value
                            parser.handle_value(name, attributes, icon_handler)
                            # </Icon>
                        elif name == u"ServerVersion" or name == u"Serverversion":
                            # <ServerVersion>
                            def serverversion_handler(value): application.server_version = value
                            parser.handle_value(name, attributes, serverversion_handler)
                            # </ServerVersion>
                        elif name == u"ScriptingLanguage":
                            # <ScriptingLanguage>
                            def scriptinglanguage_handler(value): application.scripting_language = value
                            parser.handle_value(name, attributes, scriptinglanguage_handler)
                            # </ScriptingLanguage>
                        elif name == u"DefaultLanguage":
                            # <DefaultLanguage>
                            def defaultlanguage_handler(value): application.default_language = value
                            parser.handle_value(name, attributes, defaultlanguage_handler)
                            # </DefaultLanguage>
                        elif name == u"CurrentLanguage":
                            # <CurrentLanguage>
                            def currentlanguage_handler(value): application.current_language = value
                            parser.handle_value(name, attributes, currentlanguage_handler)
                            # </CurrentLanguage>
                        else:
                            parser.reject_elements(name, attributes)
                    def close_information_handler(name):
                        if application.id is None:
                            MissingElementError(u"ID")
                        if application.name is None:
                            MissingElementError(u"Name")
                        if callback:
                            callback(application)
                    parser.handle_elements(name, attributes, information_handler, close_information_handler)
                    # </Information>
                elif name == u"Objects":
                    # <Objects>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    context = VDOM_structure(level=0, container=application.objects) # pages
                    def objects_handler(name, attributes):
                        if name == u"Object":
                            # <Object>
                            try:
                                object_type_id = attributes.pop(u"Type")
                            except KeyError:
                                raise MissingAttributeError(u"Type")
                            try:
                                object_type = managers.memory.types[object_type_id]
                            except KeyError:
                                raise ParsingException(u"Type %s not found" % object_type_id)
                            object = context.container.new_sketch(object_type)
                            try:
                                object.id = attributes.pop(u"ID")
                            except KeyError:
                                raise MissingAttributeError(u"ID")
                            try:
                                object.name = attributes.pop(u"Name")
                            except KeyError:
                                raise MissingAttributeError(u"Name")
                            previous_context = context.level, context.container
                            def object_handler(name, attributes):
                                if name == u"Attributes":
                                    # <Attributes>
                                    def attributes_handler(name, attributes):
                                        if name == u"Attribute":
                                            # <Attribute>
                                            try:
                                                attribute_name = attributes.pop(u"Name")
                                            except KeyError:
                                                raise MissingAttributeError(u"Name")
                                            def attribute_handler(value):
                                                if attribute_name in object.type.attributes:
                                                    object.attributes[attribute_name] = value
                                                else:
                                                    parser.notify("Ignore \"%s\" object attribute" % attribute_name)
                                            parser.handle_value(name, attributes, attribute_handler)
                                            # </Attribute>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    parser.handle_elements(name, attributes, attributes_handler)
                                    # </Attributes>
                                elif name == u"Objects":
                                    # <Objects>
                                    context.level, context.container = context.level + 1, object.objects
                                    parser.handle_elements(name, attributes, objects_handler)
                                    # </Objects>
                                elif name == u"Scripts":
                                    # <Scripts>
                                    def scripts_handler(name, attributes):
                                        if name == u"Script":
                                            # <Script>
                                            action = object.actions.new_sketch()
                                            try:
                                                attributes.pop(u"Language")
                                            except KeyError:
                                                pass
                                            action.id = str(uuid4())
                                            action.name = SCRIPT_CONTEXT
                                            def script_handler(value):
                                                action.source_code = value
                                                actions[action.id] = action
                                                # ~action
                                            parser.handle_value(name, attributes, script_handler)
                                            # </Script>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    parser.handle_elements(name, attributes, scripts_handler)
                                    # </Scripts>
                                elif name == u"Actions":
                                    # <Actions>
                                    def actions_handler(name, attributes):
                                        if name == u"Action":
                                            # <Action>
                                            action = object.actions.new_sketch()
                                            try:
                                                action.id = attributes.pop(u"ID")
                                            except KeyError:
                                                try:
                                                    action.id = attributes.pop(u"id")
                                                except KeyError:
                                                    raise MissingAttributeError(u"ID")
                                            try:
                                                action.name = attributes.pop(u"Name")
                                            except KeyError:
                                                raise MissingAttributeError(u"Name")
                                            try:
                                                attributes.pop(u"Language")
                                            except KeyError:
                                                pass
                                            try:
                                                # Here "or 0" is the hack to handle Top="" elements
                                                action.top = int(attributes.pop(u"Top") or u"0")
                                            except KeyError:
                                                pass
                                            except ValueError:
                                                raise UnexpectedAttributeValueError(u"Top")
                                            try:
                                                # Here "or 0" is the hack to handle Left="" elements
                                                action.left = int(attributes.pop(u"Left") or u"0")
                                            except KeyError:
                                                pass
                                            except ValueError:
                                                raise UnexpectedAttributeValueError(u"Top")
                                            try:
                                                # Here "or 0" is the hack to handle State="" elements
                                                action.state = (attributes.pop(u"State") or u"False").lower() in (u"1", u"true")
                                            except KeyError:
                                                pass
                                            def action_handler(value):
                                                action.source_code = value
                                                actions[action.id] = action
                                                # ~action
                                            parser.handle_value(name, attributes, action_handler)
                                            # </Action>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    parser.handle_elements(name, attributes, actions_handler)
                                    # </Actions>
                                else:
                                    parser.reject_elements(name, attributes)
                            def close_object_handler(name):
                                context.level, context.container = previous_context
                                objects[object.id] = object
                                if not object.parent:
                                    containers[object.id] = object
                            parser.handle_elements(name, attributes, object_handler, close_object_handler)
                            # </Object>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, objects_handler)
                    # </Objects>
                elif name == u"Actions":
                    # <Actions>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    def actions_handler(name, attributes):
                        if name == u"Action":
                            # <Action>
                            action = application.actions.new_sketch() # global
                            try:
                                action.id = attributes.pop(u"ID")
                            except KeyError:
                                raise MissingAttributeError(u"ID")
                            if action.id.lower() in (u"session", u"application"):
                                action.id = str(uuid4())
                            try:
                                action.name = attributes.pop(u"Name")
                            except KeyError:
                                raise MissingAttributeError(u"Name")
                            try:
                                attributes.pop(u"Language")
                            except KeyError:
                                pass
                            try:
                                # Here "or 0" is the hack to handle Top="" elements
                                action.top = int(attributes.pop(u"Top") or u"0")
                            except KeyError:
                                pass
                            except ValueError:
                                raise UnexpectedAttributeValueError(u"Top")
                            try:
                                # Here "or 0" is the hack to handle Left="" elements
                                action.left = int(attributes.pop(u"Left") or u"0")
                            except KeyError:
                                pass
                            except ValueError:
                                raise UnexpectedAttributeValueError(u"Top")
                            try:
                                # Here "or 0" is the hack to handle State="" elements
                                action.state = (attributes.pop(u"State") or u"False").lower() in (u"1", u"true")
                            except KeyError:
                                pass
                            def action_handler(value):
                                action.source_code = value
                                # ~action
                                actions[action.id] = action
                            parser.handle_value(name, attributes, action_handler)
                            # </Action>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, actions_handler)
                    # </Actions>
                elif name == u"Structure":
                    # <Structure>
                    if u"Objects" not in sections:
                        raise SectionMustPrecedeError(u"Objects")
                    def structure_handler(name, attributes):
                        if name == u"Object":
                            # <Object>
                            try:
                                parent_id = attributes.pop(u"ID")
                            except KeyError:
                                raise MissingAttributeError(u"ID")
                            # parent = application.objects.get(parent_id) # pages
                            parent = containers[parent_id]
                            if not parent:
                                parser.handle_elements(name, attributes)
                                return
                            structure = parent.structure
                            obsolete_resource = structure.resource
                            try:
                                structure.top = attributes.pop(u"Top")
                            except KeyError:
                                pass
                            try:
                                structure.left = attributes.pop(u"Left")
                            except KeyError:
                                pass
                            try:
                                structure.state = attributes.pop(u"State")
                            except KeyError:
                                pass
                            try:
                                # Here "or 0" is the hack to handle ResourceID="" elements
                                structure.resource = attributes.pop(u"ResourceID") or None
                            except KeyError:
                                pass
                            if structure.resource != obsolete_resource:
                                if structure.resource and \
                                        managers.resource_manager.check_resource(application.id, {"id": structure.resource}):
                                    managers.resource_manager.add_resource(application.id, parent.id, attributes, None)
                                if obsolete_resource and \
                                        managers.resource_manager.check_resource(application.id, {"id": obsolete_resource}):
                                    managers.resource_manager.delete_resource(parent.id, obsolete_resource)
                            def object_handler(name, attributes):
                                if name == u"Level":
                                    # <Level>
                                    try:
                                        level_name = attributes.pop(u"Name")
                                    except KeyError:
                                        try:
                                            level_name = attributes.pop(u"Index")
                                        except KeyError:
                                            raise MissingAttributeError(u"Name")
                                    level, obsolete_objects = structure[level_name], defaultdict(set)
                                    def level_handler(name, attributes):
                                        if name == u"Object":
                                            # <Object>
                                            try:
                                                child_id = attributes.pop(u"ID")
                                            except KeyError:
                                                raise MissingAttributeError(u"ID")
                                            child = application.cotainers.get(child_id)
                                            if not child_id:
                                                parser.handle_elements(name, attributes)
                                                return
                                            try:
                                                obsolete_objects[attributes.pop(u"Index")].add(child)
                                            except KeyError:
                                                level.add(child)
                                            parser.handle_elements(name, attributes)
                                            # </Object>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    def close_level_handler(name):
                                        for objects in obsolete_objects.itervalues():
                                            level.update(objects)
                                    parser.handle_elements(name, attributes, level_handler)
                                    # </Level>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, object_handler)
                            # </Object>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, structure_handler)
                    # </Structure>
                elif name == u"Libraries":
                    # <Libraries>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    # managers.file_manager.create_lib_path(application.id)
                    def libraries_handler(name, attributes):
                        if name == u"Library":
                            # <Library>
                            try:
                                library_name = attributes.pop(u"Name")
                            except KeyError:
                                raise MissingAttributeError(u"Name")
                            # if not is_valid_identifier(name): raise VDOM_incorrect_value_error, u"Name"
                            def library_handler(value):
                                # application.libraries[library_name] = value
                                # if application.scripting_language == u"vscript":
                                #     # TODO: Check this thread using
                                #     threading.currentThread().application = application.id
                                #     try:
                                #         value, source = vcompile(value, bytecode=0)
                                #     finally:
                                #         threading.currentThread().application = None

                                managers.file_manager.write_library(application.id,
                                    library_name + application.scripting_extension, value)
                                libraries.add(library_name)

                                # previous = managers.engine.select(application.id)
                                # try:
                                #     code, source = vcompile(value, bytecode=0)
                                # finally:
                                #     managers.engine.select(previous)

                                # managers.file_manager.write_library(application.id, library_name + ".py", value)
                            parser.handle_value(name, attributes, library_handler)
                            # </Library>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, libraries_handler)
                    # </Libraries>
                elif name == u"Languages" or name == u"LanguageData":
                    # <Languages>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    def languages_handler(name, attributes):
                        if name == u"Language":
                            # <Language>
                            try:
                                language_code = attributes.pop(u"Code")
                            except KeyError:
                                raise MissingAttributeError(u"Code")
                            def language_handler(name, attributes):
                                if name == u"Sentence":
                                    # <Sentence>
                                    try:
                                        sentence_id = int(attributes.pop(u"ID"))
                                    except ValueError:
                                        raise UnexpectedAttributeValueError(u"ID")
                                    except KeyError:
                                        raise MissingAttributeError(u"ID")
                                    def sentence_handler(value): application.sentences.setdefault(language_code, {})[sentence_id] = value
                                    parser.handle_value(name, attributes, sentence_handler)
                                    # </Sentence>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, language_handler)
                            # </Language>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, languages_handler)
                    # </Languages>
                elif name == u"Resources":
                    # <Resources>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    def resources_handler(name, attributes):
                        if name == u"Resource":
                            # <Resource>
                            try:
                                resource_id = attributes.pop(u"ID")
                            except KeyError:
                                raise MissingAttributeError(u"ID")
                            try:
                                resource_name = attributes.pop(u"Name")
                            except KeyError:
                                raise MissingAttributeError(u"Name")
                            try:
                                resource_type = attributes.pop(u"Type")
                            except KeyError:
                                raise MissingAttributeError(u"Type")
                            def resource_handler(value):
                                managers.resource_manager.add_resource(
                                    application.id, None,
                                    {"id": resource_id, "name": resource_name, "res_format": resource_type},
                                    base64.b64decode(value))
                            parser.handle_value(name, attributes, resource_handler)
                            # </Resource>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, resources_handler)
                    # </Resources>
                elif name == u"Databases":
                    # <Databases>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    def databases_handler(name, attributes):
                        if name == u"Database":
                            # <Database>
                            try:
                                database_id = attributes.pop(u"ID")
                            except KeyError:
                                raise MissingAttributeError(u"ID")
                            try:
                                database_name = attributes.pop(u"Name")
                            except KeyError:
                                raise MissingAttributeError(u"Name")
                            try:
                                database_type = attributes.pop(u"Type")
                            except KeyError:
                                raise MissingAttributeError(u"Type")
                            database_attributes = {"id": database_id,
                                "name": database_name, "owner": application.id, "type": database_type}
                            if application.id is None:
                                raise SectionMustPrecedeError(u"Information")
                            if database_type == u"xml":
                                def database_handler(value):
                                    managers.database_manager.add_database(application.id,
                                            database_attributes, value)
                                parser.handle_contents(name, attributes, database_handler)
                            elif database_type == u"sqlite":
                                def database_handler(value):
                                    managers.database_manager.add_database(application.id,
                                        database_attributes, base64.b64decode(value))
                                parser.handle_value(name, attributes, database_handler)
                            else:
                                raise UnexpectedAttributeValueError(u"Type")
                            # </Database>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, databases_handler)
                    # </Databases>
                elif name == u"E2VDOM" or name == u"E2vdom":
                    # <E2VDOM>
                    if u"Objects" not in sections:
                        raise SectionMustPrecedeError(u"Objects")
                    unknown_events = {}
                    def e2vdom_handler(name, attributes):
                        if name == u"Events":
                            # <Events>
                            def events_handler(name, attributes):
                                if name == u"Event":
                                    # <Event>  ObjSrcName??? ObjSrcName??? TypeID???
                                    unknown_bindings = []
                                    try:
                                        event_container_id = attributes.pop(u"ContainerID")
                                    except KeyError:
                                        raise MissingAttributeError(u"ContainerID")
                                    try:
                                        # event_container = application.objects[event_container_id]
                                        event_container = containers[event_container_id]
                                    except KeyError:
                                        raise ParsingException(u"Container %s not found" % event_container_id)
                                    try:
                                        event_source_object_id = attributes.pop(u"ObjSrcID")
                                    except KeyError:
                                        raise MissingAttributeError(u"ObjSrcID")
                                    try:
                                        # event_source_object = application.objects.catalog[event_source_object_id]
                                        event_source_object = objects[event_source_object_id]
                                    except KeyError:
                                        raise ParsingException(u"Source object %s not found" % event_container_id)
                                    if event_source_object.container is not event_container:
                                        raise ParsingException(u"Source object %s must have %s container: %s given" %
                                            (event_source_object_id, event_source_object.container.id, event_container.id))
                                    try:
                                        event_name = attributes.pop(u"Name")
                                    except KeyError:
                                        raise MissingAttributeError(u"Name")
                                    event = event_source_object.events.new_sketch(event_name)
                                    try:
                                        # Here "or 0" is the hack to handle Top="" elements
                                        event.top = int(attributes.pop(u"Top") or u"0")
                                    except KeyError:
                                        pass
                                    except ValueError:
                                        raise UnexpectedAttributeValueError(u"Top")
                                    try:
                                        # Here "or 0" is the hack to handle Left="" elements
                                        event.left = int(attributes.pop(u"Left") or u"0")
                                    except KeyError:
                                        pass
                                    except ValueError:
                                        raise UnexpectedAttributeValueError(u"Top")
                                    try:
                                        # Here "or 0" is the hack to handle Left="" elements
                                        event.state = (attributes.pop(u"State") or u"False").lower() in (u"1", u"true")
                                    except KeyError:
                                        pass
                                    def event_handler(name, attributes):
                                        if name == u"Action":
                                            # <Action>
                                            try:
                                                callee_id = attributes.pop(u"ID")
                                            except KeyError:
                                                raise MissingAttributeError(u"ID")
                                            try:
                                                # event.callees.append(application.bindings[callee_id])
                                                event.callees.add(bindings[callee_id])
                                            except KeyError:
                                                try:
                                                    # event.callees.append(application.actions.catalog[callee_id])
                                                    event.callees.add(actions[callee_id])
                                                except KeyError:
                                                    unknown_bindings.append(callee_id)
                                            parser.handle_elements(name, attributes)
                                            # </Action>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    def close_event_handler(name):
                                        if unknown_bindings:
                                            unknown_events[event] = unknown_bindings
                                        else:
                                            # ~event
                                            events.add(event)
                                    parser.handle_elements(name, attributes, event_handler, close_event_handler)
                                    # </Event>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, events_handler)
                            # </Events>
                        elif name == u"Actions":
                            # <Actions>
                            def actions_handler(name, attributes):
                                if name == u"Action":
                                    # <Action>
                                    try:
                                        target_object_id = attributes.pop(u"ObjTgtID")
                                    except KeyError:
                                        raise MissingAttributeError(u"ObjTgtID")
                                    try:
                                        # target_object = application.objects.catalog[target_object_id]
                                        target_object = objects[target_object_id]
                                    except KeyError:
                                        raise ParsingException(u"Target object %s not found" % target_object_id)
                                    try:
                                        binding_name = attributes.pop(u"Name")
                                    except KeyError:
                                        try:
                                            binding_name = attributes.pop(u"MethodName")
                                        except KeyError:
                                            raise MissingAttributeError(u"Name")
                                    try:
                                        binding_id = attributes.pop(u"ID")  # interface_name
                                    except KeyError:
                                        raise MissingAttributeError(u"ID")
                                    try:
                                        # Here "or 0" is the hack to handle Top="" elements
                                        binding_top = int(attributes.pop(u"Top") or u"0")
                                    except KeyError:
                                        pass
                                    except ValueError:
                                        raise UnexpectedAttributeValueError(u"Top")
                                    try:
                                        # Here "or 0" is the hack to handle Left="" elements
                                        binding_left = int(attributes.pop(u"Left") or u"0")
                                    except KeyError:
                                        pass
                                    except ValueError:
                                        raise UnexpectedAttributeValueError(u"Top")
                                    try:
                                        # Here "or 0" is the hack to handle State="" elements
                                        binding_state = (attributes.pop(u"State") or u"False").lower() in (u"1", u"true")
                                    except KeyError:
                                        pass
                                    binding_parameters = OrderedDict()
                                    def action_handler(name, attributes):
                                        if name == u"Parameter":
                                            # <Parameter>
                                            try:
                                                parameter_name = attributes.pop(u"Name")
                                            except KeyError:
                                                try:
                                                    parameter_name = attributes.pop(u"ScriptName")
                                                except KeyError:
                                                    raise MissingAttributeError(u"Name")
                                            def parameter_handler(value): binding_parameters[parameter_name] = value
                                            parser.handle_value(name, attributes, parameter_handler)
                                            # </Parameter>
                                        else:
                                            parser.reject_elements(name)
                                    def close_action_handler(name):
                                        binding = application.bindings.new_sketch(target_object, binding_name, parameters=binding_parameters)
                                        binding.id = binding_id
                                        binding.top = binding_top
                                        binding.left = binding_left
                                        binding.state = binding_state
                                        bindings[binding.id] = binding
                                        # ~binding
                                    parser.handle_elements(name, attributes, action_handler, close_action_handler)
                                    # </Action>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, actions_handler)
                            # </Actions>
                        else:
                            parser.reject_elements(name, attributes)
                    def close_e2vdom_handler(name):
                        for event, unknown_bindings in unknown_events.iteritems():
                            for binding_id in unknown_bindings:
                                # binding = application.bindings.get(binding_id, None)
                                binding = bindings.get(binding_id, None)
                                if binding:
                                    event.callees.add(binding)
                                else:
                                    parser.notify("Unable to find %s target for %s event" % (binding_id, event.name))
                            # ~event
                            events.add(event)
                    parser.handle_elements(name, attributes, e2vdom_handler, close_e2vdom_handler)
                    # </E2VDOM>
                elif name == u"Security":
                    # <Security>
                    if u"Information" not in sections:
                        raise SectionMustPrecedeError(u"Information")
                    def security_handler(name, attributes):
                        if name == u"Groups":
                            # <Groups>
                            def groups_handler(name, attributes):
                                if name == u"Group":
                                    # <Group>
                                    group = VDOM_structure(name=None, description=u"", rights={})
                                    def group_handler(name, attributes):
                                        if name == u"Name":
                                            # <Name>
                                            def name_handler(value): group.name = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, name_handler)
                                            # </Name>
                                        elif name == u"Description":
                                            # <Description>
                                            def description_handler(value): group.description = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, description_handler)
                                            # </Description>
                                        elif name == u"Rights":
                                            # <Rights>
                                            def rights_handler(name, attributes):
                                                if name == u"Right":
                                                    # <Right>
                                                    try:
                                                        target = attributes.pop(u"Target")
                                                    except KeyError:
                                                        raise MissingAttributeError(u"Target")
                                                    try:
                                                        access = map(int, map(string.strip, attributes.pop(u"Access").split(u",")))
                                                    except KeyError:
                                                        raise MissingAttributeError(u"Access")
                                                    except ValueError:
                                                        raise UnexpectedAttributeValueError(u"Access")
                                                    # if target in application.objects.catalog or target == application.id:
                                                    if target in objects or target == application.id:
                                                        group.rights[target] = access
                                                    parser.handle_elements(name, attributes)
                                                    # </Right>
                                                else:
                                                    parser.reject_elements(name, attributes)
                                            parser.handle_elements(name, attributes, rights_handler)
                                            # </Rights>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    def close_group_handler(name):
                                        if group.name is None:
                                            MissingElementError(u"Name")
                                        if not managers.user_manager.name_exists(group.name):
                                            managers.user_manager.create_group(group.name, group.description)
                                        for target, access_list in group.rights.iteritems():
                                            for access in access_list:
                                                managers.acl_manager.add_access(target, group.name, access)
                                    parser.handle_elements(name, attributes, group_handler, close_group_handler)
                                    # </Group>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, groups_handler)
                            # </Groups>
                        elif name == u"Users":
                            # <Users>
                            def users_handler(name, attributes):
                                if name == u"User":
                                    # <User>
                                    user = VDOM_structure(
                                        login=None,
                                        password=None,
                                        firstname=u"",
                                        lastname=u"",
                                        email=u"",
                                        security_level=u"",
                                        member_of=[],
                                        rights={})
                                    def user_handler(name, attributes):
                                        if name == u"Login":
                                            # <Login>
                                            def login_handler(value): user.login = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, login_handler)
                                            # </Login>
                                        elif name == u"Password":
                                            # <Password>
                                            def password_handler(value): user.password = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, password_handler)
                                            # </Password>
                                        elif name == u"FirstName":
                                            # <FirstName>
                                            def firstname_handler(value): user.firstname = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, firstname_handler)
                                            # </FirstName>
                                        elif name == u"LastName":
                                            # <LastName>
                                            def lastname_handler(value): user.lastname = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, lastname_handler)
                                            # </LastName>
                                        elif name == u"Email":
                                            # <Email>
                                            def email_handler(value): user.email = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, email_handler)
                                            # </Email>
                                        elif name == u"SecurityLevel":
                                            # <SecurityLevel>
                                            def securitylevel_handler(value): user.security_level = value.encode(u"utf8")
                                            parser.handle_value(name, attributes, securitylevel_handler)
                                            # </SecurityLevel>
                                        elif name == u"MemberOf":
                                            # <MemberOf>
                                            def memberof_handler(value): user.member_of = \
                                                [member.strip().encode(u"utf8") for member in value.split(u",")] if value else []
                                            parser.handle_value(name, attributes, memberof_handler)
                                            # </MemberOf>
                                        elif name == u"Rights":
                                            # <Rights>
                                            def rights_handler(name, attributes):
                                                if name == u"Right":
                                                    # <Right>
                                                    try:
                                                        target = attributes.pop(u"Target")
                                                    except KeyError:
                                                        raise MissingAttributeError(u"Target")
                                                    try:
                                                        access = map(int, map(string.strip, attributes.pop(u"Access").split(u",")))
                                                    except KeyError:
                                                        raise MissingAttributeError(u"Access")
                                                    except ValueError:
                                                        raise UnexpectedAttributeValueError(u"Access")
                                                    # if target in application.objects.catalog or target == application.id:
                                                    if target in objects or target == application.id:
                                                        user.rights[target] = access
                                                    parser.handle_elements(name, attributes)
                                                    # </Right>
                                                else:
                                                    parser.reject_elements(name, attributes)
                                            parser.handle_elements(name, attributes, rights_handler)
                                            # </Rights>
                                        else:
                                            parser.reject_elements(name, attributes)
                                    def close_user_handler(name):
                                        if user.login is None:
                                            MissingElementError(u"Login")
                                        if user.password is None:
                                            MissingElementError(u"Password")
                                        if not managers.user_manager.name_exists(user.login):
                                            managers.user_manager.create_user(
                                                user.login,
                                                user.password,
                                                user.firstname,
                                                user.lastname,
                                                user.email,
                                                user.security_level)
                                        user_object = managers.user_manager.get_user_object(user.login)
                                        if user_object:
                                            for target, access_list in user.rights.iteritems():
                                                for access in access_list:
                                                    managers.acl_manager.add_access(target, user.login, access)
                                            user_object.member_of = user.member_of
                                        managers.user_manager.sync()
                                    parser.handle_elements(name, attributes, user_handler, close_user_handler)
                                    # </User>
                                else:
                                    parser.reject_elements(name, attributes)
                            parser.handle_elements(name, attributes, users_handler)
                            # </Users>
                        else:
                            parser.reject_elements(name, attributes)
                    parser.handle_elements(name, attributes, security_handler)
                    # </Security>
                else:
                    parser.reject_elements(name, attributes)
            def close_application_handler(name):
                if not sections.get("Information", False):
                    raise MissingSectionError("Information")

                from scripting.executable import select_library_class
                for library in libraries:
                    executable = select_library_class(application.scripting_language)(application, library)
                    executable.compile(store=True)

                for binding in bindings.itervalues():
                    ~binding
                for action in actions.itervalues():
                    ~action
                for event in events:
                    ~event
                for object in objects.itervalues():
                    ~object
                ~application

                # def handle_on_create(container):
                #     for object in container.objects.itervalues():
                #         handle_on_create(object)
                #     managers.dispatcher.dispatch_handler(container, "on_parse") # application
                # for container in application.objects.itervalues(): # pages
                #     handle_on_create(container)
                parser.accept(application)
            parser.handle_elements(name, attributes, application_handler, close_application_handler)
            # </Application>
        else:
            parser.reject_elements(name, attributes)
    return document_handler
