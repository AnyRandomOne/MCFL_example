import re
import sbfl
import csv

class FaultFactory:
    @staticmethod
    def get_fault(fault_type, start_location, end_location):
        if re.match('change', fault_type) is not None:
            return ChangeFault(start_location, end_location)
        elif re.match('coverage', fault_type) is not None:
            # print('get fault coverage')
            return CoverageFault(start_location, end_location)
        elif re.match('insert', fault_type) is not None:
            return InsertFault(start_location, end_location)
        elif re.match('delete', fault_type) is not None:
            return DeleteFault(start_location, end_location)
        elif re.match('move', fault_type) is not None:
            return ChangeFault(start_location, end_location)
        elif re.match('remove', fault_type) is not None:
            return ChangeFault(start_location, end_location)
        return ChangeFault(start_location, end_location)

class MethodFactory:
    @staticmethod
    def get_fault(fault_type, start_location, end_location):
        return MethodFault(start_location, end_location)

class AbstractFault:
    def __init__(self, start_location, end_location):
        self.start_location = start_location
        self.end_location = end_location
        self.rank = None
        self.compare_rank = None
        self.compare_sus = None
        self.fault_location = None
        self.spectra_found = None
        self.project = None
        self.no = None
        self.suspicious_value = None

    def collect_fault_location(self, collector):
        # return collector.collect(self)
        return None

    def get_fault_location(self):
        return self.fault_location

    def judge_location(self, location):
        return self.fault_location == location

    # compare location for normal faults 
    def judge_compare_location(self, location):
        s = location.split('->')
        if len(s) < 2:
            return False
        return self.fault_location == s[1]

    def set_fault_location(self, collector):
        self.fault_location = self.collect_fault_location(collector)

    def get_type(self):
        return 'abstract'

    def ranked(self):
        return self.rank is not None

    def compare_ranked(self):
        return self.compare_rank is not None

    def to_dict(self):
        return {'project': self.project,
                'no': self.no,
                'type': self.get_type(),
                'location': self.get_fault_location(),
                'rank': self.rank,
                'suspicious_value': self.suspicious_value,
                'compare_rank': self.compare_rank,
                }

    def is_insert(self):
        return False

    def fresh(self):
        self.rank = None
        self.suspicious_value = None

    def set_project_no(self, project, no):
        self.project = project
        self.no = no

class MethodFault(AbstractFault):
    def __init__(self, start_location, end_location):
        super().__init__(start_location, end_location)

    def get_type(self):
        return 'method'

    def judge_location(self, location):
        return self.fault_location == location.split(':')[0]

    def collect_fault_location(self, collector):
        return collector.collect_method(self)

class ChangeFault(AbstractFault):
    def __init__(self, start_location, end_location):
        AbstractFault.__init__(self, start_location, end_location)

    def collect_fault_location(self, collector):
        return collector.collect_change(self)

    def get_type(self):
        return 'change'

class InsertFault(AbstractFault):
    def __init__(self, start_location, end_location):
        AbstractFault.__init__(self, start_location, end_location)
        self.set = False
        self.after = False
        self.before = False

    def collect_fault_location(self, collector):
        return collector.collect_insert(self)

    def get_type(self):
        return 'insert'

    def set_after(self):
        self.after = True
        self.before = False

    def set_before(self):
        self.after = False
        self.before = True

    def clear_status(self):
        self.after = False
        self.before = False

    def is_insert(self):
        return True

    def judge_location(self, location):
        if self.set:
            return False
        if type(self.fault_location) is not list:
            return self.fault_location == location
        elif self.after:
            return self.fault_location[1] == location
        elif self.before:
            return self.fault_location[0] == location
        else:
            if self.fault_location[0] == location:
                self.set = True
                return True
            elif self.fault_location[1] == location:
                self.set = True
                return True
            else:
                return False

    def judge_compare_location(self, location):
        # do not solve the situation with treat the fault_location as list, as it is not used with compare_rank function
        last_location = self.fault_location.split('->')[-1]
        return location == last_location

    def fresh(self):
        self.set = False
        super().fresh()

class CoverageFault(InsertFault):
    def __init__(self, start_location, end_location):
        AbstractFault.__init__(self, start_location, end_location)

    def collect_fault_location(self, collector):
        # print('collectr coverage fault: %s' % collector.collect_coverage(self))
        return collector.collect_coverage(self)

    def get_type(self):
        return 'coverage'

class DeleteFault(AbstractFault):
    def __init__(self, start_location, end_location):
        AbstractFault.__init__(self, start_location, end_location)

    def collect_fault_location(self, collector):
        return collector.collect_delete(self)

    def get_type(self):
        return 'delete'

class NormalCollector:
    def collect_change(self, change_fault):
        return change_fault.start_location

    def collect_delete(self, delete_fault):
        return delete_fault.start_location

    def collect_coverage(self, coverage_fault):
        # return coverage_fault.start_location
        return coverage_fault.end_location

    def collect_insert(self, insert_fault):
        return sbfl.integrate_location(
            insert_fault.start_location, insert_fault.end_location)

    def collect_method(self, method_fault):
        return method_fault.start_location.split(':')[0]

class ControlCollector(NormalCollector):
    def collect_insert(self, insert_fault):
        return insert_fault.end_location

class ForwardCollector(ControlCollector):
    def collect_insert(self, insert_fault):
        return insert_fault.start_location

class BothSideCollector(NormalCollector):
    def collect_insert(self, insert_fault):
        return [insert_fault.start_location,
                insert_fault.end_location]

class CoverageToInsertCollector(NormalCollector):
    def collect_coverage(self, coverage_fault):
        #print('collect coverage: %s' % sbfl.integrate_location(
        #    coverage_fault.start_location, coverage_fault.end_location))
        return sbfl.integrate_location(
                coverage_fault.start_location, coverage_fault.end_location)

class CoverageBothCollector(BothSideCollector):
    def collect_coverage(self, coverage_fault):
        return [coverage_fault.start_location,
                coverage_fault.end_location]

dict_collector = {
        'end_location': ControlCollector(),
        'start_location': ForwardCollector(),
        'both_location': BothSideCollector(),
        'coverage_to_insert': CoverageToInsertCollector(),
        'coverage_both': CoverageBothCollector(),
        }

def analyze_fault_location(version, collector, bug_list=None, factory=FaultFactory):
    if bug_list is None:
        bug_list = return_bug_list(version)
    fault_list = []
    for bug in bug_list:
        fault_now = factory.get_fault(bug['error_type'], bug['start_location'], bug['end_location'])
        fault_now.set_fault_location(collector)
        fault_list.append(fault_now)
        fault_now.set_project_no(version.name(), int(version.no()))
    return fault_list

def return_bug_list(version):
    path = version.fault_location()
    reader = csv.DictReader(open(path))
    result = []
    for row in reader:
        if int(row['no']) == int(version.no()):
            result.append(row)
        # because the faults are organized sequently.
        if int(row['no']) > int(version.no()):
            break
    return result


