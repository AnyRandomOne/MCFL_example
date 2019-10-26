import Version
import csv
import sbfl
import numpy as np
import analyzer
import calculator
import fault

experiment_formulas = [
        'barinel', 'ochiai', 'tarrantula', 'cohen', 'opt', 'dstar',
        'rogot1', 'wong1', 'wong2', 'jaccard']

def compare_version(name, no, fixed=False):
    version = Version.create_version(name, no, fixed)
    out_result = version.read_out_test()
    out_search = version.read_trigger_tests()
    print('out_result:\n%s\n' % out_result)
    print('defects4j_result:\n%s\n' % out_search)

def compare_project(name, no):
    print('%s %s fixed' % (name, no))
    compare_version(name, no, True)
    print('%s %s buggy' % (name, no))
    compare_version(name, no)

def transfer_project(name, no, formula):
    version = Version.create_version(name, no)
    version.transfer_ranking_csv(formula)
    print('transfer %s %s finished.' % (version.name(), version.no()))

def transfer_project_formula(name, formula):
    print('transfer formula %s for project %s.' % (formula, name))
    for i in range(0, Version.max_no[name]):
        transfer_project(name, i+1, formula)

def read_bug_location(project):
    # xxx  is for anonymous location
    input_file = open('xxx/location_result_of_%s.csv' % project)
    reader = csv.DictReader(input_file)
    result = []
    for row in reader:
        result.append(row)
    return result

def write_into_csv(path, result_list, headline):
    f = open(path, 'w')
    csv_writer = csv.DictWriter(f, headline)
    csv_writer.writeheader()
    for row in result_list:
        result_dict = {}
        for item in headline:
            # note that: the item may not own the key.
            result_dict[item] = row.get(item, None)
        csv_writer.writerow(result_dict)

def print_spectra(path, spectra_list, to_sort=False):
    result_list = []
    if to_sort:
        spectra_list.sort(reverse=True)
    for spectra in spectra_list:
        result_list.append(spectra.to_dict())
    write_into_csv(path, result_list, ['name', 'suspicious_value'])

class BasicTask:
    def __init__(self, dict_experiment):
        self.fault_list = {}
        self.result_list = {}
        self.calculator = None
        self.ranker = analyzer.dict_ranker[
                dict_experiment.get('rank', 'avg')]
        self.collector = fault.dict_collector[
                dict_experiment.get('collector', 'both_location')]
        # print(self.collector)
        self.exclude_blank = dict_experiment.get('rank', 'avg') in set([
            'exclude', 'after', 'compare'])

    def add_calculator(self, calculator_used):
        self.calculator = calculator_used

    def prepare_list(self, dict_experiment):
        # self.add_calculator(calculator.BasicCalculator())
        self.add_calculator(calculator.dict_calculator.get(
            dict_experiment.get('calculator', 'basic'),
            calculator.BasicCalculator()))
        self.analyze_judgements = dict_experiment['analyze']
        for formula in dict_experiment['formulas']:
            self.fault_list[formula] = []
            self.result_list[formula] = []

    def collect_fault(self, version):
        # print('collect fault')
        return fault.analyze_fault_location(version, self.collector)

    def read_spectra(self, version, dict_experiment):
        return version.return_spectra_add()

    def run_projects(self, dict_experiment):
        self.prepare_list(dict_experiment)
        for project in dict_experiment['project']:
            number_list = dict_experiment.get('no', [
                x for x in range(1, Version.max_no[project]+1)])
            # for no in range(1, Version.max_no[project] + 1):
            for no in number_list:
                version= Version.create_version(project, no, 
                    relevant=dict_experiment.get('relevant', False),
                    split=dict_experiment.get('split', False))
                try:
                    self.run_version(version, dict_experiment)
                except Exception as e:
                    print('fail in %s' % str(version))
                    print('exception: %s' % e)
        for formula in dict_experiment['formulas']:
            # print(formula)
            fault_head = list(self.fault_list[formula][0].keys())
            write_into_csv('%s/result/experiment_%s_%s_fault.csv' % (version.MISSING_BRANCH_PATH, dict_experiment['experiment_no'], formula), self.fault_list[formula], fault_head)
            write_into_csv('%s/result/experiment_%s_%s_analyze.csv' % (version.MISSING_BRANCH_PATH, dict_experiment['experiment_no'], formula), self.result_list[formula], ['project', 'no']+self.analyze_judgements)

    def run_version(self, version, dict_experiment):
        dict_experiment['fault_list'] = self.collect_fault(version)
        dict_experiment['spectra_list'] = self.read_spectra(version, dict_experiment)
        for type_name in [
                'method_call', 'variable','variable_block','predicate','key', 
                'branch']:
            self.read_info(dict_experiment, version, type_name)
        print(version)
        #print('len: %d' % len(dict_experiment['method_call']))
        #print(list(dict_experiment['method_call'].items())[0])
        for formula in dict_experiment['formulas']:
            dict_experiment['formula'] = formula
            self.calculator.set_formula(formula)
            fault_list_new, result_list_new = self.fault_localization(
                    version, self.analyze_judgements, dict_experiment)
            self.fault_list[formula] += fault_list_new
            self.result_list[formula].append(result_list_new)

    def read_info(self, dict_experiment, version, info_type):
        for solver in self.solver_list:
            if solver.need_info(info_type):
                dict_experiment[info_type] = version.read_info(info_type)
                #if info_type == 'branch':
                #    dict_experiment[info_type] = self.solve_branch_loc(
                #            dict_experiment['branch'])
                return

    def calculate_branch(self, dict_experiment):
        for solver in self.solver_list:
            if solver.need_info('branch'):
                dict_experiment['branch_result'] = self.solve_branch_loc(
                        dict_experiment['branch'])

    def solve_branch_loc(self, branch_list):
        # print('start to solve')
        result = self.calculate_value(branch_list)
        for i in range(0, len(branch_list)):
            #print(branch_list[i])
            branch_list[i].set_suspicious_value(result[i])
        branch_dict = {}
        for spectra_branch in branch_list:
            if spectra_branch.name not in branch_dict.keys():
                branch_dict[spectra_branch.name] = []
            branch_dict[spectra_branch.name].append(spectra_branch.suspicious_value)
        result_dict = {}
        for key, value in branch_dict.items():
            result_dict[key] = max(value)
        return result_dict

    def fault_localization(self, version, analyze_judgements, dict_experiment):
        spectra_list = dict_experiment['spectra_list'][:]
        fault_list = dict_experiment['fault_list'][:]
        self.calculate_branch(dict_experiment)
        result = self.calculate_value(spectra_list)
        result = self.solve_result(dict_experiment, result)
        # print(len(spectra_list)i)
        # print('type: %s; len: %s' % (type(result[0]), len(result)))
        # print('type: %s; len: %s' % (type(spectra_list[0]), len(spectra_list)))
        for i in range(0, len(spectra_list)):
            spectra_list[i].set_suspicious_value(result[i])
        if version.version_name() in dict_experiment.get('print', []):
            print_spectra('%s/result/experiment_%s_%s_%s_spectra.csv' % (version.MISSING_BRANCH_PATH, dict_experiment['experiment_no'], dict_experiment['formula'], version.version_name()), spectra_list, to_sort=True)
        return self.analyze_result(version, spectra_list, fault_list, dict_experiment['formula'])

    def calculate_value(self, spectra_list):
        data = np.array([[ x.hit_pass for x in spectra_list],
            [ x.hit_fail for x in spectra_list],
            [ x.miss_pass for x in spectra_list],
            [ x.miss_fail for x in spectra_list]])
        # print('start calculate')
        result = self.calculator.calculate(data)
        # print('end calculate')
        return result

    # the basic version does not have solver. 
    def solve_result(self, dict_experiment, result):
        return result

    def analyze_result(self, version, spectra_list, fault_list, formula):
        # print('spectra len to analyze : %s' % len(spectra_list))
        spectra_list.sort(reverse=True)
        # print_spectra(version.cal_result_dir(formula), spectra_list)
        # analyzer.count_fault_rank(fault_list, spectra_list)
        self.ranker(fault_list, spectra_list, version)
        fault_result_list = [fault_now.to_dict() for fault_now in fault_list]
        # analyze_judgements = ['EXAM']
        result_dict = {'project': version.name(), 'no': int(version.no())}
        to_exclude = version.return_spectra_exclude() if self.exclude_blank else []
        for analyze_judgement in self.analyze_judgements:
            result_dict[analyze_judgement] = analyzer.analyze(
                analyze_judgement, spectra_list, fault_list, to_exclude)
        # print('finish analyze')
        return fault_result_list, result_dict

    # not @staticmethod any longer
    def return_method_range(self, spectra_list, dict_experiment={}):
        result_list = []
        method_spectra_list = []
        dict_suspicious_method = {}
        start_no =0 
        for i in range(1, len(spectra_list)):
            if not spectra_list[i].same_method(spectra_list[i-1]):
                result_list.append([start_no, i])
                method_spectra_list.append(spectra_list[start_no])
                start_no = i
        result_list.append([start_no, len(spectra_list)])
        method_spectra_list.append(spectra_list[start_no])
        method_result = self.calculate_value(method_spectra_list)
        if dict_experiment.get('page_rank', False):
            method_result = calculator.page_rank_cal(method_result, dict_experiment, method_spectra_list)
        for i in range(0, len(method_spectra_list)):
            dict_suspicious_method[method_spectra_list[i].method_name()] = method_result[i]
        return result_list, dict_suspicious_method

    def return_class_range(self, spectra_list):
        class_range_list = []
        start_no = 0
        for i in range(1, len(spectra_list)):
            if not spectra_list[i].same_class(spectra_list[i-1]):
                class_range_list.append([start_no, i])
                start_no = i
        class_range_list.append([start_no, len(spectra_list)])
        return class_range_list 

class MethodTask(BasicTask):
    def __init__(self, dict_experiment, solver_list):
        super().__init__(dict_experiment)
        self.solver_list = solver_list

    def read_spectra(self, version, dict_experiment):
        raw_spectra = super().read_spectra(version, dict_experiment)
        method_list = [raw_spectra[0]]
        for spectra_now in raw_spectra:
            if not spectra_now.same_method(method_list[-1]):
                method_list.append(spectra_now)
        return method_list

    def collect_fault(self, version):
        # print('collect fault')
        return fault.analyze_fault_location(version, self.collector, factory=fault.MethodFactory)

    def solve_result(self, dict_experiment, data_list):
        for solver in self.solver_list:
            data_list = solver.solve(data_list, dict_experiment)
        return data_list

class SolverTask(BasicTask):
    def __init__(self, dict_experiment, solver_list):
        BasicTask.__init__(self, dict_experiment)
        self.solver_list = solver_list
        self.need_method_range = False
        self.need_class_range = False
        for solver in solver_list:
            if solver.method_level():
                self.need_method_range = True
            elif solver.class_level():
                self.need_class_range = True
        self.class_range = []
        self.method_range = []
        self.dict_method_suspicious = {}

    def fresh(self):
        self.class_range = []
        self.method_range = []
        self.dict_method_suspicious = {}

    def solve_result(self, dict_experiment, data_list):
        self.fresh()
        if self.need_method_range:
            self.method_range, self.dict_method_suspicious = self.return_method_range(dict_experiment['spectra_list'], dict_experiment)
            dict_experiment['suspicious_method'] = self.dict_method_suspicious
        if self.need_class_range:
            self.class_range = self.return_class_range(dict_experiment['spectra_list'])
        for solver in self.solver_list:
            data_list = solver.accept_task(self, dict_experiment, data_list)
        return data_list

    def class_solve(self, solver, dict_experiment, data_list):
        data_list = np.array(data_list)
        for class_range in self.class_range: 
            data = data_list[class_range[0]:class_range[1]]
            dict_experiment['local_spectra'] = dict_experiment['spectra_list'][class_range[0]:class_range[1]]
            data = solver.solve(data, dict_experiment)
            data_list[class_range[0]:class_range[1]] = data
        return data_list

    def method_solve(self, solver, dict_experiment, data_list):
        data_list = np.array(data_list)
        # dict_experiment['suspicious_method'] = dict_suspicious_method
        for method_range in self.method_range:
            data = data_list[method_range[0]:method_range[1]]
            dict_experiment['local_spectra'] = dict_experiment['spectra_list'][
                    method_range[0]:method_range[1]]
            data = solver.solve(data, dict_experiment)
            data_list[method_range[0]:method_range[1]] = data
        return data_list


class InsertTask(SolverTask):
    def __init__(self, dict_experiment, inserter, solver_list):
        if dict_experiment.get('collector') is None:
            dict_experiment['collector'] = NormalCollector()
        SolverTask.__init__(self, dict_experiment, solver_list)
        self.inserter = inserter
        # self.solver_list = solver_list

    def read_spectra(self, version, dict_experiment):
        raw_spectra_list = version.return_spectra_add()
        return self.inserter(raw_spectra_list, spectra_type=
                sbfl.dict_spectra_type.get(
                    dict_experiment.get('spectra_type', 'after'),
                    sbfl.InsertZeroSpectra))

    def collect_fault(self, version):
        return fault.analyze_fault_location(version, self.collector)

def time_experiment(project, no, relevant=False):
    # the AST has been extract, so does not extract again.
    # If change the way of extracting AST, rerun the following two lines.
    version = Version.create_version(project, no)
    modify_spectra(project, no, relevant)
    version.extract_AST()
    # version.extract_method_call()
    version.extract_variable()
    version.transfer_variable()
    #version.extract_predicate()
    #version.transfer_predicate()
    version.extract_key()
    version.transfer_key()
    version.transfer_block_info()
    version.transfer_block_variable()
     

def extract_project(project, no, relevant=False):
    # the AST has been extract, so does not extract again.
    # If change the way of extracting AST, rerun the following two lines.
    version = Version.create_version(project, no)
    version.extract_branch_info()
    # version.extract_method_call()
    #version.extract_variable()
    #version.transfer_variable()
    #version.extract_predicate()
    #version.transfer_predicate()
    # version.extract_AST()
    # version.transfer_block_info()
    #version.transfer_block_variable()
    #version.extract_key()
    #version.transfer_key()
    # modify_spectra(project, no, relevant)
    # version.extract_exclude()

def modify_spectra(project, no, relevant=False, split=False):
    version = Version.create_version(project, no, relevant=relevant, split=split)
    # print('%s, %s: %s, %s, %s' % (project, no, relevant, type(version), version.spectra_add_dir()))
    original_spectra = version.return_spectra()
    # print('get original spectra')
    # print('original: %d' % len(original_spectra))
    spectra_matrix = sbfl.SpectraMatrix(original_spectra)
    ast_info_list = version.return_ast_info()
    # print('get ast info')
    # print('ast info: ' + str(len(ast_info_list)))
    for node in ast_info_list:
        # node.insert_statement(spectra_matrix)
        node.insert_start(spectra_matrix)
        # print(node.insert_statement)
    for node in ast_info_list:
        node.insert_end(spectra_matrix)
    # print('insert')
    output_list = spectra_matrix.list_for_csv_writer()
    print('output_list: %s' % len(output_list))
    headline = ['name', 'hit_pass', 'hit_fail', 'miss_pass', 'miss_fail']
    path = version.spectra_add_dir()
    # print('prepare to write csv')
    write_into_csv(path, output_list, headline)

def solve_projects(projects, relevant=False):
    #for project in ['Lang', 'Mockito', 'Chart', 'Closure', 'Math', 'Time']:
    for project in projects:
        for no in range(1, Version.max_no[project]+1):
            try:
                extract_project(project, no)
                # modify_spectra(project, no)
                print('success in %s_%s' % (project, no))
            except Exception as e:
                print("error: %s" % e)
                print('fail in %s_%s' % (project, no))
    
def supple_for_Lang_ast():
    for no in range(42, Version.max_no['Lang']+1):
        try:
            extract_project('Lang', no)
            print('seccess in %s_%s' % ('Lang'))
        except Exception as e:
            print(e)
            print('fail in %s_%s' % ('Lang', no))

def double_experiment(dict_experiment):
    print('experiment: %s' % dict_experiment['experiment_no'])
    experiment(dict_experiment, True)
    experiment(dict_experiment, False)

def single_experiment(dict_experiment):
    print('experiment: %s' % dict_experiment['experiment_no'])
    experiment(dict_experiment, False)

def control_experiment(dict_experiment):
    print('experiment: %s' % dict_experiment['experiment_no'])
    experiment(dict_experiment, True)

def basic_experiment(dict_experiment):
    BasicTask(dict_experiment).run_projects(dict_experiment)

def basic_insert_experiment(dict_experiment):
    solver_list = [calculator.solver_dict[
        dict_experiment.get('conv_mode', 'conv')
        ](dict_experiment)]
    InsertTask(dict_experiment, sbfl.basic_inserted_spectra, solver_list
            ).run_projects(dict_experiment)

def method_experiment(dict_experiment):
    solver_list = [calculator.solver_dict['method'](dict_experiment),
            calculator.solver_dict['method_call'](dict_experiment)]
    SolverTask(dict_experiment, solver_list).run_projects(dict_experiment)

def variable_experiment(dict_experiment):
    solver_list = [calculator.solver_dict['method'](dict_experiment),
            calculator.solver_dict['method_call'](dict_experiment),
            calculator.solver_dict['variable'](dict_experiment),]
    SolverTask(dict_experiment, solver_list).run_projects(dict_experiment)

def run_basic_task(dict_experiment, solver_list):
    SolverTask(dict_experiment, solver_list).run_projects(dict_experiment)

def run_raw_task(dict_experiment, solver_list):
    BasicTask(dict_experiment).run_projects(dict_experiment)

def run_insert_task(dict_experiment, solver_list):
    InsertTask(dict_experiment, sbfl.basic_inserted_spectra, solver_list).run_projects(dict_experiment)

def run_method_task(dict_experiment, solver_list):
    MethodTask(dict_experiment, solver_list).run_projects(dict_experiment)

def method_insert_experiment(dict_experiment):
    solver_list = [calculator.solver_dict[dict_experiment.get(
        'conv_mode', 'conv')](dict_experiment), 
        calculator.solver_dict['method'](dict_experiment)
        ]
    InsertTask(dict_experiment, sbfl.basic_inserted_spectra, solver_list).run_projects(dict_experiment)

def variable_insert_experiment(dict_experiment):
    solver_list = [calculator.solver_dict['variable'](dict_experiment),
        calculator.solver_dict[dict_experiment.get(
        'conv_mode', 'conv')](dict_experiment),
        calculator.solver_dict['method_call'](dict_experiment),
        calculator.solver_dict['method'](dict_experiment)
        ]
    InsertTask(dict_experiment, sbfl.basic_inserted_spectra, solver_list).run_projects(dict_experiment)


def compare_conv_experiment(dict_experiment):
    solver_list = [calculator.solver_dict[dict_experiment.get(
        'conv_mode', 'conv')](dict_experiment),
        calculator.solver_dict['method'](dict_experiment)
        ]
    SolverTask(dict_experiment, solver_list).run_projects(dict_experiment)

dict_method = {
        'basic': basic_experiment,
        'basic_insert': basic_insert_experiment,
        'method': method_experiment,
        'method_insert': method_insert_experiment,
        'compare_conv': compare_conv_experiment,
        'variable': variable_experiment,
        'variable_insert': variable_insert_experiment,
        }

dict_task = {
        'basic': run_basic_task,
        'insert': run_insert_task,
        'raw': run_raw_task,
        'method': run_method_task,
        }

def run_experiment(dict_experiment):
    # dict_method[dict_experiment['method']](dict_experiment)
    solver_parameters = dict_experiment.get('solver_list', [])
    solver_list = []
    for solver_parameter_dict in solver_parameters:
        solver_list.append(calculator.create_solver(
            solver_parameter_dict))
    dict_task[dict_experiment['method']](dict_experiment, solver_list)
  
def run_analyze(dict_experiment):
    analyzer_parameters = dict_experiment['analyzer_parameters']
    solver_list = []
    for analyzer_dict in analyzer_parameters:
        solver_list.append(analyzer.create_analyzer(analyzer_dict))
    analyzer.analyze_experiment(solver_list, dict_experiment)

