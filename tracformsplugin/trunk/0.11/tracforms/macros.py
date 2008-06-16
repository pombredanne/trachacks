
from trac.wiki.macros import WikiMacroBase
from trac.wiki.formatter import Formatter
import sys, StringIO, re, traceback, cgi, time
from iface import TracFormDBUser

argRE = re.compile('\s*(".*?"|\'.*?\'|\S+)\s*')
tfRE = re.compile('\['
    'tf(?:\.([a-zA-Z_]+?))?'
    '(?::([^\]]*))?'
    '\]')

class TracFormMacro(WikiMacroBase, TracFormDBUser):
    """
    Docs for TracForm macro...
    """

    def expand_macro(self, formatter, name, args):
        processor = TracFormProcessor(self, formatter, name, args)
        return processor.execute()

class TracFormProcessor(object):
    # Default state (beyond what is set in expand_macro).
    showErrors = True
    page = None
    default_op = 'value'
    needs_submit = True

    def __init__(self, macro, formatter, name, args):
        self.macro = macro
        self.formatter = formatter
        self.args = args
        self.name = name

    def execute(self):
        formatter = self.formatter
        args = self.args
        name = self.name

        # Look in the formatter req object for evidence we are executing.
        self.subform = getattr(formatter.req, type(self).__name__, False)
        if not self.subform:
            setattr(formatter.req, type(self).__name__, True)

        # Remove leading comments and process commands.
        textlines = []
        errors = []
        srciter = iter(args.split('\n'))
        for line in srciter:
            if line[:1] == '#':
                # Comment or operation.
                line = line.strip()[1:]
                if line[:1] == '!':
                    # It's a command, parse the arguments...
                    args = list(self.getargs(line[1:]))
                    if len(args):
                        cmd = args.pop(0)
                        fn = getattr(self, 'cmd_' + cmd.lower(), None)
                        if fn is None:
                            errors.append(
                                'ERROR: No TracForm command "%s"' % cmd)
                        else:
                            try:
                                fn(*args)
                            except Exception, e:
                                errors.append(traceback.format_exc())
            else:
                if self.showErrors:
                    textlines.extend(errors)
                textlines.append(line)
                textlines.extend(srciter)

        # Determine our destination context and load the current state.
        if self.page is None:
            self.page = formatter.req.path_info
        self.context = self.page
        state = self.macro.get_tracform_state(self.context)
        self.state = cgi.parse_qs(state or '')
        (self.form_id, self.form_context,
            self.form_updater, self.form_updated_on,
            self.form_keep_history, self.form_track_fields) = \
            self.macro.get_tracform_meta(self.context)

        # Wiki-ize the text, this will allow other macros to execute after
        # which we can do our own replacements within whatever formatted
        # junk is left over.
        text = self.wiki('\n'.join(textlines))

        # Keep replacing tf: sections until there are no more
        # replacements.  On each substitution, wiki() is called on the
        # result.
        self.updated = True
        while self.updated:
            self.updated = False
            text = tfRE.sub(self.process, text)

        # Wrap the entire result with a form, unless we're within an existing
        # form.  If necessary, add a submit button.
        if not self.subform:
            submit = ''
            if self.needs_submit:
                submit = '<INPUT type="submit">'
            dest = formatter.req.href('/formdata/update')
            text = ''.join(str(item) for item in (
                '<FORM method="POST" action="' + dest + '">', text,
                '<INPUT type="hidden" name="__basever__" value="',
                    self.form_updated_on, '">',
                '<INPUT type="hidden" name="__context__" value="',
                    self.context, '">',
                '<INPUT type="hidden" name="__backpath__" value="',
                    formatter.req.href(formatter.req.path_info), '">',
                '<INPUT type="hidden" name="__FORM_TOKEN" value="',
                    formatter.req.form_token, '">',
                submit, '</FORM>') if str(item))

        return text

    @staticmethod
    def getargs(argstr):
        for arg in argRE.findall(argstr or ''):
            if arg[:1] in '"\'':
                yield arg[1:-1]
            else:
                yield arg

    def cmd_errors(self, show):
        self.showErrors = show.upper() in ('SHOW', 'YES')

    def cmd_page(self, page):
        if page.upper() in ('NONE', 'DEFAULT', 'CURRENt'):
            self.page = None
        else:
            self.page = page

    def cmd_default(self, default):
        self.default_op = default

    def wiki(self, text):
        out = StringIO.StringIO()
        Formatter(self.formatter.env, self.formatter.context).format(text, out)
        return out.getvalue()

    def process(self, m):
        self.updated = True
        op, argstr = m.groups()
        op = op or self.default_op
        args = tuple(self.getargs(argstr))
        fn = getattr(self, 'op_' + op.lower(), None)
        if fn is None:
            return 'ERROR: No TracForm operation "%s"' % str(op)
        else:
            try:
                if op[:5] == 'wikiop_':
                    return self.wiki(str(fn(*args)))
                else:
                    return str(fn(*args))
            except Exception, e:
                return '<PRE>' + traceback.format_exc() + '</PRE>'

    def op_test(self, *args):
        return repr(args)

    def wikiop_value(self, field):
        return 'VALUE=' + field

    def op_checkbox(self, field):
        field, value = (field.split('//', 1) + [None])[:2]
        current = self.state.get(field)
        if value is not None:
            if isinstance(current, (list, tuple)):
                checked = value in current
            else:
                checked = value == current
        else:
            checked = bool(current)
        return ("<INPUT type='checkbox' name='%s'" % field +
                (value and (' value="' + value + '"') or '') +
                (checked and ' checked' or '') +
                '>')

    def op_radio(self, field, *values):
        current = self.state.get(field)
        for value in values:
            return ("<INPUT type='radio' name='%s'" % field +
                    (current == value and ' selected' or '') +
                    '>')

    def op_context(self):
        return str(self.context)

    def op_who(self, field):
        who = self.macro.get_tracform_fieldinfo(
            self.context, field)[0] or 'unknown'
        return who
        
    def op_when(self, field, format='%m/%d/%Y %H:%M:%S'):
        when = self.macro.get_tracform_fieldinfo(self.context, field)[1]
        if when is not None:
            when = time.strftime(format, time.localtime(when))
        return when

    def op_id(self):
        return id(self)

    def op_subform(self):
        return self.subform

    def op_form_id(self):
        return self.form_id

    def op_form_context(self):
        return self.form_context

    def op_form_updater(self):
        return self.form_updater

    def op_form_updated_on(self, format='%m/%d/%Y %H:%M:%S'):
        return time.strftime(format, time.localtime(self.form_updated_on))

