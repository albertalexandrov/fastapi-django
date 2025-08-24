import importlib
import os

from fastapi_django.conf import global_settings

ENVIRONMENT_VARIABLE = "FASTAPI_DJANGO_SETTINGS_MODULE"
empty = object()


class LazySettings:
    def __init__(self):
        self._wrapped = empty

    def _setup(self, name=None):
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE, "settings")
        if not settings_module:
            raise ValueError("не сконфигурировано")

        self._wrapped = Settings(settings_module)

    def __getattr__(self, name):
        if (_wrapped := self._wrapped) is empty:
            self._setup(name)
            _wrapped = self._wrapped
        val = getattr(_wrapped, name)
        if name in {"MEDIA_URL", "STATIC_URL"} and val is not None:
            val = self._add_script_prefix(val)
        elif name == "SECRET_KEY" and not val:
            raise ValueError("The SECRET_KEY setting must not be empty.")

        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        if name == "_wrapped":
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        """Delete a setting and clear it from cache if needed."""
        super().__delattr__(name)
        self.__dict__.pop(name, None)

    @property
    def configured(self):
        """Return True if the settings have already been configured."""
        return self._wrapped is not empty

    def __dir__(self):
        if self._wrapped is empty:
            self._setup()
        return dir(self._wrapped)

    def extend(self, settings_module=None):
        mod = importlib.import_module(settings_module)
        for setting in dir(mod):
            if setting.isupper() and not hasattr(self, setting):
                value = getattr(mod, setting)
                setattr(self, setting, value)
        return self


class Settings:
    def __init__(self, settings_module):
        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module
        mod = importlib.import_module(self.SETTINGS_MODULE)

        tuple_settings = (
            "ALLOWED_HOSTS",
            "INSTALLED_APPS",
            "TEMPLATE_DIRS",
            "LOCALE_PATHS",
            "SECRET_KEY_FALLBACKS",
        )
        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                if setting in tuple_settings and not isinstance(setting_value, list | tuple):
                    raise ValueError(f"The {setting} setting must be a list or a tuple.")
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.SETTINGS_MODULE}">'


settings = LazySettings()
