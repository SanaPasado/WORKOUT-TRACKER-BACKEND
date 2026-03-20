"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def landing_page(_request):
        return HttpResponse(
                """
                <!doctype html>
                <html lang=\"en\">
                <head>
                    <meta charset=\"utf-8\" />
                    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                    <title>Workout Tracker Backend</title>
                    <style>
                        body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 40px; line-height: 1.5; }
                        h1 { margin-bottom: 8px; }
                        ul { padding-left: 20px; }
                    </style>
                </head>
                <body>
                    <h1>Workout Tracker Backend</h1>
                    <p>Service is running.</p>
                    <ul>
                        <li><a href=\"/api/\">API Root</a></li>
                        <li><a href=\"/admin/\">Admin</a></li>
                    </ul>
                </body>
                </html>
                """,
                content_type="text/html",
        )


urlpatterns = [
        path('', landing_page, name='landing-page'),
    path('admin/', admin.site.urls),
    path('api/', include('base.urls')),
]
