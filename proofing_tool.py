#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime
import shutil
from hashlib import new
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from pickle import FALSE, NONE, TRUE
from readline import set_history_length
import sys
import os
import glob
import re

# In[ ]:


#################################################
#                                               #
#  class   ：MyHTMLParser                       #
#                                               #
#  st_tag   : start tag                         #
#  st_style :                                   #
#  end_tag  : end tag                           #
#  html_data: data                              #
#                                               #
#################################################
class MyHTMLParser(HTMLParser):
    st_tag = []
    end_tag = []
    st_style = []
    html_data = []
    comment_data = []

    def handle_starttag(self, tag, attrs):
        self.st_tag.append(tag)
        self.st_style.append(attrs)

    def handle_endtag(self, tag):
        self.end_tag.append(tag)

    def handle_data(self, data):
        if data != NONE:
            self.html_data.append(data.strip())


# In[ ]:


########################################################################################################################
#                                                                                                                       #
#  Function ：typeCheck                                                                                                #
#                                                                                                                       #
#  引数： 1 parser.st_tag                                                                                                #
#        2 parser.end_tag                                                                                               #
#                                                                                                                       #
#  戻り値： 0  <p>, <span>以外                             : lineを書き込み                                                 #
#          1  <p> tmpなし, blank_data, </p> tmpなし       : 繋げず書き込み                                                  #
#          2  <p> tmpあり, <span> tmpあり, </p>, </span>  : stock_dataに追加 and stock_for_blank,stock_for_ptagに書き込み   #
#          3  tmpあり、dataあり                            : dataの長さを確認、stock_dataに追加  短ければstock_dataを書き込み   #
#          4  </p> tmpあり, </br>                         : 書き込まずにcontenue                                           #
##########################################################################################################################

def typeCheck(st_tag, end_tag, html_data, stock_data):
    st_p_flg = 0
    st_br_count = 0
    end_p_flg = 0
    st_span_flg = 0
    end_span_flg = 0
    stock_data_check = 0

    if st_tag == 'p':
        st_p_flg = 1
    elif st_tag == 'span':
        st_span_flg = 1
    elif st_tag == 'br':
        st_br_count = 1

    if end_tag == 'p':
        end_p_flg = 1
    elif end_tag == 'span':
        end_span_flg = 1

    if len(html_data) > 0:
        for data in html_data:
            if data == "blank_data":
                stock_data_check = 1
                break
            elif len(data) > 1 and len(stock_data) > 1:
                stock_data_check = 2
                break
            elif len(data) > 1:
                stock_data_check = 4
    elif len(stock_data) > 0:
        stock_data_check = 3

    if stock_data_check == 3 and end_p_flg == 1:
        return 4
    elif st_br_count == 1:
        return 4
    elif stock_data_check == 4:
        return 5
    elif stock_data_check == 2:
        return 3
    elif st_p_flg == 1 and stock_data_check == 3:
        return 2
    elif st_span_flg == 1 and stock_data_check == 3:
        return 2
    elif end_p_flg == 1 or end_span_flg == 1:
        return 2
    elif st_p_flg == 1 and stock_data_check == 0:
        return 1
    elif stock_data_check == 1:
        return 1
    elif end_p_flg == 1 and stock_data_check == 0:
        return 1
    else:
        return 0


# In[ ]:


#################################################
#                                               #
#  Function ：writeData                        #
#                                               #
#  引数： 1 string (target file name)            #
#        2 string (to write sentence)           #
#                                               #
#################################################

# ファイルに書き込み
def writeData(file_name, str):
    with open(file_name, 'a') as f:
        f.write(str)


# In[ ]:


#################################################
#                                               #
#  Function : widthCheck                        #
#                                               #
#  引数： 1 int (width size)                     #
#        2 int (margin )                        #
#        3 string (check_data )                 #
#                                               #
#  戻り値：  幅いっぱいの時  TRUE                   #
#           幅に足りない時  FALSE                  #
#################################################


def widthCheck(col_width, margin, data):
    if data == "blank_data":
        return False
    cal = col_width - margin
    cal = int(cal/12)
# --------------- 幅よりも大きかったらTrueを返す------  mod的な
    i = len(data)
    while cal < i:
        i -= cal
        if cal <= 0:
            break

    if cal - 2 <= i:
        return True
    else:
        return False


# In[ ]:


#################################################
#                                               #
#  Function : readWidth                        #
#                                               #
#  引数： 1 tuple (style)                         #
#                                               #
#  戻り値：  int（widthの値）                         #
#                                               #
#################################################

def readWidth(i):
    #       if i.find('width:') >= 0 and parser.st_tag == 'col' and parser.end_tag != 'col':

    no_width = i.find('width:')
    no_dot = i[no_width:].find('.')
    no_px = i[no_width:].find('px')
    no_pt = i[no_width:].find('pt')

    if no_dot >= 0:
        return int(i[no_width + 6: no_width + no_dot])
    elif no_px > 0:
        return int(i[no_width + 6: no_width + no_px])
    elif no_pt > 0:
        return int(i[no_width + 6: no_width + no_pt])


# In[ ]:


#################################################
#                                               #
#  Function : readMargin                       #
#                                               #
#  引数： 1 tuple (style)                        #
#                                               #
#  戻り値：  int(左右のmarginの　合計値)               #
#                                               #
#################################################

def readMargin(i):
    if i.find('margin-left') >= 0:
        no_margin_left = i.find('margin-left:')
        tmp_i = i[no_margin_left:]
        no_dot = tmp_i.find('.')
        no_px = tmp_i.find('px')
        no_pt = tmp_i.find('pt')

        if no_dot == -1 and no_px == -1 and no_pt == -1:
            return 0

        if (no_dot >= 0 and no_dot < no_px) or (no_dot >= 0 and no_dot < no_pt):
            margin_total = int(tmp_i[12: no_dot])
        elif no_px > 0:
            margin_total = int(tmp_i[12: no_px])
        elif no_pt > 0:
            margin_total = int(tmp_i[12: no_pt])
    else:
        margin_total = 0
        tmp_i = i

    if i.find('margin-right:') >= 0:
        no_margin_right = i.find('margin-right:')
        tmp_i = i[no_margin_right:]
        no_dot = tmp_i.find('.')
        no_px = tmp_i.find('px')
        no_pt = tmp_i.find('pt')

        if (no_dot >= 0 and no_dot < no_px) or (no_dot >= 0 and no_dot < no_pt):
            return margin_total + int(tmp_i[13:no_dot])
        elif no_px > 0:
            return margin_total + int(tmp_i[13: no_px])
        elif no_pt > 0:
            return margin_total + int(tmp_i[13: no_pt])
    else:
        return margin_total


# In[ ]:


#################################################
#                                               #
#  Function : main                              #
#                                               #
#  引数： 1 プログラムファイル名                     #
#  引数： 2 校正元ファイル名                        #
#  引数： 3 校正先ファイル名                        #
#                                               #
#################################################

def main():

    # 引数で校正元ファイル名と校正先ファイル名を取得
    #    dir = sys.argv[1]
    # print(os.getcwd())
    # directory_list = glob.glob(os.getcwd() + '/S100????')

    # for dir in directory_list:
    #    file_list = glob.glob(dir + '/XBRL/PublicDoc/*_ixbrl.htm')
    #    if not (os.path.exists(dir + '/XBRL/PublicDocClean')):
    #        os.mkdir(dir + '/XBRL/PublicDocClean')

    #    for file in file_list:
    #        input_file = file
    #        output_file = file.replace('PublicDoc', 'PublicDocClean')
    #        readData(input_file, output_file)

    input_file = sys.argv[1]
    output_file = sys.argv[1].replace('.htm', '_proofing.htm')
    print(input_file)
    print(output_file)

    readData(input_file, output_file)


# In[ ]:

#################################################
#                                               #
#  function ： replaceBlank                      #
#                                               #
#  input_file   :                               #
#                                               #
#  return       : prettufy                      #
#                                               #
#################################################


def replaceBlank(input_file, flg):

    with open(input_file, encoding="utf-8-sig") as f:
        data_lines = f.read()

    # 文字列置換
    if flg == 0:
        data_lines = data_lines.replace("&#160;", "blank_data")
    elif flg == 1:
        data_lines = data_lines.replace("blank_data", "&#160;")

    # 同じファイル名で保存
    with open(input_file, mode="w", encoding="utf-8-sig") as f:
        f.write(data_lines)

    return input_file

#################################################
#                                               #
#  function ： replaceBlank                      #
#                                               #
#  input_file   :                               #
#                                               #
#  return       : prettufy                      #
#                                               #
#################################################


def prCheck(par_flg, nxt_flg):
    if par_flg == True and nxt_flg == True:
        return True
    return False


#################################################
#                                               #
#  function ： prettifyLine                      #
#                                               #
#  input_file   :                               #
#                                               #
#  return       : prettify                      #
#                                               #
#################################################

def prettifyLine(line):

    parser = MyHTMLParser()
    parser.st_tag = []
    parser.st_style = []
    parser.end_tag = []
    parser.html_data = []

    bf_st_tag = NONE
    bf_end_tag = NONE

    af_st_tag = NONE
    af_end_tag = NONE

    parser.feed(line)

    if len(parser.st_tag) > 0:
        bf_st_tag = parser.st_tag

    if len(parser.end_tag) > 0:
        bf_end_tag = parser.end_tag

    parser.st_tag = []
    parser.st_style = []
    parser.end_tag = []
    parser.html_data = []

    m_st_tag = line[:line.find('>')+1]
    m_end_tag = line[line.rfind('<'):]

    soup = BeautifulSoup(line)
    line = soup.prettify()
    parser.feed(line)

    # -------------------------------------
    if len(parser.st_tag) > 0:
        af_st_tag = parser.st_tag

    if len(parser.end_tag) > 0:
        af_end_tag = parser.end_tag

    count = 0
    for pre_tag in af_st_tag:
        if pre_tag == bf_st_tag[0]:
            break
        else:
            line = line[len(pre_tag)+4: len(line)-(len(pre_tag)+3 + count)]
            count += 1

    st_count = count
    i = 0
    while st_count < len(af_st_tag):
        if af_st_tag[st_count] == bf_st_tag[i]:
            pass
        else:
            line = m_st_tag + '\n' + line
        st_count += 1
        i += 1

    end_count = count
    i = 0
    while end_count < len(af_end_tag):
        if af_end_tag[end_count] == bf_end_tag[i]:
            pass
        else:
            line = line + m_end_tag
            break
        end_count += 1
        i += 1

    return line


#################################################
#                                               #
#  function ： makeInputFile                      #
#                                               #
#  input_file   :                               #
#                                               #
#  return       : prettufy                      #
#                                               #
#################################################


def makeInputFile(input_file):
    table_flg = False
    tmp_file = os.getcwd() + '/tmp2.htm'
    with open(tmp_file, 'w') as refresh:
        refresh.write('')

    with open(input_file, encoding='utf-8-sig') as f:
        for line in f:
            parser = MyHTMLParser()
            parser.st_tag = []
            parser.st_style = []
            parser.end_tag = []
            parser.html_data = []

            st_tag = NONE
            end_tag = NONE
            st_style = NONE

            parser.feed(line)
            if len(parser.st_tag) > 0:
                st_tag = parser.st_tag[0]
            if len(parser.end_tag) > 0:
                end_tag = parser.end_tag[0]
            if len(parser.st_style) > 0:
                st_style = parser.st_style[0]

            if st_tag == 'table':
                table_flg = True
            elif end_tag == 'table':
                table_flg = False
            elif table_flg == True and len(parser.st_tag) > 1:
                line = prettifyLine(line)
            writeData(tmp_file, line)

    return tmp_file

# In[ ]:


#################################################
#                                               #
#  Function : readData                         #
#                                               #
#  引数： 1 tuple (style)                        #
#                                               #
#  戻り値：  幅いっぱいの時  TRUE                   #
#           幅に足りない時  FALSE                  #
#################################################
# def readData(args):
def readData(input_file, output_file):

    table_flg = False
    type_no = 0
    stock_data = NONE
    data_stc_count = 0

    dt = datetime.datetime.today()

    data_check_file = os.getcwd() + '/data_tmp2.htm'
    with open(data_check_file, 'w') as f:
        f.write('')
    with open(os.getcwd() + '/data_stc.txt', 'w') as reflesh:
        reflesh.write('')


#    with open(args[1]) as f:
#    with open(os.getcwd() + '/0105010_honbun_jpcrp030000-asr-001_E04869-000_2020-03-31_01_2020-06-25_ixbrl.htm') as f:
#    input_file = os.getcwd() + \        '/0101010_honbun_jpcrp030000-asr-001_E04869-000_2020-03-31_01_2020-06-25_ixbrl.htm'

    shutil.copyfile(input_file, data_check_file)

    input_file = data_check_file

    input_file = replaceBlank(input_file, 0)

    input_file = makeInputFile(input_file)

    f = open(input_file, encoding='utf-8-sig')
    data_tmp = open(os.getcwd() + '/data_stc.txt', 'a')
    #        file_name = args[2] + '{}{}_{}{}{}.htm'.format(dt.month, dt.day, dt.hour,dt.minute, dt.second )
#    file_name = os.getcwd() + '/html_proofing_xbrl' + '{}{}_{}{}{}.htm'.format(dt.month, dt.day, dt.hour, dt.minute, dt.second)
    file_name = output_file
    with open(file_name, 'w') as reflesh:
        reflesh.write('')
#        str = NONE
#        check_data = NONE
#        type_no = 0
    skip_flg = False
    data_list = []
    data_count = 0
    table_flg = False
    par_flg = False
    nxt_flg = False

    col_width = []
    col_count = 0
    margin = 0
    col_flg = False
    p_tmp_str = NONE
    for line in f:

        parser = MyHTMLParser()

        parser.st_tag = []
        parser.st_style = []
        parser.end_tag = []
        parser.html_data = []

        data = NONE
        st_tag = NONE
        end_tag = NONE
        st_style = NONE

        parser.feed(line)

        if len(parser.st_tag) > 0:
            st_tag = parser.st_tag[0]

        if len(parser.end_tag) > 0:
            end_tag = parser.end_tag[0]
        if len(parser.st_style) > 0:
            st_style = parser.st_style[0]
        if len(parser.html_data) > 0:
            for html_data in parser.html_data:
                if data == NONE:
                    data = html_data
                else:
                    data = data + html_data
        for style in st_style:
            if type(style) == tuple:
                for i in style:
                    if i.find('width:') >= 0 and st_tag == 'col':
                        col_width.append(readWidth(i))
                        col_flg = True
                    elif i.find('margin-') >= 0:
                        margin = readMargin(i)
                    elif i.find('CompanyHistoryTextBlock') > 0:
                        skip_flg = True
        if st_tag == 'table' and skip_flg == False:
            table_flg = True
        elif st_tag == 'p' or st_tag == 'span':
            par_flg = True
        elif end_tag == 'table':
            table_flg = False
            skip_flg = False
            col_width = []
            col_count = 0
            margin = 0
            col_flg = False
        elif end_tag == 'td' and col_flg == True:
            if nxt_flg == True:
                data_list[data_count - 1][1] = False
            col_count += 1
            if len(col_width) <= col_count:
                col_count = 0
            margin = 0
        elif end_tag == 'tr':
            if nxt_flg == True:
                data_list[data_count - 1][1] = False
            nxt_flg = False
            col_count = 0
        if len(data) > 1 and table_flg == True and col_flg == True:
            if data_count > 0:
                if nxt_flg == data_list[data_count - 1][1]:
                    if data == 'blank_data':
                        data_list[data_count - 1][1] = False
                        data_list.append([False, False])
                        data_tmp.write(str(data_stc_count) + ' ' + str(
                            data_list[data_stc_count][0]) + ' , ' + str(data_list[data_stc_count][1]) + data + '\n')
                    else:
                        data_list.append([prCheck(
                            par_flg, data_list[data_count - 1][1]), widthCheck(col_width[col_count], margin, data)])
                        data_tmp.write(str(data_stc_count) + ' ' + str(
                            data_list[data_stc_count][0]) + ' , ' + str(data_list[data_stc_count][1]) + data + '\n')
                    data_stc_count += 1
                else:
                    if data == 'blank_data':
                        data_list[data_count - 1][1] = False
                        data_list.append([False, False])
                        data_tmp.write(str(data_stc_count) + ' ' + str(
                            data_list[data_stc_count][0]) + ' , ' + str(data_list[data_stc_count][1]) + data + '\n')
                    else:
                        data_list.append([prCheck(par_flg, False), widthCheck(
                            col_width[col_count], margin, data)])
                        data_tmp.write(str(data_stc_count) + ' ' + str(
                            data_list[data_stc_count][0]) + ' , ' + str(data_list[data_stc_count][1]) + data + '\n')
                        data_stc_count += 1

                nxt_flg = widthCheck(col_width[col_count], margin, data)

            else:
                data_list.append([prCheck(par_flg, False), widthCheck(
                    col_width[col_count], margin, data)])
                data_tmp.write(str(data_stc_count) + ' ' + str(
                    data_list[data_stc_count][0]) + ' , ' + str(data_list[data_stc_count][1]) + data + '\n')
                data_stc_count += 1
                nxt_flg = widthCheck(col_width[col_count], margin, data)

            data_count += 1
        if end_tag == 'p' or end_tag == 'span':
            par_flg = False
    f.close()
    data_tmp.close()

    with open(input_file, encoding='utf-8-sig') as f:
        data_count = 0
        table_flg = False
        par_flg = False
        nxt_flg = False
        skip_flg = False

        col_width = []
        col_count = 0
        margin = 0
        col_flg = False

        for line in f:
            parser = MyHTMLParser()

            parser.st_tag = []
            parser.st_style = []
            parser.end_tag = []
            parser.html_data = []

            data = NONE
            st_tag = NONE
            end_tag = NONE
            st_style = NONE

            parser.feed(line)

            if len(parser.st_tag) > 0:
                st_tag = parser.st_tag[0]

            if len(parser.end_tag) > 0:
                end_tag = parser.end_tag[0]

            if len(parser.st_style) > 0:
                st_style = parser.st_style[0]
            if len(parser.html_data) > 0:
                for html_data in parser.html_data:
                    if data == NONE:
                        data = html_data
                    else:
                        data = data + html_data

            for style in st_style:
                if type(style) == tuple:
                    for i in style:
                        if i.find('width:') >= 0 and st_tag == 'col':
                            col_width.append(readWidth(i))
                            col_flg = True
                        elif i.find('margin-') >= 0:
                            margin = readMargin(i)
                        elif i.find('CompanyHistoryTextBlock') > 0:
                            skip_flg = True
            if st_tag == 'br':
                continue
            elif st_tag == 'table' and skip_flg == False:
                table_flg = True
            elif st_tag == 'p' or st_tag == 'span':
                par_flg = True
            elif end_tag == 'table':
                table_flg = False
                skip_flg = False
                col_width = []
                col_count = 0
                margin = 0
                col_flg = False

            if len(data) > 1 and table_flg == True and col_flg == True:
                if st_tag != NONE or end_tag != NONE:
                    if data != 'blank_data':
                        if st_tag != 'span':
                            if data_list[data_count][0] == False and data_list[data_count][1] == True:
                                if line.find('\n') > 0 and end_tag == 'p':
                                    line = line[:int(
                                        '-' + str(int(len(end_tag))))-4]
                                else:
                                    line = line[:int(
                                        '-' + str(int(len(end_tag))))]
                            elif data_list[data_count][0] == True and data_list[data_count][1] == True:
                                line = data
                            elif data_list[data_count][0] == True and data_list[data_count][1] == False:
                                line = data + '</p>'
                    elif data_list[data_count - 1][1] == True:
                        line = '</p>' + line
                    data_count += 1
                elif len(data) > 0:
                    data_count += 1
            elif len(data) == 0 and end_tag == 'p' and data_list[data_count - 1][1] == True and table_flg == True:
                continue
            elif len(data) == 0 and st_tag == 'p' and data_list[data_count - 1][1] == True and table_flg == True:
                continue
            writeData(file_name, line)
            if end_tag == 'p' or end_tag == 'span':
                par_flg = False

    replaceBlank(file_name, 1)


# In[ ]:


if __name__ == "__main__":
    for arg in sys.argv:
        print("------------------------")
        print(arg)
        print("------------------------")
    main()
    print('---- end ---')
