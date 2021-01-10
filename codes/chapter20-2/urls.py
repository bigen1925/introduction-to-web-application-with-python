import views
from henango.urls.pattern import URLPattern

# pathとview関数の対応
url_patterns = [
    URLPattern("/now", views.now),
    URLPattern("/show_request", views.show_request),
    URLPattern("/parameters", views.parameters),
    URLPattern("/user/<user_id>/profile", views.user_profile),
    URLPattern("/set_cookie", views.set_cookie),
    URLPattern("/login", views.login),
    URLPattern("/welcome", views.welcome),
]
