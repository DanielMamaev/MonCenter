import os


rtklib_v = "RTKLIB-2.4.3-b33"
ver = "v2.4.3-b33"

os.system("sudo apt install python3-pip -y")
os.system("sudo apt install python3-pyqt5 -y")
os.system("sudo apt install xterm -y")
os.system("sudo apt install gfortran -y")
os.system("sudo apt-get install sqlitebrowser -y")
os.system("sudo apt install unzip -y")
os.system("pip3 install pyserial")
os.system("pip3 install yadisk")
os.system("pip3 install --upgrade google-api-python-client")
os.system("pip3 install ftputil")
os.system("pip3 install psutil")
os.system('pip3 install folium')
os.system('pip3 install PyQtWebEngine')
if not os.path.exists(os.getcwd() + "/" + ver + ".zip") and not os.path.exists(os.getcwd() + "/" + rtklib_v):
    os.system("wget https://github.com/tomojitakasu/RTKLIB/archive/refs/tags/" + ver +".zip")
    os.system("unzip "+ ver +".zip")
os.system("cd " + rtklib_v + "/lib/iers/gcc; make")
os.system("cd " + rtklib_v + "/app/convbin/gcc; make")
os.system("cd " + rtklib_v + "/app/rnx2rtkp/gcc; make")
os.system("cd " + rtklib_v + "/app/str2str/gcc; make")
os.system("cp '" + os.getcwd() + "/" + rtklib_v + "/app/str2str/gcc/str2str " + os.getcwd() + "/" + rtklib_v + "/app/str2str/gcc/str2str_auto'")

print("\nDONE!")
