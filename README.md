# Distributed-computation
 Install a MPI application for your operating system.
 - for Ubuntu: conda install -c conda-forge mpi
Install mpi4py; mpi4py is a Python module that allows you to interact with your MPI, allowing any Python program to exploit multiple processors.
 - conda install -c conda-forge mpi4py
- MPI.COMM_WORLD to get information about all the processors available to run your script, gives access to the number of processes (ranks/processors) available to distribute work across, and information about each processor. 
- Size gives the total number of ranks, or processors, allocated to run our script. 
- rank gives the identifier of the processor currently executing the code.
- - To run: mpirun -n 11 python sample1.py
-  
Tools:
- Python 
- MPI
