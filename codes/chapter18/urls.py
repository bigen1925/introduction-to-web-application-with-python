import views

# pathとview関数の対応
URL_VIEW = {
    "/now": views.now,
    "/show_request": views.show_request,
    "/parameters": views.parameters,
    "/user/<user_id>/profile": views.user_profile,
}
