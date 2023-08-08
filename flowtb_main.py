from flowtb_algorithm import flow_traceback

# configuration
filename_input = "NetworkFlowProblem-Data_modified.xlsx"  # name of file containing data
filename_output = "NetworkFlowProblem-Output.xlsx"  # name of output file
number = 1  # data number; choose number within 1-6
debugging = False  # toggle debugging mode

# call flow traceback algorithm
flow_traceback(filename_input, filename_output, number, debugging)