from django.core.management.base import BaseCommand
#
from ...main import MainLoop


class Command(BaseCommand):
    def add_arguments(self, parser):
        MainLoop.add_arguments(parser)

    def handle(self, *args, **options):
        MainLoop.handle(*args, **options)
