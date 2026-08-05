# GitHub Actions runner on Ubuntu 24.04

This service image packages GitHub Actions Runner `2.334.0` on Ubuntu 24.04.
It is intended for self-hosted runner infrastructure and requires the normal
runner registration environment at container start.

The runner registration token, URL, and organization credentials must be
provided at runtime. They must not be copied into the image or image layers.
