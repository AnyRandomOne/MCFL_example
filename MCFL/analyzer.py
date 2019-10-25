import sbfl
import Version
import csv
import numpy as np
import math
# import fault

#PRINT_VERSION = False
PRINT_VERSION = True

dict_exclude_no = {
        'Lang': set({'23', '25', '32', '56'}),
        'Closure': set({'20', '28', '58', '119'}),
        'Time': set({'11', '23'}),
        'Mockito': set({'5', '26'}),
        'Chart': set({'23', '26'}),
        'Math': set({'12', '104',} ),
        }

def if_exclude(project, no):
    return no in dict_exclude_no.get(project, set({}))

def count_fault_rank_average(fault_list, spectra_list_sorted, version):
    count_rank(fault_list, spectra_list_sorted, set([]))

def count_fault_rank_exclude(fault_list, spectra_list_sorted, version):
    count_rank(fault_list, spectra_list_sorted, set(version.return_spectra_exclude()))

class Controller:
    def __init__(self, fault_list):
        self.fault_left = len(fault_list)
        self.rank = 0
        # rank_count: the rank ignore the exclude ones
        self.rank_count = 0
        self.fault_to_set = []

    def clear_temp(self):
        self.fault_left -= len(self.fault_to_set)
        self.fault_to_set = []
        self.rank = self.rank_count
        return self.fault_left == 0

    def set_rank(self, last_value):
        for fault_now in self.fault_to_set:
            # use the average rank
            # fault_now.rank = (i-1+rank)/2
            fault_now.rank = (self.rank_count-1+self.rank)/2
            fault_now.suspicious_value = last_value
            print('fault: %s %s' % (fault_now.rank, fault_now.suspicious_value))

    def rank_fault(self, fault_list, spectra_list_sorted, i):
        for fault_now in fault_list:
            # if fault_now.get_fault_location() == spectra_list_sorted[i].name:
            if fault_now.judge_location(spectra_list_sorted[i].name):
                # print('find fault')
                fault_now.spectra_found = spectra_list_sorted[i]
                self.fault_to_set.append(fault_now)

    def need_end(self):
        return len(self.fault_to_set) != 0

class CompareController(Controller):
    def __init__(self, fault_list):
        Controller.__init__(self, fault_list)
        self.compare_left = len(fault_list)
        self.compare_to_set = []

    def clear_temp(self):
        no_fault = Controller.clear_temp(self)
        self.compare_left -= len(self.compare_to_set)
        self.compare_to_set = []
        return self.compare_left == 0 and no_fault

    def set_rank(self, last_value):
        Controller.set_rank(self, last_value)
        for fault_now in self.compare_to_set:
            fault_now.compare_rank = (self.rank_count-1+self.rank)/2
            fault_now.compare_sus = last_value
            print('compare: %s %s' % (fault_now.compare_rank,
                fault_now.compare_sus))

    def rank_fault(self, fault_list, spectra_list_sorted, i):
        Controller.rank_fault(self, fault_list, spectra_list_sorted, i)
        for fault_now in fault_list:
            if fault_now.judge_compare_location(spectra_list_sorted[i].name):
                self.compare_to_set.append(fault_now)

    def need_end(self):
        return len(self.fault_to_set) + len(self.compare_to_set) != 0

def count_fault_compare(fault_list, spectra_list_sorted, version):
    count_rank(fault_list, spectra_list_sorted, set(version.return_spectra_exclude()), control_type=CompareController)

def count_rank(fault_list, spectra_list_sorted, exclude_set,
        control_type=Controller):
    if len(spectra_list_sorted) == 0:
        print('no spectra in')
        return
    if len(fault_list) == 0:
        print('no fault in')
        return
    # fault_to_search = fault_list.copy()
    controller = control_type(fault_list)
    last_value = spectra_list_sorted[0].get_suspicious_value()
    # fault_to_set = []
    #print(spectra_list_sorted[0].name)
    #print(fault_list[0].get_fault_location())
    for fault_now in fault_list:
        # print(fault_now.fault_location)
        fault_now.fresh()
    for i in range(0, len(spectra_list_sorted)):
        if spectra_list_sorted[i].get_suspicious_value() != last_value:
            controller.set_rank(last_value)
            if controller.clear_temp():
                return
            last_value = spectra_list_sorted[i].get_suspicious_value()
        controller.rank_fault(fault_list, spectra_list_sorted, i)
        if not spectra_list_sorted[i].name in exclude_set:
            controller.rank_count += 1
    #if len(controller.fault_to_set) != 0:
    if controller.need_end():
        controller.set_rank(last_value)

def count_fault_after(fault_list, spectra_list_sorted, version, exclude):
    for fault_now in fault_list:
        if fault_now.is_insert():
            fault_now.set_after()
    exclude_list = version.return_spectra_exclude() if exclude else []
    count_rank(fault_list, spectra_list_sorted, set(exclude_list))
    fault_left = []
    for fault_now in fault_list:
        # print(fault_now)
        if fault_now.is_insert() and ((not fault_now.ranked()) or 
                fault_now.rank / (len(spectra_list_sorted)-len(exclude_list)) >= 0.50):
            # print(fault_now)
            fault_now.set_before()
            fault_left.append(fault_now)
    # print('left fault: %d' % len(fault_left))
    count_rank(fault_left, spectra_list_sorted, set(exclude_list))
    for fault_now in fault_list:
        if fault_now.is_insert():
            fault_now.clear_status()

def count_fault_after_no_exclude(fault_list, spectra_list_sorted, version):
    count_fault_after(fault_list, spectra_list_sorted, version, False)

def count_fault_after_exclude(fault_list, spectra_list_sorted, version):
    count_fault_after(fault_list, spectra_list_sorted, version, True)
                
dict_ranker = {
        'avg': count_fault_rank_average,
        'exclude': count_fault_rank_exclude,
        'after': count_fault_after_exclude,
        'pure_after': count_fault_after_no_exclude,
        'compare': count_fault_compare,
        }

    
def analyze(judgement, spectra_list, fault_list, to_exclude):
    return judgement_dict[judgement](
            spectra_list, fault_list, to_exclude)

def examine_fraction(spectra_list, fault_list, to_exclude):
    spectra_num = len(spectra_list) - len(to_exclude)
    #if exclude_blank:
    #    spectra_num -= len(version.return_spectra_exclude())
    #print([fault_now.rank for fault_now in fault_list])
    #for fault_now in fault_list:
    #    if not fault_now.ranked():
    #        return 'not found'
    result_list = []
    for fault_now in fault_list:
        # print(fault_now.get_fault_location())
        if fault_now.ranked():
            result_list.append(fault_now)
    if len(result_list) == 0:
        print('not found')
        return 'not found'
    max_rank = max([fault_now.rank for fault_now in result_list])
    print('spectra num: %s; max_num: %s' % (spectra_num, max_rank))
    # print(len(fault_list))
    return max_rank / spectra_num

def examine_fraction_first_line(spectra_list, fault_list):
    spectra_num = len(spectra_list)
    result_list = []
    for fault_now in fault_list:
        if fault_now.ranked():
            result_list.append(fault_now)
    if len(result_list) == 0:
        return 'not found'
    min_rank = min([fault_now.rank for fault_now in result_list])
    print(spectra_num)
    print(len(fault_list))
    return min_rank / spectra_num

judgement_dict = {
    'EXAM': examine_fraction,
    'SpecialEXAM': examine_fraction_first_line,
}

def analyze_experiment(analyzer_list, dict_experiment):
    if dict_experiment.get('need_spectra_number', None) is not None:
        # dict_experiment['spectra_number'] = Version.return_spectra_num_dict()
        dict_experiment['spectra_number'] = Version.dict_spectra_number[dict_experiment['need_spectra_number']]
    for experiment_no in dict_experiment.get('experiment_list', []):
        experiment = Version.Experiment(experiment_no)
        for formula in dict_experiment.get('formula_list', []):
            dict_experiment['formula'] = formula
            dict_experiment['analyze_list'] = experiment.return_analyze(formula)
            dict_experiment['fault_list'] = experiment.return_fault(formula)
            for analyzer in analyzer_list:
                if dict_experiment.get('split', False):
                    analyzer.split_analyze(experiment, dict_experiment)
                else:
                    analyzer.analyze(experiment, dict_experiment)

class Analyzer:
    def __init__(self, analyze_type, exclude):
        self.analyze_type = analyze_type
        self.exclude = exclude 

    def analyze(self, experiment, dict_experiment):
        print('%s, %s: %s %s' % (
            experiment, dict_experiment['formula'], self.analyze_type, 
            'not exclude' if not self.exclude else ''))
        self.work(experiment, dict_experiment)

    def work(self, experiment, dict_experiment):
        pass

    def split_analyze(self, experiment, dict_experiment):
        print('%s, %s: %s %s' % (
            experiment, dict_experiment['formula'], self.analyze_type, 
            'not exclude' if not self.exclude else ''))
        analyze_list = dict_experiment['analyze_list']
        fault_list = dict_experiment['fault_list']
        set_project, dict_project = split_list(analyze_list)
        set_project2, dict_fault = split_list(fault_list)
        project_list = list(set_project).sort()
        for project in set_project:
            dict_experiment['analyze_list'] = dict_project[project]
            dict_experiment['fault_list'] = dict_fault[project]
            print(project)
            # print('analyze: %d' % len(dict_experiment['analyze_list']))
            # print('fault: %d' % len(dict_experiment['fault_list']))
            self.work(experiment, dict_experiment)
        dict_experiment['analyze_list'] = analyze_list
        dict_experiment['fault_list'] = fault_list

class Compare:
    VERY_BIG = 1000000
    def __init__(self, name, category=''):
        self.name = name
        self.base_value = None
        self.value = None
        self.fraction = None
        self.category = category
        #self.value = float(value)

    def add_base_value(self, value):
        self.base_value = value

    def add_value(self, value):
        self.value = value

    def in_category(self, category):
        return self.category == category

    def calcualte_fraction(self):
        try:
            base_value = float(self.base_value)
            value = float(self.value)
            self.fraction = (base_value - value) / (0.5*(base_value+value))
        except:
            self.fraction = self.VERY_BIG

    def remove_value(self):
        self.value = None

    def able_to_use(self):
        return self.value is not None

    def __lt__(self, other):
        return self.fraction < other.fraction

    def __str__(self):
        return '%s %s->%s: %s' % (self.name, self.base_value, self.value, self.fraction if self.fraction <= self.VERY_BIG else 'error')

    def xy(self):
        xy_list = []
        for x in [self.base_value, self.value]:
            x = float(x)
            if x == 0.0:
                xy_list.append(6.0)
            else:
                #print(x)
                xy_list.append(-math.log(x, 10.0))
        return '%s, %s, %s'  % (self.name, xy_list[0], xy_list[1])

class CompareMax(Compare):
    def __init__(self, name, category=''):
        super().__init__(name, category)

    def calcualte_fraction(self):
        try:
            base_value = float(self.base_value)
            value = float(self.value)
            self.fraction = (base_value - value) / max(base_value,value)
        except:
            self.fraction = self.VERY_BIG


class CompareWithBase:
    def __init__(self):
        self.compare_dict = {}

    def set_base_value(self, name, value, category=''):
        # print('own: %s' % self.compare_dict.keys())
        self.compare_dict[name] = Compare(name, category)
        self.compare_dict[name].add_base_value(value)

    def set_value(self, name, value):
        self.compare_dict[name].add_value(value)

    def remove_value(self, name):
        # self.compare_dict[name].remove_value()
        compare = self.compare_dict.get(name)
        if compare is not None:
            compare.remove_value()

    def calculate_and_print(self):
        pair_list = list(self.compare_dict.values())
        ratio_list = []
        for compare in pair_list:
            compare.calcualte_fraction()
            if compare.able_to_use() and compare.fraction < Compare.VERY_BIG:
                ratio_list.append(compare.fraction)
        pair_list.sort()
        for compare in pair_list:
            if compare.able_to_use():
                if PRINT_VERSION:
                    print(compare)
                
        print('avg: %f' % np.mean(ratio_list))

    def generate_scatter(self):
        pair_list = list(self.compare_dict.values())
        for compare in pair_list:
            compare.calcualte_fraction()
        pair_list.sort()
        for compare in pair_list:
            if compare.able_to_use():
                print(compare.xy())

    def calculate_in_category(self, category_name):
        pair_list = list(self.compare_dict.values())
        in_list, other_list = [], []
        for compare in pair_list:
            compare.calcualte_fraction()
            if compare.able_to_use() and compare.fraction < Compare.VERY_BIG:
                if compare.in_category('in'):
                    in_list.append(compare)
                else:
                    other_list.append(compare)
        print('in %s' % category_name)
        self.solve_list(in_list)
        print('other from %s' % category_name)
        self.solve_list(other_list)

    def solve_list(self, pair_list):
        pair_list.sort()
        ratio_list = [compare.fraction for compare in pair_list]
        for compare in pair_list:
            pass
        #    print(compare)
        print('avg: %s' % np.mean(ratio_list))
        

class CompareWithMax(CompareWithBase):
    def __init__(self):
        super().__init__()

    def set_base_value(self, name, value, category=''):
        # print('own: %s' % self.compare_dict.keys())
        self.compare_dict[name] = CompareMax(name, category)
        self.compare_dict[name].add_base_value(value)

dict_compare_base = {
        'avg': CompareWithBase,
        'max': CompareWithMax,
        }

# It is fool to use judgement list! I use only judgement in this class
class CompareBaseAnalyzer(Analyzer):
    def __init__(self, judgement, exclude, base, formula_list, compare_method):
        Analyzer.__init__(self, 'compare_base', exclude)
        self.judgement = judgement
        base_experiment = Version.Experiment(base)
        self.compare_system = {} 
        for formula in formula_list:
            print('formula: %s' % formula)
            # compare_machine = CompareWithBase()
            compare_machine = dict_compare_base[compare_method]()
            self.compare_system[formula] = compare_machine           
            # analyze_result = base_experiment.return_analyze(formula)
            analyze_result = self.load_base(base_experiment, formula)
            for row in analyze_result:
                if self.exclude and if_exclude(row['project'], row['no']):
                    continue
                # print(row)
                #compare_machine.set_base_value('%s@%s' % (
                #    row['project'], row['no']), row[judgement])
                self.set_base(compare_machine, row)
  
    def set_base(self, compare_machine, row):
        compare_machine.set_base_value(
                self.generate_version(row), row[self.judgement])

    def load_base(self, base_experiment, formula):
        return base_experiment.return_analyze(formula)

    def generate_version(self, row):
        return '%s@%s' % (row['project'], row['no'])

    def row_list(self, dict_experiment):
        return dict_experiment['analyze_list']

    def work(self, experiment, dict_experiment):
        # print(self.compare_system.keys())
        compare_machine = self.compare_system[dict_experiment['formula']]
        # for row in dict_experiment['analyze_list']:
        for row in self.row_list(dict_experiment):
            if self.exclude and if_exclude(row['project'], row['no']):
                continue
            # compare_machine.set_value('%s@%s' % (
            #    row['project'], row['no']), row[self.judgement])
            compare_machine.set_value(self.generate_version(row),
                    row[self.judgement])
        # compare_machine.calculate_and_print()
        self.calculate(compare_machine)
        # for row in dict_experiment['analyze_list']:
        for row in self.row_list(dict_experiment):
            compare_machine.remove_value(self.generate_version(row))#'%s@%s' % (
            #    row['project'], row['no']))

    def calculate(self, compare_machine):
        # print('calculate and print')
        compare_machine.calculate_and_print()

class ScatterAnalyzer(CompareBaseAnalyzer):
    def __init__(self, judgement, exclude, base, formula_list, compare_method):
        CompareBaseAnalyzer.__init__(self, judgement, exclude, base, formula_list, compare_method)

    def calculate(self, compare_machine):
        compare_machine.generate_scatter()
 
class CompareNumberBaseAnalyzer(CompareBaseAnalyzer):
    def __init__(self, judgement, exclude, base,
            formula_list, compare_method, max_number):
        self.num_fault = {}
        self.max_number = max_number
        CompareBaseAnalyzer.__init__(
                self, judgement, exclude, base, formula_list, compare_method)
        self.analyze_type = 'number_base'


    def load_base(self, base_experiment, formula):
        self.num_fault = FaultNumberAnalyzer.get_fault_number(
                base_experiment.return_fault(formula))
        return base_experiment.return_analyze(formula)

    def set_base(self, compare_machine, row):
        version_name =  self.generate_version(row)
        in_category = self.num_fault[version_name] < self.max_number
        compare_machine.set_base_value(version_name, row[self.judgement], 
                'in' if in_category else 'other')

    def calculate(self, compare_machine):
        # print('prepare to calculate in category')
        compare_machine.calculate_in_category(['<2'])

class CompareFaultBaseAnalyzer(CompareBaseAnalyzer):
    def __init__(self, judgement, exclude, base, 
            formula_list, compare_method, to_compare_list):
        self.to_compare_list = to_compare_list
        CompareBaseAnalyzer.__init__(
                self, judgement, exclude, base, formula_list, compare_method)
        self.analyze_type = 'fault_base'

    def load_base(self, base_experiment, formula):
        self.count_dict = {}
        return base_experiment.return_fault(formula)

    def set_base(self, compare_machine, row):
        in_category = row['type'] in self.to_compare_list
        compare_machine.set_base_value(
                self.generate_version(row), row[self.judgement], 
                'in' if in_category else 'other')

    def generate_version(self, row):
        version_name = '%s@%s' % (row['project'], row['no'])
        if not version_name in self.count_dict:
            self.count_dict[version_name] = 0
        else:
            self.count_dict[version_name] += 1
        return '%s_%s' % (version_name, self.count_dict[version_name])

    def row_list(self, dict_experiment):
        self.count_dict =  {}
        return dict_experiment['fault_list']

    def calculate(self, compare_machine):
        # print('prepare to calculate in category')
        compare_machine.calculate_in_category(self.to_compare_list)

class AvgAnalyzer(Analyzer):
    def __init__(self, judgement_list, exclude):
        Analyzer.__init__(self, 'avg_analyze', exclude)
        self.judgement_list = judgement_list
        
    def work(self, experiment, dict_experiment):
        for judgement in self.judgement_list:
            value = 0.0
            num = 0.0
            # print('all: %s' % len(dict_experiment['analyze_list']))
            for row in dict_experiment['analyze_list']:
                try:
                    if self.exclude and if_exclude(row['project'], row['no']):
                        continue
                    value += float(row[judgement])
                    num += 1
                except:
                    pass
            print('%s: %s' % (judgement, value/num if num != 0 else 'none'))

class QuartileAnalyzer(Analyzer):
    def __init__(self, judgement, exclude):
        Analyzer.__init__(self, 'quartile', exclude)
        self.judgement = judgement

    def work(self, experiment, dict_experiment):
        values = []
        for row in dict_experiment['analyze_list']:
            try:
                if self.exclude and if_exclude(row['project'], row['no']):
                    continue
                values.append(self.get_value(row[self.judgement]))
            except Exception as e:
                print(e)
        values.sort()
        length = len(values)
        print('min: %f; max: %f; mid: %f\n1/4: %f; 3/4: %f' % (
            values[0], values[-1], values[int(length/2)],
            values[int(length/4)], values[int(length*3/4)]))

    @staticmethod
    def get_value(value_source):
        return float(value_source)

class LogQuartileAnalyzer(QuartileAnalyzer):
    def __init__(self, judgement, exclude):
        QuartileAnalyzer.__init__(self, judgement, exclude)

    @staticmethod
    def get_value(value_source):
        if float(value_source) == 0.0:
            return -10.0
        return math.log(float(value_source), 10.0)

class DistributionAnalyzer(Analyzer):
    def __init__(self, judgement, exclude):
        Analyzer.__init__(self, 'distribution', exclude)
        self.judgement = judgement
        # self.min_log = int(min_log) + 1

    def work(self, experiment, dict_experiment):
        count = {}
        min_values = 0
        #border = {}
        #for x in range(0, self.min_log):
        #    count[x] = 0
        #    border[x] = 10 ** (-self.min_log)
        for row in dict_experiment['analyze_list']:
            try:
                if self.exclude and if_exclude(row['project'], row['no']):
                    continue
                if float(row[self.judgement]) == 0.0:
                    min_values += 1
                else:
                    level = int(math.log(float(row[self.judgement]), 0.1))
                    if level not in count.keys():
                        count[level] = 1
                    else:
                        count[level] += 1
            except Exception as e:
                print('%s@%s: %s' % (
                    row['project'], row['no'], row[self.judgement]))
                print(e)
                pass
        count['0.0'] = min_values
        print(count)    

def split_list(analyze_list):
    set_project = set({})
    dict_project = dict({})
    for row in analyze_list:
        if not row['project'] in set_project:
            set_project.add(row['project'])
            dict_project[row['project']] = []
        dict_project[row['project']].append(row)
    return set_project, dict_project
        
class CompareFaultAnalyzer(Analyzer):
    def __init__(self, to_compare_list, exclude):
        Analyzer.__init__(self, 'fault_compare', exclude)
        self.to_compare_list = to_compare_list

    def work(self, experiment, dict_experiment):
        dict_spectra_num = dict_experiment['spectra_number']
        type_set = {x for x in self.to_compare_list}
        value = {}
        count = {}
        # for name in self.to_compare_list + ['other']:
        for name in ['in', 'other']:
            value[name] = 0.0
            count[name] = 0
        for row in dict_experiment['fault_list']:
            try:
                if self.exclude and if_exclude(row['project'], row['no']):
                    continue    
                exam = float(row['rank']) / dict_spectra_num['%s@%s' % (
                    row['project'], row['no'])]
                if row['type'] in type_set:
                    # print('%s@%s: %f' % (row['project'], row['no'], exam))
                    #value[row['type']] += exam
                    #count[row['type']] += 1
                    value['in'] += exam
                    count['in'] += 1
                else:
                    value['other'] += exam
                    count['other'] += 1
            except:
                # find that most exceptions are not found : '' for rank of class Fault
                # print('special item: %s' % row['rank'])
                pass
        #for item in list(type_set)+['other']:
        for item in ['in', 'other']:
            average_value = value[item]/count[item] if count[item] != 0 else 'none'
            if item == 'in':
                print(self.to_compare_list)
            print('%s: %s' % (item, average_value))

class TypeCompareAnalyzer(Analyzer):
    def __init__(self, to_compare_list, exclude):
        Analyzer.__init__(self, 'type_compare', exclude)
        self.to_compare_list = to_compare_list
        self.accumulate_in = {'+': 0, '=': 0, '-': 0}
        self.accumulate_other = {'+': 0, '=': 0, '-': 0}

    def work(self, experiment, dict_experiment):
        # dict_spectra_num = dict_experiment['spectra_number']
        type_set = {x for x in self.to_compare_list}
        in_dict = {}
        other_dict = {}
        # for name in self.to_compare_list + ['other']:
        for name in ['+', '=', '-']:
            in_dict[name] = 0
            other_dict[name] = 0
        for row in dict_experiment['fault_list']:
            try:
                if self.exclude and if_exclude(row['project'], row['no']):
                    continue    
                rank = float(row['rank'])
                if row['compare_rank'] is None:
                    dict_now['=']+= 1
                    continue
                compare_rank = float(row['compare_rank'])
                if row['type'] in type_set:
                    dict_now = in_dict
                else:
                    dict_now = other_dict
                if rank > compare_rank:
                    dict_now['-'] += 1
                elif rank == compare_rank:
                    dict_now['='] += 1
                else:
                    dict_now['+'] += 1
            except:
                # find that most exceptions are not found : '' for rank of class Fault
                # print('special item: %s' % row['rank'])
                pass
        #for item in list(type_set)+['other']:
        print('to_compare: ' + str(self.to_compare_list))
        for dict_now in [in_dict, other_dict]:
            for key, value in dict_now.items():
                print('%s: %s' % (key, value))
        for dict_now, dict_acc in [[in_dict, self.accumulate_in], [
            other_dict, self.accumulate_other]]:
            for key, value in dict_now.items():
                dict_acc[key] += value
        print('accumulate: ' + str(self.to_compare_list))
        for dict_now in [self.accumulate_in, self.accumulate_other]:
            for key, value in dict_now.items():
                print('%s: %s' % (key, value))

class FaultNumberAnalyzer(Analyzer):
    def __init__(self, judgement, exclude, max_number):
        Analyzer.__init__(self, 'fault_number', exclude)
        self.judgement = judgement
        self.max_number = max_number

    def work(self, experiment, dict_experiment):
        dict_version = self.get_fault_number(dict_experiment['fault_list'])
        num_value = {}
        max_number_list = []
        for row in dict_experiment['analyze_list']:
            try:
                if self.exclude and if_exclude(row['project'], row['no']):
                    continue
                version_name = '%s@%s' % (row['project'], row['no'])
                num_fault = dict_version.get(version_name, 0)
                if not num_fault in num_value.keys():
                    num_value[num_fault] = []
                num_value[num_fault].append(float(row[self.judgement]))
                if num_fault >= self.max_number:
                    max_number_list.append(float(row[self.judgement]))
            except:
                pass
        for key, value in num_value.items():
            print('fault %d: %d -> %f' % (key, len(value),
                np.mean(value)))
        print('max %d: %d -> %f' % (self.max_number,
            len(max_number_list), np.mean(max_number_list)))

    @staticmethod
    def get_fault_number(fault_list):
        dict_version = {}
        for row in fault_list:
            version_name = '%s@%s' % (row['project'], row['no'])
            if not version_name in dict_version.keys():
                dict_version[version_name] = 0
            try:
                rank = float(row['rank'])
                dict_version[version_name] += 1
            except:
                pass
        return dict_version 

def create_avg_analyzer(dict_experiment):
    return AvgAnalyzer(dict_experiment['judgement_list'], 
            dict_experiment.get('exclude', True))
    
def create_fault_compare_analyzer(dict_experiment):
    return CompareFaultAnalyzer(dict_experiment['compare_list'],
            dict_experiment.get('exclude', True))

def create_type_compare_analyzer(dict_experiment):
    return TypeCompareAnalyzer(dict_experiment['compare_list'],
            dict_experiment.get('exclude', True))


def create_compare_base_analyzer(dict_experiment):
    return CompareBaseAnalyzer(dict_experiment['judgement'],
            dict_experiment.get('exclude', True),
            dict_experiment.get('base', '10.0'),
            dict_experiment.get('formula_list', []),
            dict_experiment.get('compare_method', 'avg'))

def create_scatter(dict_experiment):
    return ScatterAnalyzer(dict_experiment['judgement'],
            dict_experiment.get('exclude', True),
            dict_experiment.get('base', '12.15'),
            dict_experiment.get('formula_list', []),
            dict_experiment.get('compare_method', 'avg'))

def create_fault_base_analyzer(dict_experiment):
    return CompareFaultBaseAnalyzer(dict_experiment['judgement'],
            dict_experiment.get('exclude', True),
            dict_experiment.get('base', '12.15'),
            dict_experiment.get('formula_list', []),
            dict_experiment.get('compare_method', 'avg'),
            dict_experiment.get('compare_list', ['insert', 'coverage']))

def create_number_base_analyzer(dict_experiment):
    return CompareNumberBaseAnalyzer(dict_experiment['judgement'],
            dict_experiment.get('exclude', True),
            dict_experiment.get('base', '12.15'),
            dict_experiment.get('formula_list', []),
            dict_experiment.get('compare_method', 'avg'),
            dict_experiment.get('max_number', 2))
 
def create_distribution(dict_experiment):
    return DistributionAnalyzer(dict_experiment.get('judgement', 'EXAM'),
            dict_experiment.get('exclude', True))

def create_quartile(dict_experiment):
    if dict_experiment.get('type', 'simple') == 'simple':
        return QuartileAnalyzer(dict_experiment.get('judgement', 'EXAM'),
            dict_experiment.get('exclude', True))
    elif dict_experiment['type'] == 'log':
        return LogQuartileAnalyzer(dict_experiment.get('judgement', 'EXAM'),
            dict_experiment.get('exclude', True))

def create_fault_number(dict_experiment):
    return FaultNumberAnalyzer(dict_experiment.get('judgement', 'EXAM'),
        dict_experiment.get('exclude', True),
        int(dict_experiment.get('max_number', 3)))

def create_analyzer(dict_experiment):
    return dict_analyzer[dict_experiment['mode']](dict_experiment)

dict_analyzer = {
    'avg_analyze': create_avg_analyzer,
    'compare_fault': create_fault_compare_analyzer,
    'compare_base': create_compare_base_analyzer,
    'distribution': create_distribution,
    'quartile': create_quartile,
    'fault_number': create_fault_number,
    'fault_base': create_fault_base_analyzer,
    'number_base': create_number_base_analyzer,
    'type_compare': create_type_compare_analyzer,
    'scatter': create_scatter,
    }
