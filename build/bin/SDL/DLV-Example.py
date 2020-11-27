import subprocess

string="./dlv2 threecolorability"
result=subprocess.getoutput(string)
l=result.split(', ')
l[0]=l[0].replace('DLV 2.0\n\n{', '')
print(l)