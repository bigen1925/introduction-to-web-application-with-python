def render(template_path: str, context: dict):
    with open(template_path) as f:
        template = f.read()

    return template.format(**context)
