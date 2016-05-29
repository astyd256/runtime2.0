
import utils.exception
from . import errors
from .subtypes.error import error


v_genericerror=error(errors.python)
v_servererror=error(utils.exception.VDOM_exception)
v_scripterror=error(errors.generic)
v_notimplementederror=error(errors.not_implemented)
v_variableisundefinederror=error(errors.variable_is_undefined)
v_nameredefinederror=error(errors.name_redefined)
v_divisionbyzero=v_divisionbyzeroerror=error(errors.division_by_zero)
v_overflow=v_overflowerror=error(errors.overflow)
v_objecthasnopropertyerror=error(errors.object_has_no_property)
v_subscriptoutofrange=v_subscriptoutofrangeerror=error(errors.subscript_out_of_range)
v_typemismatcherror=error(errors.type_mismatch)
v_objectrequirederror=error(errors.object_required)
v_illegalassigmenterror=error(errors.illegal_assigment)
v_wrongnumberofargumentserror=error(errors.wrong_number_of_arguments)
v_invalidprocedurecallerror=error(errors.invalid_procedure_call)
