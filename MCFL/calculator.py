import numpy as np
import math

#formula_dict = {
#    'simple_match': simple_match,
#    'cohen': cohen,
#}

def same_magnitude(number):
    return 1.0 - np.exp(-1.0*number / 300.0)

def calculate_value(formula, hit_pass, hit_fail, miss_pass, miss_fail):
    return calculate_value_in_function(formula_dict[formula],
            hit_pass, hit_fail, miss_pass, miss_fail)

def calculate_value_in_function(function, hit_pass, hit_fail, miss_pass, miss_fail):
    for element in [hit_pass, hit_fail, miss_pass, miss_fail]:
        if type(element) is np.ndarray:
            element = element.astype('float64')
    try:
        result = function(hit_pass, hit_fail, miss_pass, miss_fail)
    except ZeroDivisionError as e:
        result = 0.0
    if type(result) is np.ndarray:
        for i in range(0, len(result)):
            if result[i] == float('inf') or result[i] == float('-inf') or np.isnan(result[i]):
                result[i] = 0.0
    else:
        if result == float('inf') or result == float('-inf') or np.isnan(result):
            result = 0.0

    return result

def denominator(to_transfer):
    n = np.array([to_transfer, [1.0 for num in to_transfer]])
    return np.max(n, axis=0)

def denominator_full(to_transfer):
    after = np.array(to_transfer)
    zero_loc = np.where(to_transfer == 0.0)
    for loc in zero_loc:
        after[loc] = 1.0
    return after

def simple_match(hit_pass, hit_fail, miss_pass, miss_fail):
    return (hit_fail + miss_pass) / (hit_pass + hit_fail + miss_pass + miss_fail)

def cohen(hit_pass, hit_fail, miss_pass, miss_fail):
    cohen_denominator = denominator((hit_fail+hit_pass)*(miss_pass+hit_pass)+(miss_fail+miss_pass)*(miss_fail+hit_fail))
    return (2*hit_fail*miss_pass - 2*miss_fail*hit_pass) / cohen_denominator
    # return (2*hit_fail*miss_pass-2*miss_fail*hit_pass) / ((hit_fail+hit_pass)*(miss_pass+hit_pass)+(miss_fail+miss_pass)*(miss_fail+hit_fail))

def dstar(hit_pass, hit_fail, miss_pass, miss_fail):
    # return (hit_fail*hit_fail) / (hit_pass + miss_fail)
    dstar_denominator = denominator(hit_pass + miss_fail)
    return (hit_fail * hit_fail) / dstar_denominator

def jaccard(hit_pass, hit_fail, miss_pass, miss_fail):
    jaccard_denominator = denominator(hit_fail + hit_pass + miss_fail)
    return hit_fail / jaccard_denominator
    # return hit_fail / (hit_fail + hit_pass + miss_fail)

def tarrantula(hit_pass, hit_fail, miss_pass, miss_fail):
    failed = hit_fail / (hit_fail + miss_fail)
    passed = hit_pass / (hit_pass + miss_pass)
    return failed / (failed + passed)

def tarrantula_new(hit_pass, hit_fail, miss_pass, miss_fail):
    failed = hit_fail / denominator(hit_fail + miss_fail)
    passed = hit_pass / denominator(hit_pass + miss_pass)
    return failed / denominator_full(failed + passed)

def ochiai(hit_pass, hit_fail, miss_pass, miss_fail):
    return hit_fail / denominator(np.sqrt((hit_fail + miss_fail) * (hit_fail+hit_pass)))
    # return hit_fail / math.sqrt((hit_fail+miss_fail) * (hit_fail+hit_pass))

def rogot1(hit_pass, hit_fail, miss_pass, miss_fail):
    fail_denominator = denominator((2*(2*hit_fail + hit_pass + miss_fail)))
    pass_denominator = denominator((2*(2*miss_pass + hit_pass + miss_fail))) 
    return hit_fail / fail_denominator + miss_pass / pass_denominator
    # return hit_fail /(2*(2*hit_fail + hit_pass + miss_fail)) + miss_pass / (2*(2*miss_pass + hit_pass + miss_fail))   

# the barinel in GZoltar.
# only for double, does not use numpy
def barinel(hit_pass, hit_fail, miss_pass, miss_fail):
    h = hit_pass / ( hit_pass + hit_fail)
    return pow(h, hit_pass) * pow(1-h, 11)

def opt( hit_pass, hit_fail, miss_pass, miss_fail):
    return hit_fail - ( hit_pass / (hit_pass + miss_pass + 1.0))

def wong2(hit_pass, hit_fail, miss_pass, miss_fail):
    return hit_fail - hit_pass

def ochiai2(hit_pass, hit_fail, miss_pass, miss_fail):
    # return ( hit_fail * miss_pass) / math.sqrt((hit_fail + miss_fail) * (hit_fail + hit_pass) * (miss_pass + miss_fail) * (miss_pass + hit_pass))
    return ( hit_fail * miss_pass) / denominator(np.sqrt((hit_fail + miss_fail) * (hit_fail + hit_pass) * (miss_pass + miss_fail) * (miss_pass + hit_pass)))

# barinel in ICSE 17 paper.
def barinel2( hit_pass, hit_fail, miss_pass, miss_fail):
    return hit_fail / denominator(hit_fail + hit_pass)

def corinel( hit_pass, hit_fail, miss_pass, miss_fail):
    return cohen(hit_pass, hit_fail, miss_pass, miss_fail) + barinel(hit_pass, hit_fail, miss_pass, miss_fail)

formula_dict = {
    'simple_match': simple_match,
    'cohen': cohen,
    'dstar': dstar,
    'jaccard': jaccard,
    'tarrantula': tarrantula,
    'ochiai': ochiai,
    'rogot1': rogot1,
    'barinel': barinel,
    'barinel2': barinel2,
    'opt': opt,
    'wong2': wong2,
    'ochiai2': ochiai2,
    'corinel': corinel,
    't_new': tarrantula_new,
}

class BasicCalculator:
    def __init__(self):
        self.formula = None

    def set_formula(self, formula):
        self.formula = formula_dict.get(formula, None) 

    def calculate(self, data):
        hit_pass, hit_fail, miss_pass, miss_fail = data[0], data[1], data[2], data[3]
        return calculate_value_in_function(self.formula, hit_pass, hit_fail, miss_pass, miss_fail)

class RelativeCalculator(BasicCalculator):
    def __init__(self):
        BasicCalculator.__init__(self)

    def calculate(self, data):
        result = BasicCalculator.calculate(self, data)
        return to_relative(result)
       
def to_relative(result_array):
    data_list = list(result_array.copy())
    if len(data_list) == 0:
        return []
    # relative_list = np.zeros(result_array.shape)
    relative_list = []
    value_to_relative = {}
    spectra_number = len(data_list)
    data_list.sort()
    # number_to_set = []
    rank_now, start_rank = 0, 0
    while rank_now < spectra_number:
        if data_list[rank_now] == data_list[start_rank]:
            rank_now += 1
            continue
        avg_rank = (start_rank + rank_now -1 ) /2
        value_to_relative[data_list[start_rank]] = 1.0 * avg_rank / spectra_number
        start_rank = rank_now
        rank_now += 1
    value_to_relative[data_list[start_rank]] = 1.0 * (start_rank+rank_now -1)/(
            2*(spectra_number))
    for i in range(0, len(data_list)):
        relative_list.append(value_to_relative[result_array[i]])
    return np.array(relative_list)

dict_calculator = {
        'basic': BasicCalculator(),
        'relative': RelativeCalculator(),
        }

def create_calculator(dict_experiment):
    if dict_experiment['method'] == 'basic':
        return create_basic_calculator(dict_experiment['formula'], dict_experiment['ratio_for_before'], dict_experiment['ratio_for_after'])
    elif dict_experiment['method'] == 'change':
        return create_change_calculator(dict_experiment['formula'], dict_experiment['ratio_for_change'], dict_experiment['ratio_for_basic'])
    elif dict_experiment['method'] == 'method':
        return create_method_calculator(dict_experiment['formula'], dict_experiment['ratio_for_before'], dict_experiment['ratio_for_after'], dict_experiment['spectra_dict'], dict_experiment['ratio_for_method'])
    elif dict_experiment['method'] == 'test_last':
        return create_test_last_calculator(dict_experiment['formula'], dict_experiment['ratio_for_last'])
    elif dict_experiment['method'] == 'method_last':
        return create_method_last_calculator(dict_experiment['formula'], dict_experiment['ratio_for_last'], dict_experiment['ratio_for_method'], dict_experiment['spectra_dict'])

def create_basic_calculator(formula, ratio_for_before, ratio_for_after):
    return IntegratedCalculator(CalculatorGZoltarWithFormula(formula), CalculatorSumOfSpcetra(ratio_for_before, ratio_for_after))

def create_change_calculator(formula, ratio_for_change, ratio_for_basic=1.0):
    return IntegratedCalculator(CalculatorGZoltarWithFormula(formula), CalculatorChangeOfHit(ratio_for_change, ratio_for_basic))

def create_method_calculator(formula, ratio_for_before, ratio_for_after, spectra_dict, ratio_for_method):
    calculator =  MethodCalculator(CalculatorGZoltarWithFormula(formula), CalculatorSumOfSpcetra(ratio_for_before, ratio_for_after), ratio_for_method)
    calculator.prepare_data(spectra_dict)
    return calculator

def create_method_last_calculator(formula, ratio_for_last, ratio_for_method, spectra_dict):
    calculator = MethodCalculator(CalculatorTestLast(formula, ratio_for_last), None, ratio_for_method)
    calculator.prepare_data(spectra_dict)
    return calculator

def create_test_last_calculator(formula, ratio_for_last):
    return IntegratedCalculator(CalculatorTestLast(formula, ratio_for_last), None)

class IntegratedCalculator:
    def __init__(self, gzoltar_calculator, insert_calculator):
        self.gzoltar_calculator = gzoltar_calculator
        self.insert_calculator = insert_calculator

    def cal_gzoltar(self, gzoltar_spectra):
        return self.gzoltar_calculator.cal_gzoltar(gzoltar_spectra)

    def cal_insert(self, insert_spectra):
        return self.insert_calculator.cal_insert(insert_spectra)

class MethodCalculator(IntegratedCalculator):
    def __init__(self, gzoltar_calculator, insert_calculator, ratio_for_method):
        IntegratedCalculator.__init__(self, gzoltar_calculator, insert_calculator)
        self.method_dict = {}
        self.ratio_for_method = ratio_for_method

    def prepare_data(self, spectra_dict):
        for (key, spectra) in spectra_dict.items():
            self.method_dict[key] = super().cal_gzoltar(spectra)
        
    def cal_gzoltar(self, gzoltar_spectra):
        return super().cal_gzoltar(gzoltar_spectra) + self.method_dict.get(gzoltar_spectra.method_name(), 0.0)* self.ratio_for_method

    def cal_insert(self, insert_spectra):
        return super().cal_insert(insert_spectra) + self.method_dict.get(insert_spectra.method_name(), 0.0) * self.ratio_for_method

class CalculatorGZoltarWithFormula:
    def __init__(self, formula_for_spectra):
        self.formula_for_spectra = formula_for_spectra

    def cal_gzoltar(self, gzoltar_spectra):
        # print('cal_gzoltar: %s' % gzoltar_spectra.hit_pass)
        return calculate_value(self.formula_for_spectra, 
                gzoltar_spectra.hit_pass, gzoltar_spectra.hit_fail,
                gzoltar_spectra.miss_pass, gzoltar_spectra.miss_fail)

class CalculatorSumOfSpcetra:
    def __init__(self, ratio_for_before, ratio_for_after):
        self.ratio_for_before = ratio_for_before
        self.ratio_for_after = ratio_for_after

    def cal_insert(self, insert_spectra):
        return self.ratio_for_before * insert_spectra.spectra_before.get_suspicious_value() + self.ratio_for_after * insert_spectra.spectra_after.get_suspicious_value()

class CalculatorTestLast(CalculatorGZoltarWithFormula):
    def __init__(self, formula_for_spectra, ratio_for_last):
        CalculatorGZoltarWithFormula.__init__(self, formula_for_spectra)
        self.ratio_for_last = ratio_for_last
        self.last_spectra = None

    def cal_gzoltar(self, gzoltar_spectra):
        value = super().cal_gzoltar(gzoltar_spectra)
        if self.last_spectra is not None and self.last_spectra.same_method(gzoltar_spectra):
            value = value * (1 - self.ratio_for_last) + self.ratio_for_last * super().cal_gzoltar(self.last_spectra)
        self.last_spectra = gzoltar_spectra
        return value

class CalculatorChangeOfHit:
    def __init__(self, ratio_for_change, ratio_for_basic=1.0):
        self.ratio_for_change = ratio_for_change
        self.ratio_for_basic = ratio_for_basic

    def cal_insert(self, insert_spectra):
        change_spectra = abs(insert_spectra.spectra_after.hit_pass - insert_spectra.spectra_before.hit_pass) + abs(insert_spectra.spectra_after.hit_fail - insert_spectra.spectra_before.hit_fail)
        return insert_spectra.spectra_after.get_suspicious_value()*self.ratio_for_basic*(1+self.ratio_for_change * (1 - math.exp(-1.0*change_spectra)))

class Solver:
    def __init__(self):
        pass

    dict_info_type = {
        'method_call': False,
        'variable': False,
        'variable_block': False,
        'predicate': False,
        'key': False,
        }

    def solve(self, data):
        return data

    def method_level(self):
        return False

    def class_level(self):
        return False

    def method_granularity_solver(self):
        return False

    def accept_task(self, running_task, dict_experiment, data_list):
        return data_list

    def need_info(self, info_type):
        return self.dict_info_type.get(info_type, False)

class MethodLevelSolver(Solver):
    def method_level(self):
        return True

    def accept_task(self, running_task, dict_experiment, data_list):
        return running_task.method_solve(self, dict_experiment, data_list)

    def need_info(self, info_type):
        # print('check info')
        ans = self.dict_info_type.get(info_type, None)
        if ans is None:
            # print(super())
            return super().need_info(info_type)
        else:
            return ans

class MethodGranularitySolver(Solver):
    def method_granularity_solver(self):
        return True

class ClassLevelSolver(Solver):
    def class_level(self):
        return True
    
    def accept_task(self, running_task, dict_experiment, data_list):
        return running_task.class_solve(self, dict_experiment, data_list)

    def need_info(self, info_type):
        ans = self.dict_info_type.get(info_type, None)
        if ans is None:
            return super().need_info(info_type)
        else:
            return ans

class MethodSolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        super().__init__()
        self.ratio_for_method = dict_experiment.get(
                'ratio_for_method', 0.0)

    def solve(self, data, dict_experiment):
        new_data = np.array(data).copy()
        method_sus_value = dict_experiment['suspicious_method'].get(
                dict_experiment['local_spectra'][0].method_name(), 0.0)
        # new_data += data[0] * self.ratio_for_method
        # new_data += new_data[0] * self.ratio_for_method
        new_data += method_sus_value * self.ratio_for_method
        return new_data

class MethodCallSolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        super().__init__()
        self.ratio_for_method_call = dict_experiment.get(
                'ratio_for_method_call', 0.0)
   
    dict_info_type = {
        'method_call': True,
        }

    def solve(self, data, dict_experiment):
        local_spectra = dict_experiment['local_spectra']
        dict_method_call = dict_experiment['method_call']
        for i in range(0, len(local_spectra)):
            call_list = dict_method_call.get(local_spectra[i].name, [])
            #if len(call_list) != 0:
            #    print(local_spectra[i].name) 
            for callee_method in call_list:
                data[i] += dict_experiment['suspicious_method'].get(
                        callee_method, 0.0) * self.ratio_for_method_call
                #print(dict_experiment['suspicious_method'].get(
                #        callee_method, 0.0) * self.ratio_for_method_call)
        return data

class CompareSolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        pass

    def solve(self, data, dict_experiment):
        new_data = np.array(data)
        local_spectra = dict_experiment['local_spectra']
        # the start of method cannot be insert spectra
        for i in range(1, len(new_data)):
            if local_spectra[i].is_insert():
                if new_data[i] <= 0.0:
                    new_data[i] = new_data[i-1]
        return new_data

class SelectBestSolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        pass

    def solve(self, data, dict_experiment):
        new_data = np.array(data)
        local_spectra = dict_experiment['local_spectra']
        for i in range(1, len(new_data)):
            if local_spectra[i].is_insert():
                new_data[i] = max(new_data[i], new_data[i-1])
        return new_data

class ConvSolver(MethodLevelSolver):
    # def __init__(self, conv, loc):
    def __init__(self, dict_experiment):
        super().__init__()
        # self.conv = conv
        # self.loc = loc
        self.conv = dict_experiment['conv']
        self.loc = dict_experiment['loc']

    def padding(self, data):
        return np.array([data[0] for i in range(self.loc)] + list(data[:]) +\
                [data[-1] for i in range(len(self.conv)-self.loc)]) 

    def solve(self, data, dict_experiment):
        new_data = np.zeros(np.array(data).shape)
        # print('origin data: %s' % data)
        # data = self.padding(data) 
        data = self.padding(data)
        for i in range(0, len(self.conv)):
            # print(new_data.shape)
            # print(data[i:i+len(new_data)].shape)
            new_data += self.conv[i] * data[i:i+len(new_data)] 
        return new_data

class ConvSolverZeroBorder(ConvSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    def padding(self, data):
        return np.array([0.0 for i in range(self.loc)] + list(data[:]) +\
                [0.0 for i in range(len(self.conv)-self.loc)])

class ConvSquareBorder(ConvSolverZeroBorder):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    def solve(self, data, dict_experiment):
        new_data = np.zeros(np.array(data).shape)
        data = self.padding(data)
        for i in range(0, len(self.conv)):
            new_data += self.conv[i] * (data[i:i+len(new_data)] ** 2)
        return np.sqrt(new_data)

class BranchSolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        pass

    dict_info_type = {
            'branch': True,
            }

    def solve(self, data, dict_experiment):
        new_data = np.array(data).copy()
        local_spectra = dict_experiment['local_spectra']
        branch_dict = dict_experiment['branch_result']
        # print(type(branch_dict))
        for i in range(0, len(local_spectra)):
            spectra_now = local_spectra[i]
            if not spectra_now.is_insert():
                new_data[i] = max(new_data[i], branch_dict.get(spectra_now.name, 0.0))
            else:
                #new_data[i] = max([new_data[i],
                #    branch_dict.get(spectra_now.spectra_before.name, 0.0),
                #    branch_dict.get(spectra_now.spectra_after.name, 0.0)])
                new_data[i] = self.cal_for_insert(
                        i, new_data, spectra_now, branch_dict)
        return new_data

    @staticmethod
    def cal_for_insert(loc, new_data, spectra_now, branch_dict):
        return max([new_data[loc],
                    branch_dict.get(spectra_now.spectra_before.name, 0.0),
                    branch_dict.get(spectra_now.spectra_after.name, 0.0)])
 

class BranchCondSolver(BranchSolver):
    def __init__(self, dict_experiment):
        pass

    @staticmethod
    def cal_for_insert(loc, new_data, spectra_now, branch_dict):
        return new_data[loc]

class PredicateNumberSolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        self.full_number = dict_experiment.get('full_number', 3)
        self.base_ratio = dict_experiment.get('base_ratio', 0.6)

    dict_info_type = {
            'predicate': True,
            }

    def solve(self, data, dict_experiment):
        new_data = np.array(data).copy()
        local_spectra = dict_experiment['local_spectra']
        dict_predicate = dict_experiment['predicate']
        ratio = np.ones(new_data.shape)
        predicate_number = 0
        for spectra_now in local_spectra:
            if not spectra_now.is_insert():
                if dict_predicate.get(spectra_now.name, None) is not None:
                    predicate_number += 1
        ratio_number = min(self.base_ratio + (1-self.base_ratio)*predicate_number/self.full_number, 1.0)
        for i in range(0, len(local_spectra)):
            # if i % 2 == 1:
            if self.if_set_ratio(local_spectra[i]):
                ratio[i] = ratio_number
        return new_data * ratio

    @staticmethod
    def if_set_ratio(spectra):
        return spectra.is_insert()

class PredicateDensitySolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        self.full_ratio = dict_experiment.get('full_ratio', 0.3)
        self.base_ratio = dict_experiment.get('base_ratio', 0.6)

    def solve(self, data, dict_experiment):
        local_spectra = dict_experiment['local_spectra']
        dict_predicate = dict_experiment['predicate']
        predicate_number = 0
        for spectra_now in local_spectra:
            if not spectra_now.is_insert():
                if dict_predicate.get(spectra_now.name, None) is not None:
                    predicate_number += 1
        ratio_number = min(self.base_ratio + (1-self.base_ratio)*predicate_number/(len(local_spectra)*self.full_ratio), 1.0)
        return data * ratio_number

# A special test, all statement are set ratio, instead of only insert ones.
class PredicateAllSolver(PredicateNumberSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    @staticmethod
    def if_set_ratio(spectra):
        return True

class PredicateLocSolver(MethodLevelSolver):
    def __init__(self, dict_experiment):
        self.full_number = dict_experiment.get('full_number', 3)
        self.ratio = dict_experiment.get('ratio', 0.2)
        self.base_number = dict_experiment.get('base_number', 3)

    dict_info_type = {
            'predicate': True,
            'variable': True,
            }

    def solve(self, data, dict_experiment):
        local_spectra = dict_experiment['local_spectra']
        dict_variable = dict_experiment['variable']
        # dict_predicate = dict_experiment['predicate']
        dict_predicate = self.return_predicate(dict_experiment)
        ratio_vector = np.ones(data.shape)
        times_predicate = {}
        for spectra_now in local_spectra:
            if not spectra_now.is_insert():
                variable_list = dict_predicate.get(spectra_now.name, [])
                for variable_now in variable_list:
                    if times_predicate.get(variable_now, None) is None:
                        times_predicate[variable_now] = 0
                    times_predicate[variable_now] += 1
        # base_value = 1.0 - self.ratio * self.base_number
        base_value = self.base_value_vector(local_spectra)
        # max_value = base_value + self.full_number * self.ratio
        max_value = self.max_value_vector(base_value, local_spectra)
        count_vector = np.zeros([len(local_spectra)])
        for i in range(0, len(local_spectra)):
            # if local_spectra[i].is_insert():
            if self.if_set_ratio(local_spectra[i]):
                count = 0
                variable_set = self.get_variable_set(dict_experiment, local_spectra[i])
                # print(variable_set)
                if len(variable_set) == 0:
                    count = self.return_empty_count(variable_set, local_spectra[i])
                else:
                    for variable_now in variable_set:
                        count += times_predicate.get(variable_now, 0)
                count_vector[i] = count
                #ratio_vector[i] = np.min([max_value, base_value + self.ratio * count], axis=0)
        #print(times_predicate)
        ratio_vector = np.min([max_value, base_value + self.ratio * count_vector], axis=0)
        # print(ratio_vector)
        return ratio_vector * data

    def return_empty_count(self, variable_set, spectra_now):
        return 0

    def base_value_vector(self, local_spectra):
        return np.array(
                [1.0 - self.ratio * self.base_number for i in local_spectra])
    
    def max_value_vector(self, base_vector, local_spectra):
        return base_vector + self.ratio * self.full_number

    @staticmethod
    def return_predicate(dict_experiment):
        return dict_experiment['predicate']

    @staticmethod
    def if_set_ratio(spectra):
        return spectra.is_insert()
        
    @staticmethod
    def get_variable_set(dict_experiment, spectra_now):
        #print(spectra_now.spectra_before.name)
        #print(list(dict_variable.keys())[0])
        dict_variable = dict_experiment['variable']
        varaible_before = set(dict_variable.get(spectra_now.spectra_before.name, []))
        variable_after = set(dict_variable.get(spectra_now.spectra_after.name, []))
        return varaible_before.union(variable_after)        

class PredicateBlockSolver(PredicateLocSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    dict_info_type = {
            'variable_block': True,
            'predicate': True,
            }

    @staticmethod
    def get_variable_set(dict_experiment, spectra_now):
        dict_variable = dict_experiment['variable_block']
        varaible_before = set(dict_variable.get(spectra_now.spectra_before.name, []))
        variable_after = set(dict_variable.get(spectra_now.spectra_after.name, []))
        return varaible_before.union(variable_after)        

class PredicateBothJudgeSolver(PredicateLocSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    @staticmethod
    def if_set_ratio(self):
        return True

    dict_info_type = {
            'variable_block' : True,
            'variable': True,
            'predicate': True,
            }

    @staticmethod
    def get_variable_set(dict_experiment, spectra_now):
        # print('really work')
        if spectra_now.is_insert():
            dict_variable = dict_experiment['variable_block']
            varaible_before = set(dict_variable.get(spectra_now.spectra_before.name, []))
            variable_after = set(dict_variable.get(spectra_now.spectra_after.name, []))
            return varaible_before.union(variable_after)
        else:
            dict_variable = dict_experiment['variable']
            return set(dict_variable.get(spectra_now.name, []))

class KeyBothSolver(PredicateBothJudgeSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    dict_info_type = {
            'variable_block' : True,
            'variable': True,
            'key': True,
            }

    @staticmethod
    def return_predicate(dict_experiment):
        return dict_experiment['key']

class KeyDiffSolver(KeyBothSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)
        self.base_for_change = float(dict_experiment.get('base_change', 3))
        self.full_for_change = float(dict_experiment.get('full_change', 3))

    def base_value_vector(self, local_spectra):
        base_value_vector = np.ones([len(local_spectra)])
        for i in range(0, len(local_spectra)):
            if local_spectra[i].is_insert():
                base_value_vector[i] -= self.ratio * self.base_number
            else:
                base_value_vector[i] -= self.ratio * self.base_for_change
        # print(base_value_vector)
        return base_value_vector

    def max_value_vector(self, base_vector, local_spectra):
        dict_num = {True: self.full_number, False: self.full_for_change}
        full_vector = np.array([dict_num[spectra.is_insert()] for 
            spectra in local_spectra])
        # print(full_vector)
        # print(base_vector + self.ratio * full_vector)
        return base_vector + self.ratio * full_vector 

class KeyEmptySolver(KeyDiffSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    def return_empty_count(self, variable_set, spectra_now):
        if spectra_now.is_insert():
            return self.base_number
        else:
            return self.base_for_change

class KeyDensitySolver(KeyBothSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    def solve(self, data, dict_experiment):
        local_spectra = dict_experiment['local_spectra']
        dict_variable = dict_experiment['variable']
        # dict_predicate = dict_experiment['predicate']
        dict_predicate = self.return_predicate(dict_experiment)
        ratio_vector = np.ones(data.shape)
        weight_base, weight_predicate = self.weight_calculate(
                local_spectra, dict_predicate)
        base_value = 1.0 - self.ratio
        # max_value = base_value + self.full_number * self.ratio
        max_value = 1.0
        for i in range(0, len(local_spectra)):
            # if local_spectra[i].is_insert():
            if self.if_set_ratio(local_spectra[i]):
                weight = 0
                variable_set = self.get_variable_set(dict_experiment, local_spectra[i])
                # print(variable_set)
                for variable_now in variable_set:
                    weight += weight_predicate.get(variable_now, 0)
                ratio_vector[i] = min(max_value, base_value + self.ratio * weight/(self.full_number*weight_base))
        #print(weight_predicate)
        #print(ratio_vector)
        return ratio_vector * data
 
    def weight_calculate(self, local_spectra, dict_predicate):
        weight_predicate = {}
        weight_base = 0
        for spectra_now in local_spectra:
            if not spectra_now.is_insert():
                variable_list = dict_predicate.get(spectra_now.name, [])
                if len(variable_list) > 0:
                    weight_base += 1
                for variable_now in variable_list:
                    if weight_predicate.get(variable_now, None) is None:
                        weight_predicate[variable_now] = 0
                    weight_predicate[variable_now] += 1
        # base_value = 1.0 - self.ratio * self.base_number
        weight_base = max(weight_base, self.base_number)
        return weight_base, weight_predicate
       
class KeyPredicateDensitySolver(KeyDensitySolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    #@Override
    def weight_calculate(self, local_spectra, dict_predicate):
        weight_predicate = {}
        weight_base = 0
        for spectra_now in local_spectra:
            if not spectra_now.is_insert():
                variable_list = dict_predicate.get(spectra_now.name, [])
                if len(variable_list) > 0:
                    weight_base += 1
                for variable_now in variable_list:
                    if weight_predicate.get(variable_now, None) is None:
                        weight_predicate[variable_now] = 0
                    weight_predicate[variable_now] += 1.0 / len(variable_list)
        # base_value = 1.0 - self.ratio * self.base_number
        weight_base = max(1.0, min(weight_base, self.base_number))
        return weight_base, weight_predicate


class VariableSolver(ClassLevelSolver):
    def __init__(self, dict_experiment):
        super().__init__()
        self.ratio_variable = dict_experiment.get('ratio_variable', 0.0)

    dict_info_type = {
            'variable': True,
            }

    def get_variable(self, dict_variable, spectra_now):
        return dict_variable.get(spectra_now.name, [])

    def solve(self, data, dict_experiment):
        # print('start to solve')
        new_data = np.array(data).copy()
        dict_variable = dict_experiment['variable']
        local_spectra = dict_experiment['local_spectra']
        variable_used = {}
        variable_count = 0
        for spectra_now in local_spectra:
            for variable in dict_variable.get(spectra_now.name, []):
                if not variable in variable_used:
                    # print('variable: %s; count: %d' % (variable, variable_count))
                    variable_used[variable] = variable_count
                    variable_count += 1
        weight_matrix = np.zeros((len(local_spectra), len(variable_used)))
        # print('weight_matrix_shape: %s' % str(weight_matrix.shape))
        for i in range(0, len(local_spectra)):
            # for variable in dict_variable.get(local_spectra[i].name, []):
            for variable in self.get_variable(dict_variable, local_spectra[i]):
                # print('%d, %d' % (i, variable_used[variable]))
                weight_matrix[i][variable_used[variable]] = 1.0
        # print('sum: %d' % np.sum(weight_matrix))
        variable_suspicious = self.cal_variable_suspicious(weight_matrix, data, local_spectra)
        to_divide = np.sum(weight_matrix, axis=1)
        #for i in range(0, to_divide.shape[0]):
        #    if to_divide[0] == 0.0:
        #        to_divide[0] 
        weight_matrix = (weight_matrix.T 
                / (np.sum(weight_matrix, axis=1)+1.0)).T
        # print('weight_matrix: %s' % weight_matrix)
        new_data += np.dot(weight_matrix, 
                variable_suspicious) * self.ratio_variable
        return new_data
       
    def cal_variable_suspicious(self, weight_matrix, data, local_spectra):
        fail_vector = np.array([
            1.0 if x.hit_fail>= 1.0 else 0.0 for x in local_spectra])
        sus_vector = np.max(weight_matrix.T * data, axis=1)
        # print('sus_vector %s' % sus_vector)
        fail_count = np.dot(weight_matrix.T, fail_vector)
        # print('fail_count: %s' % fail_count)
        total_count = np.sum(weight_matrix, axis = 0)
        # print('total_count: %s' % total_count)
        return sus_vector * fail_count / total_count

class InsertVariableSolver(VariableSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)
        
    def get_variable(self, dict_variable, spectra_now):
        if not spectra_now.is_insert():
            return dict_variable.get(spectra_now.name, [])
        else:
            spectra_list = spectra_now.name.split("->")
            used = []
            for spectra_name in spectra_list:
                used += dict_calculator.get(spectra_name, [])
            return used


class AvgVariableSolver(InsertVariableSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)

    def cal_variable_suspicious(self, weight_matrix, data, local_spectra):
        fail_vector = np.array([
            1.0 if x.hit_fail>= 1.0 else 0.0 for x in local_spectra])
        sus_vector = np.mean(weight_matrix.T * data, axis=1)
        # print('sus_vector %s' % sus_vector)
        fail_count = np.dot(weight_matrix.T, fail_vector)
        # print('fail_count: %s' % fail_count)
        total_count = np.sum(weight_matrix, axis = 0)
        # print('total_count: %s' % total_count)
        return sus_vector * fail_count / total_count

class AccumulateVariableSolver(InsertVariableSolver):
    def __init__(self, dict_experiment):
        super().__init__(dict_experiment)
        self.accumulate_coefficient = dict_experiment.get(
                'accumulate_coefficient', 2.0)

    def cal_variable_suspicious(self, weight_matrix, data, local_spectra):
        fail_vector = np.array([
            1.0 if x.hit_fail>= 1.0 else 0.0 for x in local_spectra])
        sus_vector = np.mean(weight_matrix.T * data, axis=1)
        total_count = denominator(np.sum(weight_matrix, axis = 0))
        accumulate_vector = np.ones(total_count.shape)*self.accumulate_coefficient - np.ones(total_count.shape)*(self.accumulate_coefficient-1.0)/total_count
        return sus_vector * accumulate_vector

class PageRankSolver(MethodGranularitySolver):
    def __init__(self, dict_experiment):
        super().__init__()
        print('create page rank solver')
        self.ratio_transfer = dict_experiment.get('ratio_transfer', 0.5)
        self.transfer_times = dict_experiment.get('transfer_times', 3)
       
    dict_info_type = {
            'method_call': True,
            }

    def solve(self, data_list, dict_experiment):
        # print('cal page rank')
        spectra_list = dict_experiment['spectra_list']
        dict_method_call = dict_experiment['method_call']
        weight_matrix = np.zeros((len(data_list), len(data_list)))
        dict_spectra_no = {}
        for i in range(0, len(data_list)):
            dict_spectra_no[spectra_list[i].method_name()] = i
        for caller, callee_list in dict_method_call.items():
            caller_method = caller.split(':')[0]
            for callee_method in callee_list:
                caller_no = dict_spectra_no.get(caller_method, None)
                callee_no = dict_spectra_no.get(callee_method, None)
                if caller_no is not None and callee_no is not None:
                    weight_matrix[callee_no][caller_no] += 1.0
        receiver_coefficient = np.array([[(s.hit_fail/(s.hit_fail+s.hit_pass+1))] for s in spectra_list])
        weight_matrix = weight_matrix * receiver_coefficient
        for i in range(0, len(data_list)):
            weight_matrix[i][i] = 1.0
        caller_sum = denominator(np.sum(weight_matrix, axis=0))
        weight_matrix /= caller_sum
        sus_running = np.array(data_list).copy()
        for i in range(0, self.transfer_times):
            sus_running = np.dot(weight_matrix, sus_running) * self.ratio_transfer + (1.0-self.ratio_transfer) * data_list
        # return self.ratio_transfer * sus_running + (1.0-self.ratio_transfer) * data_list
        return sus_running

def page_rank_cal(data_list, dict_experiment, spectra_list, ratio_transfer=0.5, transfer_times=3):
    # spectra_list = dict_experiment['spectra_list']
    dict_method_call = dict_experiment['method_call']
    weight_matrix = np.zeros((len(data_list), len(data_list)))
    dict_spectra_no = {}
    for i in range(0, len(data_list)):
        dict_spectra_no[spectra_list[i].method_name()] = i
    for caller, callee_list in dict_method_call.items():
        caller_method = caller.split(':')[0]
        for callee_method in callee_list:
            caller_no = dict_spectra_no.get(caller_method, None)
            callee_no = dict_spectra_no.get(callee_method, None)
            if caller_no is not None and callee_no is not None:
                weight_matrix[callee_no][caller_no] += 1.0
    receiver_coefficient = np.array([[(s.hit_fail/(s.hit_fail+s.hit_pass+1))] for s in spectra_list])
    weight_matrix = weight_matrix * receiver_coefficient
    for i in range(0, len(data_list)):
        weight_matrix[i][i] = 1.0
    caller_sum = denominator(np.sum(weight_matrix, axis=0))
    weight_matrix /= caller_sum
    sus_running = np.array(data_list).copy()
    for i in range(0, transfer_times):
        sus_running = np.dot(weight_matrix, sus_running) * ratio_transfer + (1.0-ratio_transfer) * data_list
    # return ratio_transfer * sus_running + (1.0-ratio_transfer) * data_list
    return sus_running

solver_dict = {
        'conv_non_zero': ConvSolver,
        'conv': ConvSolverZeroBorder,
        'method': MethodSolver,
        'method_call': MethodCallSolver,
        'variable': VariableSolver,
        'insert_variable': InsertVariableSolver,
        'page_rank': PageRankSolver,
        'avg_variable': AvgVariableSolver,
        'accumulate_variable': AccumulateVariableSolver,
        'branch_number': PredicateNumberSolver,
        'branch_all': PredicateAllSolver,
        'branch_loc': PredicateLocSolver,
        'branch_block': PredicateBlockSolver,
        'branch_loc_both': PredicateBothJudgeSolver,
        'branch_den': PredicateDensitySolver,
        'key_both': KeyBothSolver,
        'key_density': KeyDensitySolver,
        'conv_square': ConvSquareBorder,
        'key_pre_density': KeyPredicateDensitySolver,
        'key_diff': KeyDiffSolver,
        'key_empty': KeyEmptySolver,
        'branch': BranchSolver,
        'branch_cond': BranchCondSolver,
        'compare': CompareSolver,
        'select_best': SelectBestSolver,
        }

def create_solver(solver_parameter_dict):
    return solver_dict[solver_parameter_dict['mode']](solver_parameter_dict)
