# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

# Variables and setup routines for RightsStatements

record_types = [
    "administrative records", "board materials",
    "communications and publications", "grant records",
    "annual reports"]
rights_bases = ['Copyright', 'Statute', 'License', 'Other']
basis_data = [
    {
        'rights_basis': 'Copyright',
        'applies_to_type': [1, ],
        'rightsstatementcopyright_set-INITIAL_FORMS': 0,
        'rightsstatementcopyright_set-TOTAL_FORMS': 1,
        'rightsstatementcopyright_set-0-copyright_note': "Test note",
        'rightsstatementcopyright_set-0-copyright_status': 'copyrighted',
        'rightsstatementcopyright_set-0-copyright_jurisdiction': 'us',
    },
    {
        'rights_basis': 'Statute',
        'applies_to_type': [1, ],
        'rightsstatementstatute_set-INITIAL_FORMS': 0,
        'rightsstatementstatute_set-TOTAL_FORMS': 1,
        'rightsstatementstatute_set-0-statute_note': "Test note",
        'rightsstatementstatute_set-0-statute_citation': 'Test statute citation',
        'rightsstatementstatute_set-0-statute_jurisdiction': 'us',
    },
    {
        'rights_basis': 'License',
        'applies_to_type': [1, ],
        'rightsstatementlicense_set-INITIAL_FORMS': 0,
        'rightsstatementlicense_set-TOTAL_FORMS': 1,
        'rightsstatementlicense_set-0-license_note': "Test note",
    },
    {
        'rights_basis': 'Other',
        'applies_to_type': [1, ],
        'rightsstatementother_set-INITIAL_FORMS': 0,
        'rightsstatementother_set-TOTAL_FORMS': 1,
        'rightsstatementother_set-0-other_rights_note': "Test note",
        'rightsstatementother_set-0-other_rights_basis': 'Donor',
    }
]
grant_data = {
    'rightsstatementrightsgranted_set-TOTAL_FORMS': 1,
    'rightsstatementrightsgranted_set-INITIAL_FORMS': 0,
    'rightsstatementrightsgranted_set-0-act': random.choice(['publish', 'disseminate', 'replicate', 'migrate', 'modify', 'use', 'delete']),
    'rightsstatementrightsgranted_set-0-restriction': random.choice(['allow', 'disallow', 'conditional']),
    'rightsstatementrightsgranted_set-0-rights_granted_note': 'Grant note'
}
