## ExperiMental

To run pip needs to be installed, which is a python package manager. Then, depending on your Operating System, run the following:

1. Enter the base directory


2. Install dependencies(already downloaded within the project, just need to be installed).

Linux: pip install --no-index --find-links dependencies-LINUX/ -r requirements-linux.txt 



Windows: pip install --no-index --find-links dependencies-WINDOWS/ -r requirements-windows.txt 


# Note:

In case of any errors while installing, there is a requirements.txt file that you can use to download and install the packages from online:

pip install -requirements.txt

This should work OS-independent, however, if you still face dependency issues or incorrect version issues, you will be told what dependencies are needed to be installed by continuing
with the following commnd below.

3. Run the server:

python ./musicalpairs/manage.py runserver
