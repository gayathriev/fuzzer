'''

Simple module generates summary after crash is found

'''

def prepare_summary_success(aborts, hangs, iters, time):
    print('------------------- Found bad input ---------------------')
    print('No. of Iterations: ', iters)
    print('No. of Hangs: ', hangs)
    print('No. of Aborts: ', aborts)
    print('Code Coverage: not calculated')
    print('Time Elasped: ', time, " seconds")
    print("=========================================================")
    print("Register Values at Crash: ")


def prepare_summary_fail(aborts, hangs, iters, time):
    print('------------------- No crash produced :( -----------------')
    print('No. of Iterations: ', iters)
    print('No. of Hangs: ', hangs)
    print('No. of Aborts: ', aborts)
    print('Code Coverage: not calculated')
    print('Time Elasped: ', time, "seconds")
