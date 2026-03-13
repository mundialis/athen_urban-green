#!/bin/sh
########################################################################
#
# MODULE:       setup_eodag.sh
#
# AUTHOR(S):    Jonas Pischke
#
# PURPOSE:      This script inserts credentials from .env into EODAG
#               configuration (eodag.yml).
#
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
########################################################################

mkdir -p ~/.config/eodag
cat <<EOF > ~/.config/eodag/eodag.yml
# Copyright 2018, CS GROUP - France, https://www.csgroup.eu/
#
# This file is part of EODAG project
#     https://www.github.com/CS-SI/EODAG
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
cop_dataspace:
    priority: 3
    search: # Search parameters configuration
    download:
        extract:
        output_dir:
    auth:
        credentials:
            username: ${EODAG_USER}
            password: "${EODAG_PW}"
EOF