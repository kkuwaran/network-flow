# network-flow
Algorithm development for network flow traceback (i.e., sort out the orders from network flow results)

List of files:
- "NetworkFlowProblem-Data_modified.xlsx": xlsx file containing 6 dataset of the flows
- "NetworkFlowProblem-Output.xlsx": xlsx file containing the results (from 6 dataset in NetworkFlowProblem-Data_modified.xlsx) after executing the network flow traceback algorithm
- "flowtb_main.py": python file for input configuration
- "flowtb_algorithm.py": python file containing the network flow tracback algorithm

### Note
**Problem:** The data in the "Input6" sheet of the original file "NetworkFlowProblem-Data.xlsx" is not consistent with the expected output given in the "Output6" sheet.
Thus, we construct a new file "NetworkFlowProblem-Data_modified.xlsx" which slightly differs from the original dataset file in that the data in the "Input6" sheet is slightly modified so that the data agrees with the desired result. 

List of modification to the "Input6" sheet:
- Cell 'D2':: Original: AUSTRIA; Modified: HUNGARY
- Cell 'C12':: Original: HUNGARY; Modified: (blank)
- Cell 'D12':: Original: AUSTRIA; Modified: HUNGARY
- Cell 'E12':: Original: Conditioning; Modified: Sourcing
- Cell 'F12':: Original: 10; Modified: 1
- Cell 'C18':: Original: HUNGARY; Modified: AUSTRIA

Even though Row 10 and Row 53 of the "Input6" sheet should not appear (for consistency with the "Output6" sheet), we do not need to delete these rows from the excel sheet since the algorithm will detect these inconsistencies and automatically ignore these information. 

### Instruction
To run the network flow traceback alogrithm,
1. Open the file "flowtb_main.py"
2. Set 'filename_input' to be the dataset file name (note: in this case we use "NetworkFlowProblem-Data_modified.xlsx")
3. Set 'filename_output' to be the desired output file name (note: in this case we use "NetworkFlowProblem-Output.xlsx")
4. Set 'number' to be the number 'X' appearing in the sheet name "InputX" of 'filename_input' (In other words, if you want to traceback the data in the "Input3" sheet, simply put '3' as the value of the variable 'number'. In this case we can choose the number between 1 to 6)
5. Set 'debugging' to False so that the algorithm does not print unnecessary information
6. Run the script file

Note: The result in the "OutputX" sheet of 'filename_output' corresponds to the data given in the "InputX" sheet of 'filename_input' where "X" can be the number between 1 to 6. 
