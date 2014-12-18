# -*- coding: utf-8 -*-
'''
Created on 2014-12-1

@author: simon
'''
import Tkinter
import tkFileDialog
import tkMessageBox
import os
import shutil

from docs_tool import docs_tool
import adjust_html_style
import tool

def main():
    root = Tkinter.Tk()
    root.withdraw()
    
    #选择待处理的html文件夹所在路径
    html_srcdir=tkFileDialog.askdirectory(parent=root, initialdir="D:",title="选择待处理的帮助文档所在目录")
    if html_srcdir == "":
        tkMessageBox.showerror('未选择任何文件夹',"请选择从confluence导出的html资源所在文件夹！")
        return ;
    
    #将待处理的html文件夹复制一份到当前目录,处理复制出来的这一份
    html_father = os.path.split(html_srcdir)[0]
    html_targetdir = html_father + '/' + os.path.split(html_srcdir)[1] + "_target"
    if os.path.exists(html_targetdir) == True:
        shutil.rmtree(html_targetdir)
    shutil.copytree(html_srcdir, html_targetdir)
    
    #导出的html页面中多了一个index.html,要删除,在帮助文档中没有用。
    index_html = os.path.join(html_targetdir,"index.html")
    if os.path.exists(index_html):
        os.remove(index_html)
    
    #实例化处理类
    dt = docs_tool()
    dt.set_docs_path(html_targetdir)
    
#     contextstxt_path = html_targetdir + '/' + "contexts.txt"
#     toctxt_path = html_targetdir + '/' + "toc.txt"
    contextstxt_path = "contexts.txt"
    toctxt_path = "toc.txt"
    
    #验证文件是否存在
    if os.path.exists(contextstxt_path) == False:
        tkMessageBox.showerror("文件不存在", "contexts.txt不在当前目录内，请将文件拷贝进来！")
        return
    if os.path.exists(toctxt_path) == False:
        tkMessageBox.showerror("文件不存在", "toc.txt不在当前目录内，请将文件拷贝进来！")
        return
    dt.set_contextstxt_path(contextstxt_path)
    dt.set_toctxt_path(toctxt_path)
    
    
    #删除未引用的图片
    dt.delete_unquoted_images()
    #生成toc.xml
    dt.generate_toc_xml()
    #生成contexts.xml
    dt.generate_contexts_xml()
    #格式个性化调整
    dt.adjust_style()
    tkMessageBox.showinfo("处理完成", "处理后的文件夹位于"+html_targetdir);
    return 

def help_info():
    help(docs_tool)
    help(adjust_html_style)
    help(adjust_html_style.add_navigator2htmlpage)
    help(tool)
    help(tool.Chinese2Pinyin)
    help(tool.get_contexts_tree)
    help(tool.get_toc_tree)
    help(tool.get_url_title_map)
    
if __name__ == '__main__':
    main()
    #help_info()
    
