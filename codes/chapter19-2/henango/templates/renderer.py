def render(template_path: str, **kwargs):
    with open(template_path) as f:
        template = f.read()

    return template.format(**kwargs)
