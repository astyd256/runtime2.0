
import json
from .auxiliary import lookup


def loads(vdomjson, object, catch):
    try:
        actions = json.loads(vdomjson)
    except Exception as error:
        raise Exception("Unable to parse VDOM JSON: %s" % error)

    if not actions:
        return ()

    bindings = []
    for event_declaration, event_actions in actions.iteritems():
        try:
            source_name, event_name = event_declaration.split(":")
        except:
            raise Exception("Invalid event declaration: %s" % event_declaration)

        source = lookup(object, source_name)
        if not source:
            raise Exception("Unable to find object: %s" % source_name)

        event = source.events.new(event_name)
        for action in event_actions:
            if isinstance(action, list):
                try:
                    target_name, action_name = action[0].split(":")
                except:
                    raise Exception("Invalid action declaration: %s" % action[0])

                target = lookup(object, target_name)
                if not target:
                    raise Exception("Can't find object by name: %s" % target_name)

                binding = event.callees.new(target, action_name, parameters=action[1:])
            else:
                binding = event.callees.new(catch, "catchEvent", parameters=("\"%s\"" % action, "evt_param(\"evt_ref\")"))
            bindings.append(binding)

    return bindings
