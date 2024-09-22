import streamlit as st
import fitz, os, re  # PyMuPDF
import pandas as pd
from PIL import Image, ImageDraw
import pdf_style

def get_folders_with_pdfs(path='.'):  # 현재 디렉토리
    folders_with_pdfs = []    
    for root, dirs, files in os.walk(path):
        if any(file.lower().endswith('.pdf') for file in files):
            relative_path = os.path.relpath(root, start=path)
            if relative_path == '.':
                folders_with_pdfs.append(os.path.basename(path))
            else:
                folders_with_pdfs.append(relative_path)
    
    return folders_with_pdfs

def main(pdf_path, keywords, condition):    
    if keywords:        
        if hasattr(pdf_path, 'seek'):
            pdf_path.seek(0)
                    
        if isinstance(pdf_path, str):  # 로컬 파일 경로    
            doc = fitz.open(pdf_path)
            file_size = os.path.getsize(pdf_path)
            pdf_name = os.path.basename(pdf_path)            
        else:  # UploadedFile 객체
            doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
            file_size = pdf_path.size
            pdf_name = pdf_path.name

        found_pages = [];  found_texts = [];  n_per_page = [];  imgs = []
        for page_num in range(len(doc)):            
        # for page_num in range(6): 
            page = doc[page_num]
            line_text, line_bbox = keyword_line(page, keywords, condition)            
            
            if line_bbox:                
                found_texts.extend(line_text)
                n_per_page.append(len(line_text))
                found_pages.append(page_num + 1)                
                img = highlight_page(pdf_path, page_num + 1, keywords, condition)
                imgs.append(img)

        st.write(f"### 📚 PDF 정보 : :green[[{pdf_name}]]")
        condition = ' : 모두 포함된 문장' if condition == 'and' else ' : 하나라도 포함된 문장'
        if len(keywords) == 1:
            condition = ''                
        
        col = st.columns([1,1,1,2])
        with col[0]:
            st.metric(label="페이지 수", value=f"{len(doc):,.0f} 쪽")
        with col[1]:
            st.metric(label="파일 크기", value=f'{file_size/1024/1024:,.1f} MB')
        with col[2]:
            st.metric(label="검색 개수", value=f'{sum(n_per_page):,.0f}개 찾음')
        with col[3]:
            st.metric(label="검색어", value=f'{keywords} {condition}')

        if n_per_page:
            df = pd.DataFrame()
            pages = [];  img = []
            for i in range(len(found_pages)):
                for j in range(n_per_page[i]):
                    if j == 0:
                        img.append(imgs[i])
                        pages.append(found_pages[i])
                    else:
                        img.append('')
                        pages.append('')
            
            df['페이지'] = pages
            df['찾은 내용'] = found_texts
            df['원본 페이지'] = img            
            pdf_style.style(df, keywords)
        else:
            st.write('#### :blue[검색된 내용이 없습니다.]')

        doc.close()
        st.write('---')

def keyword_line(page, keywords, condition):
    keywords = [k.lower() for k in keywords]
    text = page.get_text("text")
    # text = page.get_text("word")
    # st.write(text)
    lines = text.split('\n')  # 줄 단위로 분리    
    # lines = re.split(r'(?<=[.!?])\s+', text)  # 문장 단위로 분리  .!?로 분리

    line_text = [];  line_bbox = []
    for line in lines:
        lower_line = line.lower()        
        # 조건에 따라 키워드 일치 여부를 확인, \은 한줄 코드를 2줄 이상으로 쓸때
        if (condition == 'and' and all(keyword in lower_line for keyword in keywords)) or \
            (condition == 'or' and any(keyword in lower_line for keyword in keywords)):
            line_text.append(line)
            bbox = page.search_for(line.strip())
            
            if bbox:
                line_bbox.extend(bbox)    

    return line_text, line_bbox

@st.cache_data
def highlight_page(pdf_path, page_number, keywords, condition, zoom=3):
    if hasattr(pdf_path, 'seek'):
        pdf_path.seek(0)
    
    if isinstance(pdf_path, str):  # 로컬 파일 경로    
        doc = fitz.open(pdf_path)    
    else:  # UploadedFile 객체
        doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
    page = doc[page_number - 1]
    
    # 전체 줄에서 키워드가 포함된 줄을 찾고 하이라이트
    _, line_bbox = keyword_line(page, keywords, condition)
    
    # 페이지를 고해상도 이미지로 변환
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # 반투명한 하이라이트 추가
    draw = ImageDraw.Draw(img, "RGBA")
    colors = [(255, 0, 0, 55), (0, 255, 0, 55), (0, 0, 255, 55), (255, 0, 255, 55), (0, 255, 255, 55), (255, 255, 0, 55)]
    
    # 먼저 모든 매칭된 라인을 반투명 파란색으로 하이라이트
    for bbox in line_bbox:
        rect = fitz.Rect(bbox)
        draw.rectangle([rect.x0*zoom, rect.y0*zoom, rect.x1*zoom, rect.y1*zoom], fill=colors[2])
    
    # 그 다음, 각 키워드에 대해 개별적으로 하이라이트
    for idx, keyword in enumerate(keywords):
        color = colors[idx % len(colors)]
        if condition == 'and':
            for bbox in line_bbox:
                instances = page.search_for(keyword, clip=bbox)
                for inst in instances:
                    rect = fitz.Rect(inst)
                    draw.rectangle([rect.x0*zoom, rect.y0*zoom, rect.x1*zoom, rect.y1*zoom], fill=color)
        else:
            instances = page.search_for(keyword)
            for inst in instances:
                rect = fitz.Rect(inst)
                draw.rectangle([rect.x0*zoom, rect.y0*zoom, rect.x1*zoom, rect.y1*zoom], fill=color)
    
    return img