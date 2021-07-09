import os

rtklib_v = "RTKLIB_2.4.3_b33"
ver = "v2.4.3-b33"
os.system("sudo apt install python3-pip -y")
os.system("sudo apt install python3-pyqt5 -y")
os.system("sudo apt install xterm -y")
os.system("sudo apt install gfortran -y")
os.system("pip3 install pyserial")
os.system("pip3 install yadisk")
os.system("pip3 install --upgrade google-api-python-client")
os.system("pip3 install ftputil")
os.system("pip3 install psutil")
os.system("sudo apt install unzip -y")
if not os.path.exists(os.getcwd() + "/" + rtklib_v + ".zip") and not os.path.exists(os.getcwd() + "/" + rtklib_v):
    os.system("wget https://github.com/tomojitakasu/RTKLIB/releases/download/" + ver + "/" + rtklib_v +".zip")
    os.system("unzip RTKLIB_2.4.3_b33")
    os.system("cd RTKLIB_2.4.3_b33/lib/iers/gcc; make")
    os.system("cd RTKLIB_2.4.3_b33/app/convbin/gcc; make")
    os.system("cd RTKLIB_2.4.3_b33/app/rnx2rtkp/gcc; make")
    os.system("cd RTKLIB_2.4.3_b33/app/str2str/gcc; make")
