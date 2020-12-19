import os

import settings


def render(template_name: str, context: dict):
    template_path = os.path.join(settings.TEMPLATES_DIR, template_name)

    with open(template_path) as f:
        template = f.read()

    return template.format(**context)
