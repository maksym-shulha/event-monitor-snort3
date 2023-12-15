reputation =
{
    blocklist = BLACK_LIST_PATH .. '/default.blocklist'
}

ips =
{
    enable_builtin_rules = true,
    include = RULE_PATH .. "/pulledpork.rules",
    variables = default_variables
}

suppress =
{
    { gid = 116, sid = 6 },
    { gid = 112, sid = 1 }
}

alert_json = 
{
    file = true,
    limit = 1024,
    fields = 'seconds action dst_addr dst_port msg proto sid rev gid src_addr src_port',
}
