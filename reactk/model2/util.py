def make_func(name: str, body):
    code = f"def {name}():\n    {body}"
    ns = {}
    exec(code, ns)
    return ns[name]
