import re 

class Spectra:
    def __init__(self, name, suspicious_value=0.0):
        self.name = name
        self.suspicious_value = suspicious_value

    def method_name(self):
        return ''
     
    def same_method(self, other):
        return self.method_name() == other.method_name()
        #method_name = self.name.split(':')[0]
        #other_name = other.name.split(':')[0]
        #if method_name == other_name:
        #    return True
        #else:
        #    return False
 
    def calculate_suspicious_value(self, calculator):
        pass
        #return calculate_value(formula, self.hit_pass, self.hit_fail, self.miss_pass, self.miss_fail)

    def set_suspicious_value(self, value):
        self.suspicious_value = value

    def get_suspicious_value(self):
        return self.suspicious_value

    def __str__(self):
        return '%s:%s' % (self.name, self.suspicious_value)

    def class_name(self):
        return ''

    def line_no(self):
        return -1

    def name_without_lineno(self):
        pass

    def __lt__(self, other):
        return self.suspicious_value < other.suspicious_value

    def to_dict(self):
        return {'name': self.name, 
                'suspicious_value': self.suspicious_value}

    def is_insert(self):
        return False

    def same_class(self, other):
        return self.class_name() == other.class_name()

class GZoltarSpectra(Spectra):
    def __init__(self, name, hit_pass, hit_fail, miss_pass, miss_fail, suspicious_value=0.0):
        Spectra.__init__(self, name, suspicious_value)
        self.hit_pass = float(hit_pass)
        self.hit_fail = float(hit_fail)
        self.miss_pass = float(miss_pass)
        self.miss_fail = float(miss_fail)

    def file_name_old(self):
        # return (self.name.split('$')[1]).split('#')[0]
        return ".".join([self.name.split('$')[0],
            (self.name.split('$')[1]).split('#')[0]])

    def file_name(self):
        # return (self.name.split('$')[1]).split('#')[0]
        return "$".join([self.name.split('$')[0],
            (self.name.split('$')[1]).split('#')[0]])

    def simplify_name(self):
        return '%s:%s' % (self.file_name(), self.line_no())

    def class_name(self):
        return self.name.split('#')[0]

    def method_name(self):
        return self.name.split(':')[0]

    def line_no(self):
        return self.name.split(':')[-1]

    def name_without_lineno(self):
        return ":".join(self.name.split(':')[:-1])
    
    def calculate_suspicious_value(self, calculator):
        self.suspicious_value = calculator.cal_gzoltar(self)
        # print(self.suspicious_value)

    def copy_spectra(self, new_line_no):
        new_name = '%s:%d' % (self.name_without_lineno(), new_line_no)
        return GZoltarSpectra(new_name, self.hit_pass, self.hit_fail, self.miss_pass, self.miss_fail, self.suspicious_value)

    def is_insert(self):
        return False

    def __str__(self):
        return Spectra.__str__(self) 

class GZoltarBranchSpectra(GZoltarSpectra):
    def __init__(self, name, hit_pass, hit_fail, miss_pass, miss_fail, location, boolean, suspicious_value=0.0):
        GZoltarSpectra.__init__(self, name, hit_pass, hit_fail, miss_pass, miss_fail, suspicious_value)
        self.location = location
        self.boolean = boolean

def integrate_location(before, after):
    return "->".join([before, after])

def insert_spectra(spectra_list):
    if len(spectra_list) == 0:
        return []
    result_list = []
    spectra_last = spectra_list[0]
    for i in range(1, len(spectra_list)):
        # print(spectra_list[i].method_name())
        if spectra_list[i].same_method(spectra_last):
            # print('same spectra')
            result_list.append(InsertSpectra(spectra_last, spectra_list[i]))
        spectra_last = spectra_list[i]
    print('add: %s' % len(result_list))
    return result_list

def basic_inserted_spectra(spectra_list, spectra_type):
    if len(spectra_list) == 0:
        return []
    result_list = [spectra_list[0]]
    for i in range(1, len(spectra_list)):
        if spectra_list[i].same_method(result_list[-1]):
            result_list.append(spectra_type(result_list[-1], spectra_list[i]))
        result_list.append(spectra_list[i])
    print('after add: %s' % len(result_list))
    return result_list

#def return_inserted_spectra_number(version, inserter=basic_inserted_spectra, spectra_type=InsertZeroSpectra):
#    spectra_list = version.return_spectra_add()
#    return len( inserter( spectra_list, spectra_type))

class InsertSpectra(Spectra):
    """The first version of insert spectra experiment, which use a different formula of calculating suspicious value
    Attention: there are not hit_pass or other values for this version!
    """
    def __init__(self, spectra_before, spectra_after, suspicious_value=0.0):
        # Spectra.__init__(self, "->".join([spectra_before.name, spectra_after.name], suspicious_value)
        Spectra.__init__(self, integrate_location(spectra_before.name, spectra_after.name), suspicious_value)
        self.spectra_before = spectra_before
        self.spectra_after = spectra_after

    def class_name(self):
        return self.spectra_before.class_name()

    def line_no(self):
        return self.spectra_before.line_no()

    def name_without_lineno(self):
        return self.spectra_before.name_without_lineno()

    def calculate_suspicious_value(self, calculator):
        self.suspicious_value = calculator.cal_insert(self) 

    def method_name(self):
        return self.spectra_before.method_name()

    def is_insert(self):
        return True

class InsertSBFLSpectra(InsertSpectra):
    """In this version, there are hit_pass, hit_fail, miss_pass, miss_fail
    A bi-inherit in C++ is better.
    """
    def __init__(self, spectra_before, spectra_after, hit_pass=0.0, hit_fail=0.0, miss_pass=0.0, miss_fail=0.0, suspicious_value=0.0):
        InsertSpectra.__init__(self, spectra_before, spectra_after, suspicious_value)
        self.hit_pass =   hit_pass 
        self.hit_fail =   hit_fail 
        self.miss_pass =  miss_pass
        self.miss_fail =  miss_fail

class InsertAfterSpectra(InsertSBFLSpectra):
    """In this version, the hit_pass ... and all other SBFL info are 0.0
    """
    def __init__(self, spectra_before, spectra_after, suspicious_value=0.0):
        # values are all 0.0, as default values.
        InsertSBFLSpectra.__init__(self, spectra_before, spectra_after, 
                hit_pass=spectra_after.hit_pass,
                hit_fail=spectra_after.hit_fail,
                miss_pass=spectra_after.miss_pass,
                miss_fail=spectra_after.miss_fail)

class InsertZeroSpectra(InsertSBFLSpectra):
    """In this version, the hit_pass ... and all other SBFL info are 0.0
    """
    def __init__(self, spectra_before, spectra_after, suspicious_value=0.0):
        # values are all 0.0, as default values.
        InsertSBFLSpectra.__init__(self, spectra_before, spectra_after)

dict_spectra_type = {
        'zero': InsertZeroSpectra,
        'after': InsertAfterSpectra,
        }

#class AddSpectra(Spectra):
#    def __init__(self, name, hit_pass, hit_fail, miss_pass, miss_fail, file_name_in, line_no_in, last_spectra, next_spectra=None):
#        Spectra.__init__(self, name, hit_pass, hit_fail, miss_pass, miss_fail, last_spectra, next_spectra)
#        self.file_name_ = file_name_in
#        self.line_no_ = line_no_in
#
#    def class_name(self):
#        return self.file_name_
#
#    def line_no(self):
#        return self.line_no_


class SpectraMatrix:
    def __init__(self, spectra_dict):
        self.spectra_matrix = {}
        for value in spectra_dict.values():
            self.insert_spectra(value)
        #for name in self.spectra_matrix.keys():
        #    print(name)
            #name = value.class_name() 
            #line = value.line_no() 
            #if self.spectra_matrix.get(name, None) is None:
            #    self.spectra_matrix[name] = {}
            #self.spectra_matrix[name][line] = value

    def insert_spectra(self, new_spectra):
        # name = new_spectra.class_name()
        name = new_spectra.file_name_old()
        # print('name: %s' % name)
        line = int(new_spectra.line_no())
        if self.spectra_matrix.get(name, None) is None:
            self.spectra_matrix[name] = {}
        self.spectra_matrix[name][line] = new_spectra

    # if does not exist, return None
    def find_spectra(self, name, line):
        if self.spectra_matrix.get(name, None) is None:
            return None
        found = self.spectra_matrix[name].get(line, None)
        return found

    def find_next(self, name, line):
        if self.spectra_matrix.get(name, None) is None:
            # print('no such class: ' + name)
            return None
        # print(list(self.spectra_matrix[name].keys()))
        max_line = max(list(self.spectra_matrix[name].keys()))
        # print('max_line %d' % max_line)
        for x in range(line+1, max_line+1):
            # print('check line %s' % x)
            found = self.spectra_matrix[name].get(x, None)
            if found is not None:
                return found
        return None

    def find_last(self, name, line):
        if self.spectra_matrix.get(name, None) is None:
            return None
        min_line = min(list(self.spectra_matrix[name].keys()))
        for x in range(line-1, min_line-1, -1):
            found = self.spectra_matrix[name].get(x, None)
            if found is not None:
                return found
        return None

    def spectra_exist(self, name, line):
        if self.spectra_matrix.get(name, None) is None:
            return False
        if self.spectra_matrix[name].get(line, None) is None:
            return False
        return True

    def get_spectra(self, name, line):
        if self.spectra_matrix.get(name, None) is None:
            return None
        return self.spectra_matrix[name].get(line, None)

    def get_method_spectra(self):
        method_dict = {}
        for name in self.spectra_matrix.keys():
            for spectra_now in self.spectra_matrix[name].values():
                if spectra_now.is_insert():
                    continue
                if method_dict.get(spectra_now.method_name(), None) is None:
                    method_dict[spectra_now.method_name()] = spectra_now
                elif int(method_dict[spectra_now.method_name()].line_no()) < int(spectra_now.line_no()):
                    method_dict[spectra_now.method_name()] = spectra_now
        return method_dict

    def list_for_csv_writer(self):
        result_list = []
        for name in self.spectra_matrix.keys():
            # we sort the dict to make sure that the output is easy to understand and debug. I decide not to change the original matrix, for there should be only one output.
            spectra_dict = self.spectra_matrix[name]
            # new_dict = {}
            line_no_list = list(spectra_dict.keys())
            line_no_list.sort()
            for no in line_no_list:
                # new_dict[no] = spectra_dict[no]
                spectra_now = spectra_dict[no]
                result_list.append({
                    'name': spectra_now.name,
                    'hit_pass': int(spectra_now.hit_pass),
                    'hit_fail': int(spectra_now.hit_fail),
                    'miss_pass': int(spectra_now.miss_pass),
                    'miss_fail': int(spectra_now.miss_fail),
                    })
        return result_list

# I decide to try all with one method first.
# If cannot work well, then try to substitute with other way
'''
ast_info_dict = {
        'method': MethodInfo,
        'if': IfInfo,
        'for': ForInfo,
        'forEach': ForEachInfo,
        'while': WhileInfo,
        'switchEntry': SwitchEntryInfo,
        'switch': SwitchInfo,
        'try': TryInfo,
        'catchClause': CatchClauseInfo,
        'else': ElseInfo,
}
'''

nearest_info = ['method']

def create_ast(info_type, info_file, start, end):
    # return ast_info_dict[info_type](info_file, start, end)
    # return NearestInfo(info_file, start, end) 
    if info_type in nearest_info:
        return NearestInfo(info_file, start, end, info_type)
    else:
        return BlockInfo(info_file, start, end, info_type)

class AstInfo:
    def __init__(self, info_file, start, end, info_type): 
        self.read_file(info_file)
        # print(self.info_file)
        self.start = int(start)
        self.end = int(end)
        self.info_type = info_type

    def read_file(self, file_path):
        # self.info_file = file_path.split('/')[-1].split('.')[0]
        # self.info_file = 
        for src_path in ['src/main/java/', 'src/java/', 'src/', 'source/']:
            range_find = re.search(src_path, file_path)
            if range_find is not None:
                path_need = file_path[range_find.span()[1]:].split('.')[0]
                self.info_file = '.'.join(path_need.split('/'))
                return
        # in this situation, there is no valid one
        self.info_file = ''

    def ast_type(self):
        return 'abstract'

    def __str__(self):
        return '%s in %s at (%d -> %d)' % (self.ast_type(), self.info_file, self.start, self.end)

    def insert_statement(self, spectra_matrix):
        pass

    def insert_start(self, spectra_matrix):
        pass

    def insert_end(self, spectra_matrix):
        pass

    def is_block(self):
        return False

    def find_spectra_name(self, spectra_matrix):
        spectra_start, spectra_end = self.find_spectra(spectra_matrix)
        if spectra_start is None or spectra_end is None:
            return None
        else:
            return {'start': spectra_start.name, 'end': spectra_end.name}

    def find_spectra(self, spectra_matrix):
        spectra_start = spectra_matrix.find_spectra(self.info_file, self.start)
        spectra_end = spectra_matrix.find_spectra(self.info_file, self.end)
        return spectra_start, spectra_end

    def find_next(self, spectra_matrix):
        return spectra_matrix.find_next(self.info_file, self.start)


class NearestInfo(AstInfo):
    def __init__(self, info_file, start, end, info_type):
        AstInfo.__init__(self, info_file, start, end, info_type)

    def ast_type(self):
        return 'nearest'

    def insert_statement(self, spectra_matrix):
        # print(str(self))
        self.insert_start(spectra_matrix)
        self.insert_end(spectra_matrix)

    # use the GZoltarSpectra only.
    def insert_start(self, spectra_matrix):
        # if exist, then no use to insert
        # print('insert start')
        if spectra_matrix.spectra_exist(self.info_file, self.start):
            # pass
            return
        spectra_next = spectra_matrix.find_next(self.info_file, self.start) 
        if spectra_next is None:
            # print('no spectra next')
            return
        # print('new spectra')
        new_spectra = spectra_next.copy_spectra(self.start)
        # print('insert new at start: %s' % new_spectra)
        spectra_matrix.insert_spectra(new_spectra)
        #if spectra_next.last_spectra is not None:
        #    spectra_next.last_spectra.set_next(new_spectra)
        #new_spectra.set_next(spectra_next)

    def insert_end(self, spectra_matrix):
        # if exist, then no use to insert
        if spectra_matrix.spectra_exist(self.info_file, self.end):
            # pass
            return
        spectra_last = spectra_matrix.find_last(self.info_file, self.end)
        if spectra_last is None:
            return
        new_spectra = spectra_last.copy_spectra(self.end)
        spectra_matrix.insert_spectra(new_spectra)
        #if spectra_last.next_spectra is not None:
        #    spectra_last.next_spectra.set_last(new_spectra)
        #new_spectra.set_last(spectra_last)

    #def is_block(self):
    #    return False

class BlockInfo(NearestInfo):
    def __init__(self, info_file, start, end, info_type):
        NearestInfo.__init__(self, info_file, start, end, info_type)

    def insert_end(self, spectra_matrix):
        if spectra_matrix.spectra_exist(self.info_file, self.end):
            return
        spectra_to_copy = None
        if spectra_matrix.spectra_exist(self.info_file, self.start):
            spectra_to_copy = spectra_matrix.get_spectra(self.info_file, self.start)
        else:
            spectra_to_copy = spectra_matrix.find_next(self.info_file, self.start) 
        if spectra_to_copy is None:
            return
        new_spectra = spectra_to_copy.copy_spectra(self.end)
        # print('insert new at end of block %s' % new_spectra)
        spectra_matrix.insert_spectra(new_spectra)

    def is_block(self):
        return True

def get_method_spectra(spectra_list):
    method_dict = {}
    for spectra_now in spectra_list: 
        if spectra_now.is_insert():
            continue
        if method_dict.get(spectra_now.method_name(), None) is None:
            method_dict[spectra_now.method_name()] = spectra_now
        elif int(method_dict[spectra_now.method_name()].line_no()) > int(spectra_now.line_no()):
            method_dict[spectra_now.method_name()] = spectra_now
    return method_dict

def transform_spectra_from_asm(origin_spectra):
    token_list = origin_spectra.split(":")
    if len(token_list) != 2:
        print("error: %d ->  %s" % (len(token_list), origin_spectra))
        return origin_spectra
    method_name = token_list[0]
    line_no = token_list[1]
    return "%s:%s" % (transform_method_from_asm(method_name), line_no)

dict_token_asm = {
        'I': 'int',
        'Z': 'boolean',
        'C': 'char',
        'S': 'short',
        'B': 'byte',
        'J': 'long',
        'F': 'float',
        'D': 'double',
}

def transform_method_from_asm(origin_method):
    # return origin_method
    try:
        method_name = origin_method.split('(')[0]
        word_list = method_name.split('.')
        direct_name = word_list[-1].split('#')[1]
        if direct_name == "<init>":
            if word_list[-1].split('#')[0].split('$')[-1] == "1":
                word_list[-1] = '$'.join(word_list[-1].split('#')[0].split('$')[:-1])+"#<clinit>"
            else:
                word_list[-1] = word_list[-1].split('#')[0] + "#<clinit>"
        method_name = "%s$%s" % (
                '.'.join(word_list[:-1]), word_list[-1])
        parameter = origin_method.split('(')[1].split(')')[0]
        # print(parameter)
        loc_now, parameter_list, if_list = 0, [], False
        while loc_now != len(parameter):
            result_now = ''
            if parameter[loc_now] == 'L':
                start = loc_now
                while parameter[loc_now] != ';':
                    loc_now += 1
                result_now = parameter[start+1:loc_now].replace('/', '.')
            elif parameter[loc_now] == '[':
                if_list = True
            else:
                result_now =  dict_token_asm[parameter[loc_now]]
            if len(result_now) != 0:
                if if_list:
                    result_now = '%s[]' % result_now
                    if_list = False
                parameter_list.append(result_now)
            loc_now += 1
        parameter = ','.join(parameter_list)
            
        return "%s(%s)" % (method_name, parameter)
    except Exception as e:
        print('error: %s' % e)
        return origin_method
            
    
