from setuptools import setup, find_packages

setup(name="gui_messenger_client",
      version="0.0.1",
      description="Gui messenger client",
      author="Demin Dmitry",
      author_email="sampaccs@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
