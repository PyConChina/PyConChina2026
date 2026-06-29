import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pycon.settings.dev")
django.setup()

from talk.models import TalkPage
from talk.utils import render_poster

talk = TalkPage.objects.first()
render_poster(talk).show()
