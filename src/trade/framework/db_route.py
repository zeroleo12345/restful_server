from django.db import models


def base_rule(model: models.Model):
    """
    :param model:
    :return: None for default db; 'db name' for specific database
    """
    return None


class Router:
    def db_for_read(self, model, **hints):
        return base_rule(model)

    def db_for_write(self, model, **hints):
        return base_rule(model)

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
