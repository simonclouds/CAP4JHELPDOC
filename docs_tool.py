# -*- coding: utf-8 -*-
'''
Created on 2014-12-1

@author: cib
'''
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

import os
import shutil
from pyquery import PyQuery as pq

from tool.get_toc_tree import get_toc_tree
from tool.get_url_title_map import get_urltitle_map
from tool.get_contexts_tree import get_contexts_tree
from adjust_html_style.add_navigator2htmlpage import add_headnavi2html, add_tailnavi2html, add_anchor2html

class docs_tool():
    '''
            使用这个类完成帮助文档插件开发前，对内容的预处理。
    '''
    #要处理的目录的路径
    docs_path = ""
    #生成toc.xml的辅助文件toc.txt所在位置
    toctxt_path = ""
    #生成contexts.xml的辅助文件contexts.txt所在位置
    contextstxt_path = ""
    #处理完成的docs保存的目录
    target_docs_path = ""

    #默认为docs_path下面保存着两个文件，如果没有设置的话
    tocxml_path = ""
    contextsxml_path = ""
    
    def set_docs_path(self, docs_path):
        self.docs_path = docs_path;
    
    def set_toctxt_path(self, toctxt_path):
        self.toctxt_path = toctxt_path;
        
    def set_contextstxt_path(self, contextstxt_path):
        self.contextstxt_path = contextstxt_path;

    def set_tocxml_path(self,tocxml_path):
        self.tocxml_path = tocxml_path;
    def set_contextsxml_path(self,contextsxml_path):
        self.contextsxml_path = contextsxml_path;
        
    def __init__(self):
        '''
        Constructor
        '''
    
    
    def adjust_style(self):
        '''
        调整docs目录下所有的html文件的格式。
        1，添加页内导航栏，页前导航和页后导航，也可以只添加其中一个。
        2，为h3标签添加汉语的序号和锚点，为页內添加footer，显示copyright信息
        输入参数：无，通过类成员变量传递
        输出参数：无
        '''
        htmlfilenamelist = os.listdir(self.docs_path)
        toc_tree = get_toc_tree(self.toctxt_path)
        url_title_map = get_urltitle_map(self.docs_path)
        
        for filename in htmlfilenamelist:
            if filename.find('html') != -1:
                filename = os.path.join(self.docs_path,filename);
                add_headnavi2html(filename,toc_tree,url_title_map);
                add_tailnavi2html(filename,toc_tree,url_title_map);
                add_anchor2html(filename);
        return 
    def delete_unquoted_images(self):
        '''
        docs目录中attachments目录下是存放html中插入的图片，这其中的图片都是在编辑期间插入的新图片
                    以及被替换了但是未删除的旧图片，confluenc不会自动删除这些没有在html中引用的图片。因此这个
                    函数将自动去查找那些未引用的图片，删除之。
                    输入：无, 通过类成员变量传递
                    输出：无，删除attachments目录下未被html页面引用的图片。
        '''      
        attachmentsdir = os.path.join(self.docs_path,'attachments')
        
        htmls = os.listdir(self.docs_path)
        for html in htmls:
            html_absfilepath = os.path.join(self.docs_path,html)
            #0，判断是否是html文件，是html文件才处理
            if os.path.isfile(html_absfilepath) and (html_absfilepath[-4:]=="html" or html_absfilepath[-4:]==".htm"):
                
                #1. 找出该html文件中引用了所有的位于attachments下的图片
                try:
                    fin = open(html_absfilepath,'r')
                    sourcedata = fin.read()
                    htmlpq = pq(sourcedata)
                    imgs = htmlpq('img')
                    #img标签包含了所有的图片，将不是attachments下的图片过滤掉(还有images目录下的图片等）
                    #attachment_imgs表示html页面中引用了的位于attachment目录下的图片文件
                    attachment_imgs = self.filte_pictures(imgs)
                    # 1-1 判断该html文件中这类图片是否存在，若不存在（即html中引用了0张位于attachments下的图片）
                    #直接可跳过本次循环？可能先引用了，后来又删除了，那么attachments目录下将会建立此html对应的目录并保存图片。
                    #因此，要将该html对应的pic目录都删除掉吧！！！！
                    
                    imgs_number = len(attachment_imgs)
                     
                    if imgs_number == 0 :
                        continue;
                    
                    #2. 获取存放该html文件图片的文件夹在attachments下的那个目录 ,html.split('.')[0] 是这样子的：436059
                    # html_picture_dir 是这样子的：D:\zhangguosheng\workspace_4eclipse\cap4j3help\html\attachments\436059\
                    html_picture_dir = os.path.join(attachmentsdir, html.split('.')[0])
                    #2-1 判断该目录是否存在，若目录不存在，直接跳过本次循环
                    if os.path.exists(html_picture_dir) != True:
                        continue;
                    #3. 目录存在，列举这个目录下的所有图片
                    pictures_indir = os.listdir(html_picture_dir)
                    #3-1 如果目录为空，直接跳过本次循环；删除该空目录!
                    pictures_number = len(pictures_indir)
                    if pictures_number <= 0:
                        os.rmdir(html_picture_dir)
                        continue;
                    #4. 筛选出html文件中未出现的图片
                    imgs_notusedlist = [val for val in pictures_indir if val not in attachment_imgs]
                    #5. 将未出现的图片从磁盘上删除
                    for img in imgs_notusedlist:
                        img_absfilepath = os.path.join(html_picture_dir,img)
                        os.remove(img_absfilepath)
                        #print img_absfilepath
                    
                    #再检测一次该目录删完上述图片后是否为空，若未空，删除该目录
                    pictures_number = len(pictures_indir)
                    if pictures_number <= 0:
                        os.rmdir(html_picture_dir)
                        continue;
                except IOError,e:
                    print e
                finally:
                    fin.close()
            
        return 
    def generate_toc_xml(self):
        '''
        使用toc.txt中保存的帮助文档目录树信息，构建toc.xml文件。
        toc.txt文件是需要手动从confluence的服务器web端拷贝下来。因此toc.xml的生成时半自动的。
        后期可以优化一下，直接从confluence页面中把树形结构抓取出来，生成toc.txt文件。
        输入：无，通过类成员变量传递
        输出：无，生成toc.xml文件
        '''
        toc_tree = get_toc_tree(self.toctxt_path)
        url_title_map = get_urltitle_map(self.docs_path)
        
        if(self.tocxml_path == ""):
            self.set_tocxml_path(self.docs_path + "/" + "toc.xml");
        
        outfile = self.tocxml_path
        len_tree = len(toc_tree);

        try:
            fout = open(outfile,'w')
            fout.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
                #遍历目录，生成xml文件内容
            for cur in range(0,len_tree):
                curnode = toc_tree[cur];
                #当前节点的层次
                curdepth = curnode.rfind('\t') + 1;
                curnode = curnode.strip()#.replace('&','&amp;');
                #如果是根节点，一般根节点在第一行，其实这段应该提出到循环外，默认是单根的树
                if curdepth == 0 and curnode != '':
                    #print('<toc label="' + curnode + '" ' + 'topic="' + urltitlemap[curnode] + '" >')
                    fout.write('<toc label="' + curnode + '" ' + 'topic="' + url_title_map[curnode] + '" >' + '\n')
                    continue;
            
                #下一个节点的index
                next = cur + 1 ;
                
                #文件结束,循环结束,输出当前节点，并关闭目录层次至倒数第一层，最后一层由</toc>来关闭
                if next >= len_tree:
                    fout.write(curdepth*'\t' + '<topic label="' + curnode + '" ' + 'href="' + url_title_map[curnode] + '" />' + '\n')
                    for d in range(0,curdepth-1):
                        fout.write((curdepth-d-1)*'\t' + '</topic>' + '\n')
                        fout.write('</toc>' + '\n')
                    break;
                
                #下一个节点的内容
                nextnode= toc_tree[next];
                
                #下一个节点的树的层次，层次以'\t'来表示，一个'\t'表示一层深度
                nextdepth = nextnode.rfind('\t') + 1;
            
                #当前节点是叶子节点，下一节点深度与自己一样
                #那么输出为 <topic label="aaa" href="docs/123456.html" />
                if curdepth == nextdepth:
                    fout.write(curdepth*'\t' + '<topic label="' + curnode + '" ' + 'href="' + url_title_map[curnode] + '" />' + '\n')
                #当前节点是叶子节点，且当前节点所在目录结束
                # 输出当前的叶子节点，再关闭目录，关闭的深度要计算 dep = curdepth - nextdepth
                # <topic label="aaa" href="docs/123456.html" />
                # 再输出</topic>\n  dep次，关闭dep深度的目录
                elif curdepth > nextdepth:
                    dep = curdepth - nextdepth;
                    fout.write(curdepth*'\t' + '<topic label="' + curnode + '" ' + 'href="' + url_title_map[curnode] + '" />' + '\n')
                    for d in range(0,dep):
                        fout.write((curdepth-d-1)*'\t' + '</topic>' + '\n')
                #当前节点是目录节点，下一个节点是当前节点的子节点
                #<topic label="aaa" href="docs/123456.html">
                else :
                    fout.write(curdepth*'\t' + '<topic label="' + curnode + '" ' + 'href="' + url_title_map[curnode] + '" >' + '\n')
        except IOError,e:
            print(e)
        finally:
            fout.close()
        
        return

    def generate_contexts_xml(self):
        '''
                    使用contexts.txt中保存的contexts索引关联的页面的目录节点，构建contexts.xml。
        contexts.txt文件需要先整理一些在IDE界面中可能会使用到的关键词，关键词会关联一些html页面，
                    但是关键词下只需要写上关键词关联的html文件的title，即html在confluence中目录树上的节点名。
                    输入：无，通过类成员变量传递
                    输出：无，生成文件contexts.xml
        '''
        contexts_tree = get_contexts_tree(self.contextstxt_path)
        title_url_map = get_urltitle_map(self.docs_path)
                
        if(self.contextsxml_path == ""):
            self.set_contextsxml_path(self.docs_path + "/" + "contexts.xml");
        
        outfile = self.contextsxml_path
        
        len_tree = len(contexts_tree);

        try:
            fout = open(outfile,'w')
            fout.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
            fout.write('<?NLS TYPE="org.eclipse.help.contexts"?>' + '\n')
            fout.write('<contexts>' + '\n')
            
            for cur in range(0,len_tree):
                curnode = contexts_tree[cur];
                curdepth = curnode.rfind('\t') + 1;
            
                next = cur + 1;
                #文件结束了
                if next >= len_tree:
                    if curdepth == 0:
                        curnode = curnode.strip()
                        if curnode.find('|') != -1:
                            content = curnode.split('|');
                            description = content[0];
                            id = content[1];
                        else :
                            description = curnode;
                            id = "";
                        fout.write('\n\t<context id="' + id + '">' + '\n');
                        fout.write('\t\t<description>' + description + '</description>' + '\n');
                        fout.write('\t</context>' + '\n');
                    else:
                        curnode = curnode.strip();
                        #curnode = unicode(curnode,'utf-8')
                        fout.write('\t\t<topic label="' + curnode + '" ' + 'href="' + title_url_map[curnode] + '" />' + '\n')
                        #自己关闭标签，后面没有节点了
                        fout.write('\t</context>' + '\n')
                    #关闭根节点标签
                    fout.write('</contexts>'+'\n')
                    break;
                
                nextnode = contexts_tree[next];
                nextdepth = nextnode.rfind('\t') + 1;
            
                #当前节点是父节点，下一个是叶子节点
                if curdepth < nextdepth:
                    if curnode.find('|') != -1:
                        content = curnode.split('|');
                        description = content[0];
                        id = content[1];
                    else :
                        description = curnode;
                        id = "";
                    fout.write('\n\t<context id="' + id + '">' + '\n');
                    fout.write('\t\t<description>' + description + '</description>' + '\n');
                elif curdepth == nextdepth:
                    #当前节点是父节点 ，层次为0，下一个节点也是父节点,那么当前的节点就没有叶子节点
                    if curdepth == 0:
                        curnode = curnode.strip()
                        if curnode.find('|') != -1:
                            content = curnode.split('|');
                            description = content[0];
                            id = content[1];
                        else :
                            description = curnode;
                            id = "";
                        fout.write('\n\t<context id="' + id + '">' + '\n');
                        fout.write('\t\t<description>' + description + '</description>' + '\n');
                        fout.write('\t</context>' + '\n');
                    #当前节点是叶子节点，下一个也是
                    else:
                        curnode = curnode.strip();
                        #curnode = unicode(curnode,'utf-8')
                        fout.write('\t\t<topic label="' + curnode + '" ' + 'href="' + title_url_map[curnode] + '" />' + '\n')
                #当前节点是叶子节点，下一个节点是父节点
                else:
                    curnode = curnode.strip();
                    #curnode = unicode(curnode,'utf-8')
                    fout.write('\t\t<topic label="' + curnode + '" ' + 'href="' + title_url_map[curnode] + '" />' + '\n')
                    fout.write('\t</context>' + '\n')
        except IOError,e:
            print(e)
        finally:
            fout.close()
        return
    
    def filte_pictures(self,pqimg): 
        '''
        类内部函数，用于过滤图片，html页面中出现了的图片，都保存在qpimg对象中，pgimg 是一个pquery的对象。
        包含了html页面中出现的所有图片，我们所关心的是位于attachments目录下的图片，因此将位于attachments目录下的图片才放到list中去。
        输入：qpimg 是通过pyquery模块从html页面中提取了所有图片的pyquery对象
        输出：list html中位于attachments目录下的图片名列表
        '''
        list = []
        
        l = len(pqimg)
        for i in range(0,l):
            item = pqimg.eq(i).attr('src')
            if item.find('attachments') != -1:
                object = item.split('/')[-1]
                list.append(object)
        return list
