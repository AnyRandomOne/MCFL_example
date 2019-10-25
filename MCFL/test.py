import Version
import sbfl
import calculator
import fault
import numpy as np

# this is because the class name in ast analysis and GZoltar spectra are not same.
def test_spectra_align(project, no):
    version = Version.create_version(project, no)
    original_spectra = version.return_spectra()
    spectra_matrix = sbfl.SpectraMatrix(original_spectra)
    ast_info_list = version.return_ast_info()
    node = ast_info_list[0]
    print('GZoltarSpectra')
    print(list(spectra_matrix.spectra_matrix.keys())[0])
    print('node')
    print(node.info_file)

def test_extract(project, no):
    version = Version.create_version(project, no)
    version.extract_AST()

def test_calculator(project, no):
    version = Version.create_version(project, no)
    fault_list = fault.analyze_fault_location(version, fault.ControlCollector())
    spectra_list = version.return_spectra_add()
    calculator_used = calculator.create_change_calculator('cohen', 0.2)
    spectra_list += sbfl.insert_spectra(spectra_list)
    for spectra in spectra_list:
        spectra.calculate_suspicious_value(calculator_used)
    spectra_list.sort(reverse=True)

def test_formula(formula, hit_pass, hit_fail, miss_pass, miss_fail):
    print( calculator.calculate_value(formula, hit_pass, hit_fail, miss_pass, miss_fail))

def test_return_methods(project, no):
    version = Version.create_version(project, no)
    spectra_list = version.return_spectra_add()
    spectra_dict = sbfl.get_method_spectra(spectra_list)
    for key in list(spectra_dict.keys())[:25]:
        print(key)
        print(spectra_dict[key])
    return spectra_dict

def test_conv():
    conv_solver = calculator.ConvSolver([1,2,1],1)
    l = conv_solver.solve([1,2,3,4])
    return l

def test_relative():
    array = np.array([3, 1, 2, 4])
    print(calculator.to_relative(array))

def test_transfer():
    print(sbfl.transform_spectra_from_asm("org.apache.commons.lang3.mutable.MutableInt#toInteger()Ljava/lang/Integer;:222"))
    print(sbfl.transform_method_from_asm("org.apache.commons.lang3.mutable.MutableInt#intValue()I"))
    print(sbfl.transform_method_from_asm("org.apache.commons.lang3.AnnotationUtils$1#<init>()V"))
    print(sbfl.transform_spectra_from_asm("org.apache.commons.lang3.text.StrBuilder$StrBuilderReader#read([CII)I:2879"))
    print(sbfl.transform_spectra_from_asm("org.apache.commons.lang3.text.FormattableUtils#append(Ljava/lang/CharSequence;Ljava/util/Formatter;III)Ljava/util/Formatter;:83"))

def test_matrix_variable():
    weight_matrix = np.array([[1, 0, 1, 0], [1, 1, 1, 0], [1, 0, 0, 1]])
    print('weight_matrix:\n %s' % weight_matrix)
    print('weight_shape:\n %s' % str(weight_matrix.shape))
    fail_vector = np.array([1, 0, 1])
    data = np.random.random((3,))
    print('data:\n %s' % data)
    sus_vector = np.max(weight_matrix.T * data, axis=1)
    fail_count = np.dot(weight_matrix.T, fail_vector)
    total_count = np.sum(weight_matrix, axis = 0)
    variable_suspicious = sus_vector * fail_count / total_count
    print('variable_suspicious:\n %s' % variable_suspicious)
    weight_matrix = (weight_matrix.T / np.sum(weight_matrix, axis=1)).T
    print('new_weight_matrix:\n %s' % weight_matrix)
    data += np.dot(weight_matrix, variable_suspicious) * 0.1
    print('new_data:\n %s' % data)
        
def test_extract_variable():
    version = Version.create_version('Lang', 1)
    version.extract_variable()
    version.transfer_variable()

def test_extract_predicate():
    version = Version.create_version('Lang', 1)
    version.extract_predicate()
    version.transfer_predicate()

def test_read_ast_info():
    version = Version.create_version('Lang', 1)
    version.return_ast_info()

def test_block():
    version = Version.create_version('Lang', 1)
    # version.transfer_block_info()
    version.transfer_block_variable()

def test_dict_info():
    judge_list = ['method_call', 'variable', 'variable_block', 'predicate', 'key']
    basic_solver = calculator.Solver()
    method_call = calculator.MethodCallSolver({})
    both = calculator.PredicateBothJudgeSolver({})
    acc = calculator.AccumulateVariableSolver({})
    for solver in [basic_solver, method_call, both, acc]:
        print(str(solver))
        for to_judge in judge_list:
            print('%s : %s' % (to_judge, solver.need_info(to_judge)))

def test_exclude_spectra():
    version =  Version.create_version('Lang', 1)
    version.extract_exclude()

def test_branch():
    version = Version.create_version('Lang', 1)
    version.extract_branch_info()

if __name__ == '__main__':
    #test_exclude_spectra() 
    test_branch()
