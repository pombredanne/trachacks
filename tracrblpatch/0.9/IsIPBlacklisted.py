from trac import rbl

def execute(hdf, args, env):
	return "%s ist blacklisted: %s (%s)" % (args, rbl.is_blacklisted(args.strip(), env.config.get), env.config.get("trac", "rbl"))
