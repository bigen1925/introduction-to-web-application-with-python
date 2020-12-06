import views
from henango.urls.resolver import URLPattern

# pathとview関数の対応
url_patterns = [
    URLPattern("/now", views.now),
    URLPattern("/show_request", views.show_request),
    URLPattern("/parameters", views.parameters),
    URLPattern("/user/<name>", views.user),
]
