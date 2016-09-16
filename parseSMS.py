#!/usr/bin/python
import re

#txt='SMS:1101,R1 SMS:1101,R1154063|005  1317161323.4 6 -290 298 -446.3 3.6 3.853e+01 1.292e+04 6.535e+03 0.00'
def parseSMS(txt):
    re1='(SMS)'# Word 1
    re2='(:)'# Any Single Character 1
    re3='(\\d+)'# Integer Number 1
    re4='(,)'# Any Single Character 2
    re5='(R)'# Any Single Character 3
    re6='(\\d+)'# Integer Number 2
    re7='(\\s+)'# White Space 1
    re8='(SMS)'# Word 2
    re9='(:)'# Any Single Character 4
    re10='(\\d+)'# Integer Number 3
    re11='(,)'# Any Single Character 5
    re12='(R)'# Any Single Character 6
    re13='(\\d+)'# Integer Number 4
    re14='(\\|)'# Any Single Character 7
    re15='(\\d+)'# Integer Number 5
    re16='(\\s+)'# White Space 2
    re17='((.*)$)'# Variable Name 1
    
#re17='($)'# rest
    rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12+re13+re14+re15+re16+re17,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)

    if m:
        word1=m.group(1)
        c1=m.group(2)
        int1=m.group(3)
        c2=m.group(4)
        c3=m.group(5)
        int2=m.group(6)
        ws1=m.group(7)
        word2=m.group(8)
        c4=m.group(9)
        int3=m.group(10)
        c5=m.group(11)
        c6=m.group(12)
        int4=m.group(13)
        c7=m.group(14)
        queue=m.group(15)
        ws2=m.group(16)
        rest=m.group(17)
    #print "("+word1+")"+"("+c1+")"+"("+int1+")"+"("+c2+")"+"("+c3+")"+"("+int2+")"+"("+ws1+")"+"("+word2+")"+"("+c4+")"+"("+int3+")"+"("+c5+")"+"("+c6+")"+"("+int4+")"+"("+c7+")"+"("+int5+")"+"("+ws2+")"+"("+rest+")"+"\n"
        return rest,queue
    else:
        return None,None

