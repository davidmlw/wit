install_root := $(PREFIX)
version := $(shell git describe --tags --dirty)
install_dir := $(install_root)/$(version)

install:
	mkdir -p $(install_dir)
	echo $(version) > $(install_dir)/__version__
	rsync -ar --include=wit --include='*.py' --exclude='t/' --exclude='__pycache__/' --exclude='*.pyc' --exclude='.*' --exclude='mypy.ini' --exclude='Makefile' . $(install_dir)
