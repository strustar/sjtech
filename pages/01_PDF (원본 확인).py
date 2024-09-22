import streamlit as st
import time, os, gdown, tempfile
import pdf_Fcn

# os.system('cls')  # 터미널 창 청소, clear screen
total_start_time = time.time();  start_time = time.time()
st.set_page_config(page_title = "PDF 자료 분석", page_icon = "✨", layout = "wide",    # centered, wide
                    initial_sidebar_state="expanded",
                    # runOnSave = True,
                    menu_items = {        #   initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
                        # 'Get Help': 'https://www.extremelycoolapp.com/help',
                        # 'Report a bug': "https://www.extremelycoolapp.com/bug",
                        # 'About': "# This is a header. This is an *extremely* cool app!"
                    })

col = st.sidebar.columns(2)
with col[0]:
    keywords = st.text_input("#### :green[✨ 키워드 입력] (공백으로 구분)", "신축 이음").split()    
with col[1]:
    keywords_condition = st.radio('#### :green[✨조건을 선택하세요]', ['and', 'or'], horizontal=True, index=0)

st.sidebar.write('---')
search_condition = st.sidebar.radio('#### :green[✨검색할 조건을 선택하세요]', ['폴더에서 검색', '파일들을 업로드해서 검색', '구글 드라이브에서 검색'], horizontal=False, index=2)

if '폴더' in search_condition:
    pdf_folders = pdf_Fcn.get_folders_with_pdfs('.')

    col = st.sidebar.columns([2, 1])
    with col[0]:
        pdf_folder = st.selectbox("#### :blue[검색할 폴더를 선택하세요]", pdf_folders[1:], index=2)
        pdf_list = os.listdir(pdf_folder)
    with col[1]:
        st.write('');  st.write('')
        st.write(f'#### 파일 개수 : {len(pdf_list)}개')
    with st.sidebar.expander('#### :blue[파일 목록을 보시려면 클릭하세요]'):
        st.write(pdf_list)


    for idx, pdf_name in enumerate(pdf_list):
        # idx
        # if idx > 2:
        #     break

        pdf_path = os.path.join(pdf_folder, pdf_name)
        pdf_Fcn.main(pdf_path, keywords, keywords_condition)
elif '업로드' in search_condition:  # 업로드 파일
    uploaded_files = st.sidebar.file_uploader("#### :blue[PDF 파일들을 끌어 놓으세요]", type=["pdf"], accept_multiple_files=True)    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            pdf_Fcn.main(uploaded_file, keywords, keywords_condition)
    else:
        st.write('#### :blue[왼쪽 사이드바에서 검색할 PDF 파일들을 끌어 놓으세요]')
else:  # 구글 드라이브에서 검색
    gdrive_url = st.sidebar.text_input("#### :blue[구글 드라이브 파일 URL을 입력하세요]", "https://drive.google.com/file/d/1BrWtUEHPNzupNnfyTv9sUHryBbkpXEsn/view?usp=sharing")
    
    if gdrive_url:
        if 'gdrive_file' not in st.session_state:
            with st.spinner('구글 드라이브에서 파일 다운로드 중...'):
                file_id = gdrive_url.split('/')[-2]
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    output = '도로설계요령(2020) 제3권 교량.pdf' #tmp_file.name
                    gdown.download(f'https://drive.google.com/uc?id={file_id}', output, quiet=False)
                st.session_state.gdrive_file = output
        else:
            output = st.session_state.gdrive_file
        
        # st.success('파일 다운로드 완료!')
        try:
            pdf_Fcn.main(output, keywords, keywords_condition)
        finally:
            # 파일 처리 후 항상 삭제
            pass
            # os.remove(output)
    else:
        st.write('#### :blue[구글 드라이브 파일 URL을 입력하세요]')

# Metric 스타일
st.markdown("""
    <style>
    [data-testid="stMetricLabel"] {
        font-size: 20px !important;
        color: green !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: orange;
        # font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
st.sidebar.write('---')
st.sidebar.write(f"#### :orange[총 검색 시간 : {time.time() - start_time:.2f} 초]")