# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import RequestFactory, TestCase
from django.core.urlresolvers import reverse
from orgs.accession.views import AccessionView, AccessionRecordView


class AccessionGroupTest(TestCase):

    def setUp(self):
        # set up dirs
        self.org = set_up_org('Rockefeller Archive Center')
        self.user = set_up_user(self.org, 'accessioning_archivists')
        self.factory = RequestFactory()
        pass

    def tearDown(self):
        # remove dirs
        pass

    def test_group_by_identifier_in_list(self):
        bag_names = ['valid_bag_identifier1', 'valid_bag_identifier2']
        for name in bag_names:
            # TODO: add process_status to archive setup
            set_up_archive(name, 70)
        request = self.factory.get(reverse('accession-main'))
        request.user = self.user
        response = AccessionView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['uploads']), 1)

    def test_group_by_identifier_in_record(self):
        bag_names = ['valid_bag_identifier1', 'valid_bag_identifier2']
        archives = []
        for name in bag_names:
            # TODO: add process_status to archive setup
            arc = set_up_archive(name, 70)
            archives.append(arc.id)
        request = self.factory.get(reverse('accession-record'), {'transfers': archives})
        request.user = self.user
        response = AccessionRecordView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        # form valid
        self.assertEqual(len(response.context['uploads']), 1)

# Scenario: transfers related to each other via source organization, record creator, and record type are grouped into the same accession
##  valid_bag_ford_grants, valid_bag_ford_grants3, valid_bag_ford_grants4
# 	Given multiple transfers match on source organization
# 		And record creator matches
# 		And record type matches
# 		And transfers have been approved by an appraisal archivist
# 	When Accessioning Queue UI is loaded
# 	Then transfers are grouped together
# 		And displayed as single accession in Accessioning Queue UI
#
# Scenario: transfers related to each other via record creator and record type are not grouped into the same accession
##  valid_bag and valid_bag_rockefeller
# 	Given multiple transfers do not match on source organization
# 		And record creator matches
# 		And record type matches
# 		And transfers have been approved by an appraisal archivist
# 	When Accessioning Queue UI is loaded
# 	Then transfers are not grouped into single accession
# 		And multiple accessions are displayed in the Accessioning Queue UI
#
# Scenario: transfers related to each other via source organization and record type are not grouped into the same accession
##  valid_bag_ford_grants and valid_bag_ford_grants2
# 	Given multiple transfers match on source organization
# 		And record creator does not match
# 		And record type matches
# 		And transfers have been approved by an appraisal archivist
# 	When Accessioning Queue UI is loaded
# 	Then transfers are not grouped into single accession
# 		And multiple accessions are displayed in the Accessioning Queue UI
#
# Scenario: transfers related to each other via source organization and record creator are not grouped into the same accession
##  valid_bag_ford_grants and valid_bag_ford_communications
# 	Given multiple transfers match on source organization
# 		And record creator matches
# 		And record type does not match
# 		And transfers have been approved by an appraisal archivist
# 	When Accessioning Queue UI is loaded
# 	Then transfers are not grouped into single accession
# 		And multiple accessions are displayed in the Accessioning Queue UI
#
# Scenario: transfers not related to each other via source organization, record creator, and record type are not grouped into the same accession
##  valid_bag_ford_grants, valid_bag_ford_grants3, valid_bag_ford_grants4 BUT ADDRESS PROCESSING STATUS
# 	Given multiple transfers match on source organization
# 		And record creator matches
# 		And record type matches
# 		And transfers have not been approved by an appraisal archivist
# 	When Accessioning Queue UI is loaded
# 	Then transfers are not grouped into single accession
# 		And transfers are not displayed in the Accessioning Queue UI


# Feature: Allow accessioning archivists to review or edit accession records
# Scenario: accessioning archivist reviews accession records
# 	Given accessioning archivist has permission to view Accessioning Queue UI
# 	When archivist selects "Accession" in Accessioning Queue UI
# 	Then open Accession Approval view
# 		And autopopulate accession record fields
# 		And allow archivist to view and read contents of each field
#
# Scenario: accessioning archivist edits accession records
# 	Given accessioning archivist has permission to view Accessioning Queue UI
# 	When archivist selects "Accession" in Accessioning Queue UI
# 	Then open Accession Approval window
# 		And autopopulate accession record fields
# 		And allow archivist to edit select accession record fields
# 		And allow archivist to save updated accession


# Feature: Allow accessioning archivists to approve accession records
# Scenario: accessioning archivist approves accession records
# 	Given accessioning archivist has permission to view Accessioning Queue UI
# 	When archivist selects "Accession" in Accessioning Queue UI
# 	Then open Accession Approval window
# 		And autopopulate accession record fields
# 		And allow archivist to enter target resource record
# 		And allow archivist to edit accession record fields
# 		And allow archivist to save updated accession
# 		And remove accession from Accessioning Queue UI
# 		And split single accession into individual transfers

## USER AUTHORIZATION??


# Feature: Validate target resource record field in Aurora Accession Record UI
# Scenario: an archivist types name of existing resource record
# 	Given target resource record exists in ArchivesSpace
# 	When archivist starts typing the title or identifier of that resource record
# 	Then name of resource record appears as an option to select
# 		And archivist selects the name of the appropriate resource record
#
# Scenario: an archivist types name of resource record that does not exist
# 	Given target resource record does not exist in ArchivesSpace
# 	When archivist starts typing the title or identifier of that resource record
# 	Then name of resource record does not appear as an option to select
# 		And archivist is not able to save the accession record


# Feature: Validate agents in Aurora Accession Record UI
# Scenario: Source-Organization names matching existing ArchivesSpace agent records are marked as verified
# 	Given a string value exists for the Source-Organization key
# 		And that string can be matched to the name of an existing agent in ArchivesSpace
# 	When accessioning archivist selects "Accession" in Accession Queue UI
# 	Then query ArchivesSpace for a matching name agent
# 		And returns the URI for that agent
# 		And display the Source-Organization as a verified name in the Accession Approval window
#
# Scenario: Record-Creators names matching existing ArchivesSpace agent records are marked as verified
# 	Given a string value exists for one or more Record-Creators keys
# 		And that string can be matched to the name of an existing agent in ArchivesSpace
# 	When accessioning archivist selects "Accession" in Accession Queue UI
# 	Then query ArchivesSpace for a matching name agent
# 		And returns the URI for that agent
# 		And display the Record-Creator as a verified name in the Accession Approval window
#
# Scenario: Source-Organization names which do not match existing ArchivesSpace agent records are marked as unverified
# 	Given a string value exists for the Source-Organization key
# 		And that string cannot be matched to the name of an existing agent in ArchivesSpace
# 	When accessioning archivist selects "Accession" in Accession Queue UI
# 	Then query ArchivesSpace for a matching name agent
# 		And display the Source-Organization as an unverified name in the Accession Approval window
#
# Scenario: Record-Creators which do not match existing ArchivesSpace agent records are marked as unverified
# 	Given a string value exists for one or more Record-Creators key
# 		And that string cannot be matched to the name of an existing agent in ArchivesSpace
# 	When accessioning archivist selects "Accession" in Accession Queue UI
# 	Then query ArchivesSpace for a matching name agent
# 		And display that Record-Creators as an unverified name in the Accession Approval window


# Feature: Add metadata about individual transfers in an accession to an existing resource record in ArchivesSpace
# Scenario: add metadata about individual transfers in an accession to an existing resource record in ArchivesSpace
# 	Given one or more transfers have been grouped into an accession record
# 		And a valid resource record has been selected
# 	When an accession record is created in ArchivesSpace
# 	Then metadata about each transfer is included in individual file-level components in the target resource record
# 		And that metadata is grouped together under a grouping component in the target resource record
# 		And data from bag-info.txt maps correctly to ArchivesSpace


# Feature: Allow external application to update transfer status
# Scenario: Update transfer status in Aurora
# 	Given an object has passed through the appraisal and accessioning workflows successfully
# 	When the object is stored in Fedora
# 	Then the transfer status is updated to "accessioned" in Aurora
# 		And a success notification is sent to user who uploaded the transfer
