from task import *

if __name__ == '__main__':
    # solve_projects(['Lang', 'Closure', 'Math', 'Chart', 'Time', 'Mockito'])
    #modify_spectra('Lang',42, split=True)
    #modify_spectra('Lang', 43, split=True)
    run_experiment({
        'experiment_no': '0.1_experiment',
        'method': 'insert',
        'project': ['Math'],
        'no': [1],
        'analyze': ['EXAM'],
        'rank': 'exclude',
        'collector': 'coverage_to_insert',
        'solver_list': [{'mode': 'branch_cond',},
            {'mode': 'conv_square',
            'conv': [0.65, 1.0, 0.35],
            'loc': 1,},
            {'mode':'key_diff',
            'ratio': 0.1,
            'base_number': 4.0,
            'full_number': 4.0,
            'base_change': 3.0,
            'full_change': 3.0,
            }],
        'formulas': ['ochiai', 'barinel2', 'jaccard', 'dstar',],
        })

