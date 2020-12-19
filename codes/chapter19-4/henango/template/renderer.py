import os

import settings


def render(template_name: str, context: dict):
    template_filename = template_name + ".html"

    template_path = os.path.join(settings.TEMPLATES_DIR, template_filename)

    with open(template_path) as f:
        template = f.read()

    return template.format(**context)
