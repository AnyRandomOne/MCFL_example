from task import *

if __name__ == '__main__':
    # solve_projects(['Lang', 'Closure', 'Math', 'Chart', 'Time', 'Mockito'])
    #modify_spectra('Lang',42, split=True)
    #modify_spectra('Lang', 43, split=True)
    run_experiment({
        'experiment_no': '0.0_compare',
        'method': 'insert',
        'project': ['Math'],
        'no': [1],
        'analyze': ['EXAM'],
        'rank': 'exclude',
        'collector': 'coverage_to_insert',
        'solver_list': [{'mode': 'compare',},
           ],
        'formulas': ['ochiai', 'barinel2', 'jaccard', 'dstar',],
        })

