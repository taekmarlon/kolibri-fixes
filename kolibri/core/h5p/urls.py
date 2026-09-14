from django.urls import re_path

from .proxy import H5PProxyView

urlpatterns = [
    re_path(r"^(?P<path>.*)$", H5PProxyView.as_view(), name="h5p_proxy"),
]
