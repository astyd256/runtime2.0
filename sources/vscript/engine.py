
import sys, traceback, os.path, re
from copy import copy, deepcopy
from weakref import WeakKeyDictionary
import managers
from utils.mutex import VDOM_named_mutex_auto as auto_mutex
from . import errors, lexemes, syntax
from .variables import variant
from .essentials import exitloop
from .prepare import lexer, parser
from .subtypes import v_nothing
from .wrappers.environment import v_server, v_request, v_response, v_session, v_application
from .wrappers.scripting import v_vdomobject
from . import wrappers


vscript_source_signature=u"<vscript"
vscript_source_string=u"<vscript>"
vscript_wrappers_name="wrappers"

vscript_default_code=compile(u"", vscript_source_string, u"exec")
vscript_default_listing=""
vscript_default_source=[]

vscript_default_action_namespace={
	u"v_server": v_server(),
	u"v_request": v_request(),
	u"v_response": v_response(),
	u"v_session": v_session(),
	u"v_application": v_application()}
vscript_default_environment={
	u"v_this": None,
	u"v_server": None,
	u"v_request": None,
	u"v_response": None,
	u"v_session": None,
	u"v_application": None}

weakuses=WeakKeyDictionary()


for name in dir(wrappers):
	if name.startswith("v_"):
		vscript_default_environment.setdefault(name, vscript_wrappers_name)


def check_exception(source, error, error_type=errors.generic.runtime, quiet=None):
	exclass, exexception, extraceback=sys.exc_info()
	history=traceback.extract_tb(extraceback)
	path_python=sys.prefix
	path_binary=os.path.split(os.path.dirname(sys.argv[0]))[0]
	vbline=error.line if isinstance(error, errors.generic) else None
	if not quiet:
		debug( "- - - - - - - - - - - - - - - - - - - -")
	for path, line, function, st in history:
		if path.startswith(".."):
			path=os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), path))
		# if path==vscript_source_string:
		if path.startswith(vscript_source_signature):
			try:
				st=source[line-1][2]
			except IndexError:
				debug("st IndexError")
				st = None
			try:
				vbline=source[line-1][0] or None
			except IndexError:
				debug("vbline IndexError")
				vbline = None
		elif path.startswith(path_binary):
			path="<server>%s"%path[len(path_binary):]
		elif path.startswith(path_python):
			path="<python>%s"%path[len(path_python):]	
			
		if not quiet:
			debug( (u"%s, line %s%s - %s"%(path, line, ": %s"%st if st else "", function)).encode("utf-8"))
	if not quiet:
		debug( "- - - - - - - - - - - - - - - - - - - -")
	if isinstance(error, errors.generic):
		error.line=vbline
		error.source=error_type
	if not quiet:
		debug(error, console=True)
	del exclass, exexception, extraceback, history
	#managers.log_manager.error_bug(error, "vscript")


def advanced_check_exception(error_type=errors.generic.runtime):
	error_class, error, traceback=sys.exc_info()
	if not isinstance(error, errors.generic):
		return

	vtraceback=[]
	while traceback is not None:
		frame=traceback.tb_frame
		information=frame.f_globals.get("__vscript__")
		if information:
			try:
				lineno=information[traceback.tb_lineno-1][0]
			except:
				lineno=None
			try:
				library=frame.f_globals.get("__name__").partition(".")[2]
			except:
				library=None
			vtraceback.append((library, lineno))
		traceback=traceback.tb_next

	if vtraceback:
		error.traceback=vtraceback
		error.library, error.line=vtraceback[-1]
		error.source=error_type

	del error_class, error, traceback, frame


def vcompile(script=None, let=None, set=None, filename=None, bytecode=1, package=None,
		lines=None, environment=None, use=None, anyway=1, quiet=None, listing=False, safe=None):
	if script is None:
		if let is not None:
			script="result=%s"%let
		elif set is not None:
			script="set result=%s"%set
		else:
			return vscript_default_code, vscript_default_source
	if not safe:
		mutex=auto_mutex("vscript_engine_compile_mutex")
	try:
		source=None
		if not quiet and listing:
			debug("- - - - - - - - - - - - - - - - - - - -")
			for line, statement in enumerate(script.split("\n")):
				debug( (u"  %s      %s"%(unicode(line+1).ljust(4), statement.expandtabs(4))).encode("utf-8"))
		lexer.lineno=1
		try:
			parser.package=package
			parser.environment=vscript_default_environment if environment is None else environment
			source=parser.parse(script, lexer=lexer, debug=0, tracking=0).compose(0)
		finally:
			parser.package=None
			parser.environment=None
		if lines: source[0:0]=((None, 0, line) for line in lines)
		if not quiet and listing:
			debug( "- - - - - - - - - - - - - - - - - - - -")
			for line, data in enumerate(source):
				debug( (u"  %s %s %s%s"%(unicode(line+1).ljust(4),
					unicode("" if data[0] is None else data[0]).ljust(4),
					"    "*data[1], data[2].expandtabs(4))).encode("utf-8"))
			debug( "- - - - - - - - - - - - - - - - - - - -")
		code=u"\n".join([u"%s%s"%(u"\t"*ident, string) for line, ident, string in source])
		if bytecode:
			code=compile(code, filename or vscript_source_string, u"exec") # CHECK: code=compile(code, vscript_source_string, u"exec")
		if use:
			use_code, use_source=vcompile(use, package=package, environment=environment, safe=True)
			weakuses[code]=use_code, use_source
		return code, source
	except errors.generic as error:
		# check_exception(None, error, error_type=errors.generic.compilation, quiet=quiet)
		advanced_check_exception(error_type=errors.generic.compilation)
		if error.line is None:
			error.line=lexer.lineno
			if isinstance(error, errors.unknown_syntax_error):
				position = getattr(parser.symstack[-1], "lexpos", None)
				if position is not None:
					try:
						newline_position=script.rindex("\n", 0, position)
					except ValueError:
						newline_position=0
					character, column=script[position], (position-newline_position) or 1
					error.near=(column, character) if ' '<=character<='~' else column
		if anyway:
			if bytecode: return vscript_default_code, vscript_default_source
			else: return vscript_default_listing, vscript_default_source
		else: raise
	# except errors.python as error:
	# 	check_exception(source, errors.system_error(unicode(error)), error_type=errors.generic.compilation, quiet=quiet)
	# 	raise
	finally:
		if not safe:
			del mutex

def vexecute(code, source, object=None, namespace=None, environment=None, use=None, quiet=None):
	try:
		try:
			if namespace is None:
				namespace={}
			if environment is None:
				namespace[u"v_this"]=v_vdomobject(object) if object else v_nothing
				namespace.update(vscript_default_action_namespace)
			else:
				namespace.update(environment)
			if use:
				use_code, use_source=weakuses[code]
				vexecute(use_code, use_source, namespace=namespace, environment=environment)
			namespace["__vscript__"] = source
			exec code in namespace
		except exitloop:
			exclass, exexception, extraceback=sys.exc_info()
			del exclass, exexception
			raise errors.invalid_exit_statement, None, extraceback
		except AttributeError, error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			# if path==vscript_source_string:
			if path.startswith(vscript_source_signature):
				if not quiet:
					debug( "- - - - - - - - - - - - - - - - - - - -")
					debug( (u"Python (AttributeError): %s"%error.message).encode("utf-8"))
				result=re.search(".+ has no attribute \'(.+)\'", unicode(error))
				if result:
					del exclass, exexception
					raise errors.object_has_no_property(name=result.group(1)), None, extraceback
				else:
					del exclass, exexception, extraceback
					raise
			else:
				del exclass, exexception, extraceback
				raise
		except ValueError as error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			# if path==vscript_source_string:
			if path.startswith(vscript_source_signature):
				if not quiet:
					debug( "- - - - - - - - - - - - - - - - - - - -")
					debug((u"Python (ValueError): %s"%error).encode("utf-8"))
				del exclass, exexception
				raise errors.type_mismatch, None, extraceback
			else:
				del exclass, exexception, extraceback
				raise
		except TypeError as error:
			exclass, exexception, extraceback=sys.exc_info()
			path, line, function, text=traceback.extract_tb(extraceback)[-1]
			# if path==vscript_source_string:
			if path.startswith(vscript_source_signature):
				if not quiet:
					debug("- - - - - - - - - - - - - - - - - - - -")
					debug ((u"Python (TypeError): %s"%error).encode("utf-8"))
				result=re.search("(.+)\(\) (?:takes no arguments)|(?:takes exactly \d+ arguments) \(\d+ given\)", unicode(error))
				if result:
					del exclass, exexception
					raise errors.wrong_number_of_arguments(name=result.group(1)), None, extraceback
				elif re.match("__init__\(\) got an unexpected keyword argument 'set'", unicode(error)):
					del exclass, exexception
					raise errors.illegal_assigment
				else:
					del exclass, exexception
					raise errors.type_mismatch, None, extraceback
			else:
				del exclass, exexception, extraceback
				raise
	except errors.generic as error:
		# check_exception(source, error, quiet=quiet)
		advanced_check_exception()
		raise
	# except errors.python as error:
	# 	check_exception(source, error, quiet=quiet)
	# 	raise

def vevaluate(code, source, object=None, namespace=None, environment=None, use=None, quiet=None, result=None):
	if result is None:
		result=variant()
	if namespace is None:
		namespace={"v_result": result}
	else:
		namespace["v_result"]=result
	vexecute(code, source, object=object, namespace=namespace, environment=environment, use=use, quiet=quiet)
	return namespace["v_result"].subtype
