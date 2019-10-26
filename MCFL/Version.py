import csv
import os
import linecache
import re
import sbfl
import util

# used for extract the valid part of path for compare in AST info
#src_dict = {
#        'Time': ['src/main/java/'],
#        'Lang': ['src/main/java/', 'src/java/'],
#        'Math': ['src/main/java/', 'src/java/'],
#        'Chart': ['source/'],
#        'Closure': ['src/'],
#        'Mockito': ['src/'],
#}

# move to the only location use it
# src_list = ['src/main/java/', 'src/java/', 'src/', 'source/'] 

max_no = {
        'Time' : 27,
        'Chart' : 26,
        'Closure' : 133,
        'Lang' : 65, 
        'Math' : 106,
        'Mockito' : 38
}
        

class FailedTest:
    def __init__(self, name, runtime, stacktrace):
        self.name = name
        self.runtime = runtime
        self.stacktrace = stacktrace

class Version:
    MISSING_BRANCH_PATH = '../data/'
    WORKSPACE = '../workspace'
    JAR_PATH = '../AST_analyzer/target/AST_analyzer-1.0-SNAPSHOT.jar'

    def __init__(self, project_name, project_no):
        self.project_name = project_name
        self.project_no = project_no

    def name(self):
        return self.project_name

    def no(self):
        return str(self.project_no) if self.project_no >= 10 else '0%s' % self.project_no

    def __str__(self):
        return '%s @ %s' % (self.name(), self.no())

    def version_name(self):
        return '%s@%s' % (self.name(), self.no())

    def base_dir(self):
        return '%s/%s_%s_buggy' % (Version.WORKSPACE, self.project_name, self.no())
    
    def classes_dir(self):
        check_list = ['%s/target/classes' % self.base_dir(),
                '%s/build/classes/main' % self.base_dir(),
                '%s/build/classes' % self.base_dir(),
                '%s/build/' % self.base_dir(),
                ]
        for to_check in check_list:
            if os.path.exists(to_check):
                return to_check

    def method_call_dir(self):
        return '%s/method_call/%s_%s_method_call.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def method_call_without_transfer(self):
        return '%s/method_call_without_transfer/%s_%s_method_call.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def variable_call_without_transfer(self):
        return '%s/variable_without_transfer/%s_%s_variable.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def variable_block_dir(self):
        return '%s/variable_block/%s_%s_variable_block.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def variable_dir(self):
        return '%s/variable/%s_%s_variable.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def predicate_without_transfer(self):
        return '%s/predicate_without_transfer/%s_%s_predicate.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def key_dir(self):
        return '%s/key/%s_%s_key.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def key_without_transfer(self):
        return '%s/key_without_transfer/%s_%s_key.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def predicate_dir(self):
        return '%s/predicate/%s_%s_predicate.csv' % (
                Version.MISSING_BRANCH_PATH, self.project_name, self.no())

    def spectra_add_dir(self):
        return '%s/spectra_add/%s_%s_spectra.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def cal_result_dir(self, formula):
        return '%s/result/%s_%s_%s_rank.csv' % (
            Version.MISSING_BRANCH_PATH, self.name(), self.no(), formula)

    def spectra_sort_result_dir(self):
        return '%s/result/%s_%s_rank.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def fault_result_dir(self):
        return '%s/result/%s_%s_fault.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def analyze_dir(self):
        return '%s/result/%s_%s_analyze.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def spectra_dir(self):
        return '%s/spectra_GZoltar/%s_%s/spectra.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def exclude_spectra_dir(self):
        return '%s/exclude_spectra/%s_%s_exclude.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def fault_location(self):
        return '%s/fault_location/location_result_of_%s.csv' % (
                Version.MISSING_BRANCH_PATH, self.name())

    def return_spectra_exclude(self):
        path = self.exclude_spectra_dir()
        reader = csv.DictReader(open(path))
        result = []
        for row in reader:
            result.append(row['name'])
        return result

    def return_spectra(self):
        # the spectra file has been transferred to missing branch file
        # path = '%s/spectra.csv' % self.gzoltar_txt_dir()
        path = self.spectra_dir()
        reader = csv.DictReader(open(path), delimiter=';')
        result = {}
        #last_statement = None
        for row in reader:
            result[row['name']] = sbfl.GZoltarSpectra(row['name'], row['hit_pass'], row['hit_fail'], row['miss_pass'], row['miss_fail'])
        # print('read spectra: %s' % len(result))
        return result

    # I am wondering list and dict which is better...
    def return_spectra_add(self):
        path = self.spectra_add_dir()
        reader = csv.DictReader(open(path))
        result = []
        for row in reader:
            result.append(sbfl.GZoltarSpectra(row['name'], row['hit_pass'], row['hit_fail'], row['miss_pass'], row['miss_fail']))
        return result

    def return_branch_info(self):
        path = self.branch_info()
        reader = csv.DictReader(open(path))
        result = []
        for row in reader:
            result.append(sbfl.GZoltarBranchSpectra(row['spectra'], row['hit_pass'], row['hit_fail'], row['miss_pass'], row['miss_fail'], row['location'], bool(row['bool'])))
        return result

    def return_raw_number(self):
        spectra_list = self.return_spectra_add()
        return len(spectra_list)

    def return_number(self, number_type):
        if number_type.startswith('raw'):
            num = self.return_raw_number() 
        elif number_type.startswith('inserted'):
            num = self.return_inserted_number()
        if number_type.endswith('exclude'):
            num -= len(self.return_spectra_exclude())
        return num
        
    def return_ast_info(self):
        path = self.ast_analysis()
        reader = csv.DictReader(open(path))
        ast_info_list = []
        for row in reader:
            ast_info_list.append(sbfl.create_ast(row['type'], row['file'], row['start'], row['end']))
        return ast_info_list

    def transfer_block_info(self):
        ast_info_list = self.return_ast_info()
        #spectra_add = self.return_spectra_add()
        #spectra_dict = {}
        #for spectra_now in spectra_add:
        #    spectra_dict[spectra_now.name] = spectra_now
        spectra_dict = self.spectra_add_dict()
        spectra_matrix = sbfl.SpectraMatrix(spectra_dict)
        block_info_list = []
        for node in ast_info_list:
            if not node.is_block():
                continue
            found = node.find_spectra_name(spectra_matrix)
            if found is not None:
                block_info_list.append(found)
        # return block_info_list
        util.write_into_csv(self.ast_block(), block_info_list, ['start', 'end'])
   
    def extract_branch_info(self):
        spectra_dict = self.spectra_add_dict()
        ast_info_list = self.return_ast_info()
        spectra_matrix = sbfl.SpectraMatrix(spectra_dict)
        branch_info_list = []
        spectra_switch = None
        for node in ast_info_list:
            if node.info_type in ['abstract', 'method', 'else']:
                continue
            elif node.info_type in ['if', 'while', 'for']:
                spectra_start, spectra_end = node.find_spectra(spectra_matrix)
                if spectra_start is None:
                    continue
                spectra_next = node.find_next(spectra_matrix)
                branch_success = {'spectra': spectra_start.name,
                        'bool': True,
                        'location': 'start',
                        'hit_pass': spectra_next.hit_pass,
                        'hit_fail': spectra_next.hit_fail,
                        'miss_pass': spectra_next.miss_pass,
                        'miss_fail': spectra_next.miss_fail,}
                branch_fail = {'spectra': spectra_start.name,
                  'bool': False,
                  'location': 'start',
                  'hit_pass': spectra_start.hit_pass - spectra_next.hit_pass,
                  'hit_fail': spectra_start.hit_fail - spectra_next.hit_fail,
                  'miss_pass': spectra_start.miss_pass + spectra_next.hit_pass,
                  'miss_fail': spectra_start.miss_fail + spectra_next.hit_fail,
                  }
                branch_info_list.append(branch_success.copy())
                branch_info_list.append(branch_fail.copy())
                if spectra_end is not None:
                    branch_success['spectra'] = spectra_end.name
                    branch_fail['spectra'] = spectra_end.name
                    branch_success['location'] = 'end'
                    branch_fail['location'] = 'end'
                    branch_info_list.append(branch_success.copy())
                    branch_info_list.append(branch_fail.copy())
            elif node.info_type == 'switch':
                spectra_start, spectra_end = node.find_spectra(spectra_matrix)
                if spectra_start is not None:
                    spectra_switch = spectra_start
            elif node.info_type == 'switchEntry':
                spectra_start, spectra_end = node.find_spectra(spectra_matrix)
                if spectra_start is None or spectra_switch is None:
                    continue
                branch_fail = {'spectra': spectra_start.name,
                'bool': False,
                'location': 'start',
                'hit_pass': spectra_switch.hit_pass - spectra_start.hit_pass,
                'hit_fail': spectra_switch.hit_fail - spectra_start.hit_fail,
                'miss_pass': spectra_switch.miss_pass + spectra_switch.hit_pass,
                'miss_fail': spectra_switch.miss_fail + spectra_switch.hit_fail,
                }
                branch_info_list.append(branch_fail.copy())
        util.write_into_csv(self.branch_info(), branch_info_list, ['spectra', 
            'location', 'bool', 'hit_pass', 'hit_fail', 'miss_pass', 'miss_fail'])

    def branch_info(self):
        return '%s/branch/%s_%s.csv' % (Version.MISSING_BRANCH_PATH, 
                self.name(), self.no())

    def spectra_add_dict(self):
        spectra_add = self.return_spectra_add()
        spectra_dict = {}
        for spectra_now in spectra_add:
            spectra_dict[spectra_now.name] = spectra_now
        return spectra_dict

    def ast_block(self):
        return '%s/Ast_block/%s_%s.csv' % (Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def transfer_block_variable(self):
        variable_dict = self.read_variable()
        block_info_list = self.read_block()
        change = True
        while change:
            change = False
            for row in block_info_list:
                for variable_now in variable_dict.get(row['start'], []):
                    if not variable_now in variable_dict.get(row['end'], []):
                        if not row['end'] in variable_dict:
                            variable_dict[row['end']] = []
                        variable_dict[row['end']].append(variable_now)
                        change = True
        variable_list = []
        for key, value in variable_dict.items():
            variable_list.append({'line': key, 'variable': ";".join(value)})
        util.write_into_csv(self.variable_block_dir(), variable_list, ['line', 'variable'])            

    def ast_analysis(self):
        return '%s/AST_analysis/%s_%s.csv' % (Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def copy_result_file(self, formula):
        os.system('cp %s/%s.statements.ranking.csv %s/' % (self.gzoltar_txt_dir(), formula, self.result_Delta_4T_dir()))

    def exist_fl_result(self, fl_formula):
        return os.path.exists('%s/%s.ranking.csv' % (self.gzoltar_txt_dir(), fl_formula))

    def exist_Delta4T_data(self, formula):
        return os.path.exists('%s/%s.statements.ranking.csv' % (self.result_Delta_4T_dir(), formula))

    def last_no(self):
        return self.project_no-1 if self.project_no!=0 else max_no[self.project_name]

    def defects4j_dir(self):
        # xxx is for anonymous.
        return 'xxx/defects4j/framework/projects/%s' % self.project_name

    def gzoltar_txt_dir(self):
        return '%s/gzoltar/sfl/txt' % self.base_dir()

    def read_fail_tests_from_gzoltar(self):
        failed_tests = []
        with open('%s/gzoltar/sfl/txt/tests.csv' % self.base_dir()) as csvfile:
            reader=csv.DictReader(csvfile)
            for row in reader:
                if row['outcome'] == 'FAIL':
                    failed_tests.append(row)
        return failed_tests

    def read_out_test(self):
        failed_tests = []
        with open('%s/out_test.log' % self.base_dir()) as fin:
            for line in fin.readlines():
                if line[2] == '-':
                    failed_tests.append(line[4:-1])
        return failed_tests

    def read_trigger_tests(self):
        failed_tests = []
        with open('%s/trigger_tests/%s' % (self.defects4j_dir(), self.project_no)) as fin:
            for line in fin.readlines():
                # print(line)
                if line[0:3] == '---':
                    failed_tests.append(line[4:-1])
        return failed_tests

    def extract_AST(self):
        jar_path = Version.JAR_PATH
        order = 'allJarFilesInPath'
        src_path = '%s/%s_%s_buggy/%s' % (Version.WORKSPACE, self.name(),
                self.no(), self.src_dict())
        output_path = '%s/AST_analysis/%s_%s' % (Version.MISSING_BRANCH_PATH,
                self.name(), self.no())
        mode_order = 'border'
        os.system('java -jar %s %s %s %s %s' % (jar_path, order, src_path, mode_order, output_path))

    def extract_method_call(self):
        jar_path = Version.JAR_PATH
        file_order = 'allJarFilesInPath'
        cls_path = self.classes_dir()
        mode_order = 'method'
        middle_path = self.method_call_without_transfer()
        #print(middle_path)
        output_path = self.method_call_dir()
        os.system('java -jar %s %s %s %s %s' % (
            jar_path, file_order, cls_path, mode_order, middle_path))
        input_reader = csv.DictReader(open(middle_path))
        output_writer = csv.DictWriter(open(output_path, 'w'), ['line','method_call'])
        output_writer.writeheader()
        # print("write header")
        for row in input_reader:
            output_writer.writerow({
                'line':sbfl.transform_spectra_from_asm(row['line']),
                'method_call':sbfl.transform_method_from_asm(row['method_call']),
                })

    def transfer_variable(self):
        self.transfer_line_info(self.variable_call_without_transfer(),
                self.variable_dir(), ['variable'])

    def transfer_predicate(self):
        self.transfer_line_info(self.predicate_without_transfer(),
                self.predicate_dir(), ['variable'])

    def transfer_key(self):
        self.transfer_line_info(self.key_without_transfer(),
                self.key_dir(), ['variable'])

    def transfer_line_info(self, middle_path, output_path, info_list):
        # middle_path = self.variable_call_without_transfer()
        # output_path = self.variable_dir()
        dict_spectra = {}
        spectra_list = self.return_spectra_add()
        for spectra_now in spectra_list:
            dict_spectra[spectra_now.simplify_name()] = spectra_now.name
        #print(len(dict_spectra))
        #print(list(dict_spectra.items())[0])
        #print(dict_spectra['org.apache.commons.lang3$AnnotationUtils:83'])
        input_reader = csv.DictReader(open(middle_path))
        output_writer = csv.DictWriter(open(output_path, 'w'), ['line'] + info_list)
        output_writer.writeheader()
        # print("write header")
        cannot_found = 0
        for row in input_reader:
            try:
                row['line'] = dict_spectra[row['line']]
                output_writer.writerow(row)
                #output_writer.writerow({
                #    'line':dict_spectra[row['line']],
                #    'variable':row['variable'],
                #    })
            except KeyError as e:
                print('cannot find: %s' % row['line'])
                cannot_found += 1
                # pass
        print('cannot find: %d' % cannot_found)
   

    def extract_variable(self):
        #file_order = 'allJarFilesInPath'
        #src_path = '%s/%s' % (self.base_dir(), self.src_dict())
        #mode_order = 'variable'
        #middle_path = self.variable_call_without_transfer()
        ##print(middle_path)
        #output_path = self.variable_dir()
        #os.system('java -jar %s %s %s %s %s' % (
        #    jar_path, file_order, src_path, mode_order, middle_path))
        self.extract_info_with_AST_analyzer('variable', 
                self.variable_call_without_transfer(), self.variable_dir())

    def extract_predicate(self):
        self.extract_info_with_AST_analyzer('predicate',
                self.predicate_without_transfer(), self.predicate_dir())

    def extract_key(self):
        self.extract_info_with_AST_analyzer('key',
                self.key_without_transfer(), self.key_dir())

    def extract_info_with_AST_analyzer(self, mode_order, middle_path, output_path):
        jar_path = Version.JAR_PATH
        file_order = 'allJarFilesInPath'
        src_path = '%s/%s' % (self.base_dir(), self.src_dict())
        # mode_order = 'variable'
        # middle_path = self.variable_call_without_transfer()
        #print(middle_path)
        # output_path = self.variable_dir()
        os.system('java -jar %s %s %s %s %s' % (
            jar_path, file_order, src_path, mode_order, middle_path))
 
        
    def src_dict(self):
        if self.project_name == 'Time':
            return 'src/main/java'
        elif self.project_name == 'Lang':
            if self.project_no <= 35:
                return 'src/main/java'
            else:
                return 'src/java'
        elif self.project_name == 'Math':
            if self.project_no <= 84:
                return 'src/main/java'
            else:
                return 'src/java'
        elif self.project_name == 'Closure':
            return 'src'
        elif self.project_name == 'Chart':
            return 'source'
        elif self.project_name == 'Mockito':
            return 'src'

    def get_patch(self):
        f = open('%s/patches/%s.src.patch' % (self.defects4j_dir(), self.project_no))
        last_delete = False
        last_line = ''
        for line in f.readlines():
            line = str(line)
            if line.startswith('+ '):
                return line[2:-1].lstrip()
            elif line.startswith('- '):
                last_delete=True
            elif last_delete:
                if len(line.lstrip()) > 3 and line.lstrip()[:2] != '//':
                    last_line = line[:-1].lstrip()
                    last_delete = False
        return last_line

    def search_patch(self, formula, patch_dict):
        patch_statement = patch_dict[self.project_no]
        csv_reader = csv.reader(open('%s/%s.rank.csv' % (self.result_Delta_4T_dir(), formula)))
        for row in csv_reader:
            statement = row[0]
            # match ok
            # print(patch_statement)
            # print(statement)
            # if re.match(patch_statement, statement) is not None:
            if patch_statement in statement:
                return row
        # if not found
        return None

    def return_inserted_number(self, inserter=sbfl.basic_inserted_spectra, spectra_type=sbfl.InsertZeroSpectra):
        spectra_list = self.return_spectra_add()
        return len(inserter(spectra_list, spectra_type))

    def transfer_ranking_csv(self, formula_name):
        # src_path = '%s/src' % self.base_dir() if os.path.exists('%s/src' % self.base_dir()) else '%s/source' % self.base_dir()
        # src_path = '%s/%s' % (self.base_dir(), src_dict[self.project_name])
        if not self.exist_fl_result(formula_name):
            print('%s for %s does not exist.' % (formula_name, str(self)))
            return

        src_path = '%s/%s' % (self.base_dir(), self.src_dict()) 
        # output_writer = csv.DictWriter(open('%s/%s.statements.ranking.csv' % (self.gzoltar_txt_dir(), formula_name), 'w'), ['statement','key', 'suspiciousness_value'], delimiter=';')
        output_writer = csv.DictWriter(open('%s/%s.statements.ranking.csv' % (self.result_Delta_4T_dir(), formula_name), 'w'), ['statement','suspiciousness_value'], delimiter=';')
        output_writer.writeheader()
        input_reader = csv.DictReader(open('%s/%s.ranking.csv' % (self.gzoltar_txt_dir(), formula_name)), delimiter=';')
        result_dict = {}
        statement_searched = set([])
        statement_twice = False
        # print(input_reader.fieldnames)
        for row in input_reader:
            # print(row['suspiciousness_value'])
            if float(row['suspiciousness_value']) > 0.0 or formula_name == 'wong2':
                linenum = int(row['name'].split(':')[-1])
                lineloc = row['name'].split(':')[0]
                filepath = row['name'].split('#')[0]
                # filepath = re.split('\$|\.', filepath)
                filepath = filepath.split('$')[:2]
                filepath = filepath[0].split('.') + [filepath[1]]
                file_to_open = ''
                for f in filepath:
                    file_to_open += '/%s' % f
                # file_to_open = file_to_open[:-2]
                file_to_open += '.java'
                file_to_open = src_path + file_to_open
                try:
                    statement = lineloc + ':' + linecache.getline(file_to_open, linenum)[:-1]
                except UnicodeDecodeError:
                    print('UnicodeDecodeError')
                    print('%s for %s @ %s ' % (str(self), linenum, file_to_open))
                    continue
                # statement = row['name'] + ':' + linecache.getline(file_to_open, linenum)[:-1]
                # key = ''
                if statement in statement_searched:
                    print('occur before: %s' % statement)
                    # key = row['name']
                    statement_twice = True
                else:
                    statement_searched.add(statement)
                # output_writer.writerow({'statement':statement, 'key':key, 'suspiciousness_value':row['suspiciousness_value']})
                # print('write a row')
                result_dict[statement] = max(float(result_dict.get(statement, 0.0)), float(row['suspiciousness_value']))
        if len(result_dict) == 0:
            print('empty result')
        else:
            # min_value = min([min(result_dict.values()), 0.0])
            min_value = min(result_dict.values())
            max_value = max(result_dict.values())
            if min_value - max_value == 0:
                min_value = 0.0
            # still cannot recognize
            if max_value - min_value == 0:
                min_value = max_value -1
            # normalize
            for key, value in result_dict.items():
                output_writer.writerow({'statement': key, 'suspiciousness_value': (value-min_value) / (max_value-min_value)})
        if statement_twice:
            print('attention: exist statement twice')

    def extract_exclude(self):
        src_path = '%s/%s' % (self.base_dir(), self.src_dict()) 
        # output_writer = csv.DictWriter(open('%s/%s.statements.ranking.csv' % (self.result_Delta_4T_dir(), formula_name), 'w'), ['statement','suspiciousness_value'], delimiter=';')
        # output_writer.writeheader()
        spectra_add = self.return_spectra_add()
        # non_rank_list = [{'name':spectra_add[0].name}]
        non_rank_list = []
        # print(input_reader.fieldnames)
        # first_line = False
        # spectra_last = spectra_add[0]
        for spectra in spectra_add:
            # print(row['suspiciousness_value'])
            #if not spectra_last.same_method(spectra):
            #    spectra_last = spectra
            #    non_rank_list.append({'name': spectra.name})
            #    continue
            linenum = int(spectra.line_no())
            # lineloc = row['name'].split(':')[0]
            filepath = spectra.class_name() 
            # filepath = re.split('\$|\.', filepath)
            filepath = filepath.split('$')[:2]
            filepath = filepath[0].split('.') + [filepath[1]]
            file_to_open = ''
            for f in filepath:
                file_to_open += '/%s' % f
            # file_to_open = file_to_open[:-2]
            file_to_open += '.java'
            file_to_open = src_path + file_to_open
            try:
                statement = linecache.getline(file_to_open, linenum)[:-1]
                if statement.lstrip() == '{' or statement.lstrip() == '}':
                    non_rank_list.append({'name': spectra.name}) 
            except UnicodeDecodeError:
                print('UnicodeDecodeError')
                print('%s for %s @ %s ' % (str(self), linenum, file_to_open))
                continue
        util.write_into_csv(self.exclude_spectra_dir(), 
                non_rank_list, ['name'])
   

    def get_ranking_dict(self, formula_name):
        suspiciousness_dict = {}
        csv_reader = csv.DictReader(open('%s/%s.statements.ranking.csv' % (self.result_Delta_4T_dir(), formula_name)), delimiter=';')
        for row in csv_reader:
            # suspiciousness_dict[row['statement']] = max(float(suspiciousness_dict.get(row['statement'],0)), float(row['suspiciousness_value']))
            suspiciousness_dict[row['statement']] = float(row['suspiciousness_value'])
        return suspiciousness_dict

    def read_method_call(self):
        dict_method_call = {}
        csv_reader = csv.DictReader(open(self.method_call_dir()))
        for row in csv_reader:
            if dict_method_call.get(row['line']) is None:
                dict_method_call[row['line']] = []
            dict_method_call[row['line']].append(row['method_call'])
        return dict_method_call

    def read_block(self):
        block_info_list = []
        csv_reader = csv.DictReader(open(self.ast_block()))
        for row in csv_reader:
            block_info_list.append(row)
        return block_info_list

    def read_variable(self):
        return self.read_variable_from_file(self.variable_dir())

    def read_variable_block(self):
        return self.read_variable_from_file(self.variable_block_dir())

    def read_key(self):
        return self.read_variable_from_file(self.key_dir())

    def read_variable_from_file(self, file_path):
        dict_variable = {}
        csv_reader = csv.DictReader(open(file_path))
        for row in csv_reader:
            dict_variable[row['line']] = row['variable'].split(';')
        return dict_variable

    def read_predicate(self):
        return self.read_variable_from_file(self.predicate_dir())

    def read_info(self, info_type):
        return self.dict_read_source.get(info_type, self.emtpy)(self)

    def emtpy(self):
        return []

    dict_read_source = {
            'method_call': read_method_call,
            'variable': read_variable,
            'variable_block': read_variable_block,
            'predicate': read_predicate,
            'key': read_key,
            'branch': return_branch_info,
            }

class FixedVersion(Version):
    def __init__(self, project_name, project_no):
        Version.__init__(self, project_name, project_no)

    def base_dir(self):
        return '%s/%s_%s_fixed' % (Version.WORKSPACE, self.project_name, self.no())

    def read_trigger_tests(self):
        return []

class Version100(Version):
    def __init__(self, project_name, project_no):
        Version.__init__(self, project_name, project_no)

    def no(self):
        if self.project_no >= 100:
            return str(self.project_no)
        elif self.project_no >= 10:
            return '0%s' % self.project_no
        else:
            return '00%s' % self.project_no

class FixedVersion100(Version100):
    def __init__(self, project_name, project_no):
        Version100.__init__(self, project_name, project_no)

    def base_dir(self):
        return '%s/%s_%s_fixed' % (Version.WORKSPACE, self.project_name, self.no())

    def read_trigger_tests(self):
        return []

class VersionRelevant(Version):
    def __init__(self, project_name, project_no):
        Version.__init__(self, project_name, project_no) 

    def spectra_add_dir(self):
        return '%s/spectra_add_relevant/%s_%s_spectra.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def spectra_dir(self):
        return '%s/spectra_GZoltar_relevant/%s_%s/spectra.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

class SplitVersion(Version):
    def __init__(self, project_name, project_no):
        Version.__init__(self, project_name, project_no)

    def spectra_add_dir(self):
        return '%s/spectra_split/%s_%s_spectra.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

    def spectra_dir(self):
        return '%s/spectra_GZoltar_split/%s_%s/spectra.csv' % (
                Version.MISSING_BRANCH_PATH, self.name(), self.no())

def create_version(name, no, fixed=False, relevant=False, split=False):
    # now there are only 'Time' with relevant experiments.
    if relevant:
        return VersionRelevant(name, no)
    if split:
        return SplitVersion(name, no)
    if name == 'Closure' or name == 'Math':
        return FixedVersion100(name, no) if fixed else Version100(name, no)
    else:
        return FixedVersion(name, no) if fixed else Version(name, no)

class Experiment:
    def __init__(self, no):
        self.no = no

    def base_dir(self):
        return '%s/history_result/%s/' % (Version.MISSING_BRANCH_PATH, self.no)

    def __str__(self):
        return 'experiment %s' % self.no

    def return_analyze(self, formula): 
        path = '%s/experiment_%s_%s_analyze.csv' % (
                self.base_dir(), self.no, formula)
        return self.read_csv(path)

    def read_csv(self, path):
        reader = csv.DictReader(open(path))
        result = []
        for row in reader:
            result.append(row)
        return result

    def return_fault(self, formula):
        path = '%s/experiment_%s_%s_fault.csv' % (
                self.base_dir(), self.no, formula)
        return self.read_csv(path)
 
def return_spectra_num_dict():
    dict_number = {}
    for project in max_no.keys():
        for no in range(1, max_no[project] + 1):
            version = create_version(project, no)
            print(version)
            #dict_number[str(version)] = version.return_inserted_number()
            dict_number['%s@%s' % (project, no)] = version.return_inserted_number()
    return dict_number

def return_raw_num_dict():
    dict_number = {}
    for project in max_no.keys():
        for no in range(1, max_no[project] + 1):
            version = create_version(project, no)
            print(version)
            #dict_number[str(version)] = version.return_inserted_number()
            dict_number['%s@%s' % (project, no)] = version.return_raw_number()
    return dict_number

def prepare_num_dict(number_type, file_name):
    dict_number = {}
    for project in max_no.keys():
        for no in range(1, max_no[project] + 1):
            version = create_version(project, no)
            print(version)
            #dict_number[str(version)] = version.return_inserted_number()
            dict_number['%s@%s' % (project, no)] = version.return_number(number_type)
    output_writer = csv.DictWriter(open('%s/info/%s' % (Version.MISSING_BRANCH_PATH, file_name), 'w'), ['version','number'], delimiter=';')
    output_writer.writeheader()
    for key, value in dict_number.items():
        output_writer.writerow({'version': key, 'number': value}) 

def prepare_raw_num_dict():
    prepare_num_dict('raw', 'raw_spectra_number.csv')

def prepare_inserted_num_dict():
    prepare_num_dict('inserted', 'inserted_spectra_number.csv')

def prepare_raw_exclude_dict():
    prepare_num_dict('raw_exclude', 'raw_exclude_spectra_number.csv')

def prepare_inserted_exclude_dict():
    prepare_num_dict('inserted_exclude', 'inserted_exclude_spectra_number.csv')

#def prepare_raw_num_dict():
#    dict_number = return_raw_num_dict()
#    output_writer = csv.DictWriter(open('%s/info/raw_spectra_number.csv' % Version.MISSING_BRANCH_PATH, 'w'), ['version','number'], delimiter=';')
#    output_writer.writeheader()
#    for key, value in dict_number.items():
#        output_writer.writerow({'version': key, 'number': value})

def prepare_spectra_num_dict():
    dict_number = return_spectra_num_dict()
    output_writer = csv.DictWriter(open('%s/info/inserted_spectra_number.csv' % Version.MISSING_BRANCH_PATH, 'w'), ['version','number'], delimiter=';')
    output_writer.writeheader()
    for key, value in dict_number.items():
        output_writer.writerow({'version': key, 'number': value})

def read_spectra_num_dict(name):
    dict_number = {}
    input_reader = csv.DictReader(open('%s/info/%s.csv' % (Version.MISSING_BRANCH_PATH, name) ), delimiter=';')
    for row in input_reader:
        dict_number[row['version']] = float(row['number'])
    return dict_number

dict_spectra_number = {
        'inserted': read_spectra_num_dict('inserted_spectra_number'),
        'raw': read_spectra_num_dict('raw_spectra_number'),
        'raw_exclude': read_spectra_num_dict('raw_exclude_spectra_number'),
        'inserted_exclude': read_spectra_num_dict('inserted_exclude_spectra_number'),
        }
        
if __name__ == '__main__':
    #version = Version('Lang', 1)
    #l = version.return_spectra()
    #print(len(l))
    #print(l[list(l.keys())[0]])
    #print(l[list(l.keys())[1]])
    #print(l[list(l.keys())[2]])
    #print(l[1])
    # print(dict_spectra_number['raw'])
    # prepare_inserted_num_dict()
    prepare_raw_exclude_dict()
    # prepare_inserted_exclude_dict()
