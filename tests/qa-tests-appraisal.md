# Project Electron QA Tests for Appraisal

These tests are written in [Gherkin](https://github.com/cucumber/cucumber/wiki/Gherkin), a structured language that can be used for both documentation and automated testing of software.

## Feature: automatically apply default rights statements to transfers

	Scenario: default rights statements are applied to the transfer  
		Given source organization exists in Aurora  
			And one or more record types are associated with that organization  
			And default PREMIS-compliant rights exist for that source organization and each record type
		When rights assignment script is run
		Then assign one or more PREMIS-compliant default rights statement based on source organization and record type
			And display rights assignment on transfer detail page
			And route transfer to Appraisal Queue

	Scenario: Rules are missing for applying PREMIS rights statements
		Given source organization exists in Aurora
			And one or more record types are associated with that organization
			And default PREMIS-compliant rights do not exist for that source organization and record type
		When rights assignment script is run
		Then do not assign PREMIS rights statements
			And do not display rights assignment on transfer detail page
			And route transfer to Appraisal Queue

## Feature: Allow appraisal archivists to search and sort transfers  

	Scenario: appraisal archivist searches for transfer by creator
		Given one or more transfers exist in Appraisal Queue UI
		When user enters search into search field
		Then display search results with matching creator  

	Scenario: appraisal archivist searches for transfer by title
		Given one or more transfers exist in Appraisal Queue UI
		When user enters search into search field
		Then display search results with matching title  

	Scenario: appraisal archivist searches for transfer by date transferred
		Given one or more transfers exist in Appraisal Queue UI
		When user enters search into search field
		Then display search results with matching date transferred  

	Scenario: appraisal archivist searches for transfer by record type
		Given one or more transfers exist in Appraisal Queue UI
		When user enters search into search field
		Then display search results with matching record type  

	Scenario: appraisal archivist sorts by creator
		Given one or more** transfers exist in Appraisal Queue UI
		When user clicks on creator column
		Then sort creator column by ascending or descending  

	Scenario: appraisal archivist sorts by title
		Given one or more transfers exist in Appraisal Queue UI
		When user clicks on title column
		Then sort title column by ascending or descending  

	Scenario: appraisal archivist sorts by transferred date
		Given one or more** transfers exist in Appraisal Queue UI
		When user clicks on date transferred column
		Then sort date transferred column by ascending or descending  

	Scenario: appraisal archivist sorts by record type
		Given one or more** transfers exist in Appraisal Queue UI
		When user clicks on record type column
		Then sort record type column by ascending or descending

## Feature: Allow appraisal archivists to add appraisal notes to transfers  

	Scenario: appraisal archivist adds note to transfer
		Given user is an appraisal archivist
			And transfer exists in Appraisal Queue UI
		When user clicks on View Detailed Transfer Information
		Then load detailed transfer info page
			And provide free text field for data entry
			And save information upon save button click  

	Scenario: appraisal archivist edits transfer note
		Given user is an appraisal archivist
			And transfer exists in Appraisal Queue UI
			And transfer already has saved transfer note information
		When user clicks on View Detailed Transfer Information
		Then load detailed transfer info page
			And load free text field with existing transfer note information
			And allow edit of string text in note field
			And save information upon save button click

	Scenario: non-appraisal archivist tries to add note to transfer
		Given user is not an appraisal archivist
			And one or more transfers exist in Appraisal Queue UI
		When user clicks on View Detailed Transfer Information
		Then show detailed transfer info page
			And show appraisal note on page
			And do not allow non-appraisal archivist to update information

## Feature: Allow appraisal archivists to accept or reject transfers  

	Scenario: appraisal archivist accepts a transfer
		Given the appraisal archivist deems transfer is within collecting scope
			And appraisal archivist is on Appraisal Queue UI
		When appraisal archivist clicks accept
		Then accept transfer pop-up box appears
			And appraisal archivist adds and confirms an appraisal note if desired
			And transfer automatically moves to the Accessioning Queue
			And transfer disappears from Appraisal Queue UI
			And user is returned to Appraisal Queue UI

	Scenario: appraisal archivist rejects a transfer
		Given the appraisal archivist deems transfer is out of collecting scope
			And appraisal archivist is on Appraisal Queue UI
		When appraisal archivist clicks reject
		Then reject transfer pop-up box appears
			And appraisal archivist adds and confirms an appraisal note if desired
			And email containing appraisal note is delivered to donor
			And transfer is deleted
			And user is returned to Appraisal Queue UI

## Feature: Allow appraisal archivists to manage default structured rights and acquisition type for organizations  

	Scenario: user edits default rights statements
		Given user has permissions to edit organization information
			And source organization record exists
			And user views UI to edit organization
		When user updates text in rights statement box
		Then user selects corresponding record type that rights statement applies to
			And user updates organization record
			And system stores structured rights statements with organization

	Scenario: appraisal archivist edits acquisition type
		Given user has permissions to edit organization information
			And source organization record exists
			And user views UI to edit organization
		When user selects "acquisition type" from dropdown list
		Then user updates organization record
			And system stores acquisition type information with organization
