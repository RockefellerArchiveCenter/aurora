# Example Bags

The following sample bags are needed:

### valid_bag_unzipped
Unzipped bag that validates against all checks

### valid_bag_zipped
Zipped bag that validates against all checks

### large_bag
bag that exceeds 500GB size

### invalid_filëname
bag whose root directory contains a filename with special characters

### contains_virus
bag which contains a file which will trigger virus scanning tools

### missing_bag_declaration
bag missing bagit.txt

### missing_payload_manifest
bag missing mainifest-<alg>.txt

### missing_bag_manifest
bag missing bag-info.txt

### missing_payload_directory
bag missing payload directory

### empty_payload_directory
bag with empty payload directory

### invalid_metadata_file
bag with metadata.json file that is invalid

### missing_required_fields
bag with fields missing in bag-info.txt

### repeating_fields
bag containing repeating non-repeatable metadata fields in bag-info.txt

### invalid_data_type
bag containing metadata element that does not conform to datatype specification

### unauthorized_term
bag containing metadata elements which do not adhere to locally controlled vocabularies

### changed_file
bag containing a file modified after the bag was created
