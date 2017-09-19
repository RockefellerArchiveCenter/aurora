import bagit

from transfer_app.lib import files_helper as FH

class bagChecker():

    def __init__(self,archiveObj):
        self.archiveObj = archiveObj
        self.archive_extracted = self._extract_archive()
        self.archive_path = '/data/tmp/{}'.format(self.archiveObj.bag_it_name) 

    def _extract_archive(self):
        if self.archiveObj.machine_file_type == 'TAR':
            if FH.tar_extract_all(self.archiveObj.machine_file_path):
                return True
        return False

    def _is_generic_bag(self):
        bag = bagit.Bag(self.archive_path)
        return bag.is_valid()

    def _is_rac_bag(self):
        pass

    def bag_passed_all(self):
        if not self.archive_extracted:
            print 'bag didnt pass due to extract error'
            return False

        if not self._is_generic_bag():
            print 'bag didnt pass due to not being valid bag'
            return False

        return True

