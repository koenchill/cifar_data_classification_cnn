"""Secure FastAPI inference boundary."""

from cifar_cnn.api.app import app_factory, create_app

__all__ = ["app_factory", "create_app"]
