# -*- mode:makefile; coding:utf-8 -*-

# Copyright (c) 2024 Red Hat All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


pre-commit: 
	pre-commit install

pre-commit-update:
	pre-commit autoupdate

code-format:
	pre-commit run yapf --all-files

code-lint:
	pre-commit run flake8 --all-files

pylint:
	pylint example

pylint-test:
	pylint tests --rcfile=.pylintrc_tests

check-for-changes:
	python scripts/have_files_changed.py -u