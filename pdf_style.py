import streamlit as st
import base64, re
from PIL import Image
from io import BytesIO

@st.cache_data
def style(df, keywords):
    # 이미지 Base64 인코딩 함수
    def get_image_base64(image_obj):
        if isinstance(image_obj, str):
            if image_obj.strip() == "":
                return ""
            try:
                with open(image_obj, "rb") as img_file:
                    return base64.b64encode(img_file.read()).decode('utf-8')
            except FileNotFoundError:
                return ""
        elif isinstance(image_obj, Image.Image):
            buffered = BytesIO()
            image_obj.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        else:
            raise ValueError("Invalid input for get_image_base64: expected str or Image object")

    # 텍스트에서 키워드 강조 함수 (여러 키워드 지원)
    def highlight_keywords(text, keywords):
        colors = ['red', 'green', 'blue', 'purple', 'teal', 'orange']
        for idx, keyword in enumerate(keywords):
            color = colors[idx % len(colors)]
            if keyword.lower() in text.lower():
                text = re.sub(f'(?i){re.escape(keyword)}', f'<span style="background-color:{color};">{keyword}</span>', text)
        return text

    # HTML 테이블 생성 함수 (병합 기능 추가)
    def create_html_table(df, keywords):
        html = """
            <style>
                body { color: white;}
                table { width: 1800px; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
                th, td { border: 2px solid #444; padding: 15px; text-align: left; overflow: hidden; text-align: center;>}
                td.findings { text-align: left; } /* 특정 클래스에 대해 왼쪽 정렬 적용 */
                th { background-color: #333; color: #FFF; } /* 열 제목 가운데 정렬 */
                tr:nth-child(even) { background-color: #2C2C2C; }
                tr:nth-child(odd) { background-color: #252525; }
                button { background-color: purple; color: white; border: none; padding: 10px 20px; cursor: pointer; font-size: 18px; }
                button:hover { background-color: green; }
                .image-container { width: 100%; height: 800px; overflow: auto; display: none; }
                img { max-width: 100%; height: auto; }
            </style>
            <table>
                <colgroup>
                    <col style="width: 80px">
                    <col style="width: 800px">
                    <col style="width: 1100px">
                </colgroup>
                <thead>
                    <tr>
                        <th>페이지</th>
                        <th>찾은 내용</th>
                        <th>원본 페이지</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        prev_page = None
        prev_button = None
        rowspan_page = 0
        rowspan_button = 0

        for i, row in df.iterrows():
            highlighted_text = highlight_keywords(row['찾은 내용'], keywords)
            image_base64 = get_image_base64(row['원본 페이지'])

            # 페이지 병합 처리
            if row['페이지'] == '' and prev_page is not None:
                rowspan_page += 1
            else:
                if prev_page is not None:
                    html = html.replace(f'ROWSPAN_PAGE_{prev_page}', str(rowspan_page))
                prev_page = row['페이지']
                rowspan_page = 1
            
            # 버튼 병합 처리
            if row['원본 페이지'] == '' and prev_button is not None:
                rowspan_button += 1
            else:
                if prev_button is not None:
                    html = html.replace(f'ROWSPAN_BUTTON_{prev_button}', str(rowspan_button))
                prev_button = row['원본 페이지']
                rowspan_button = 1

            html += '<tr>'
            if rowspan_page == 1:
                html += f'<td rowspan="ROWSPAN_PAGE_{prev_page}">{prev_page}</td>'
            html += f'<td class="findings">{highlighted_text}</td>'
            if rowspan_button == 1:
                if image_base64:
                    image_html = f"""
                        <button id="btn_{i}" onclick="toggleImage('{i}')">원본페이지 보기</button>
                        <div id="container_{i}" class="image-container">
                            <img src="data:image/png;base64,{image_base64}">
                        </div>
                    """
                else:
                    image_html = prev_button
                html += f'<td rowspan="ROWSPAN_BUTTON_{prev_button}">{image_html}</td>'
            html += '</tr>'

        html += '</tbody></table>'
        html = html.replace(f'ROWSPAN_PAGE_{prev_page}', str(rowspan_page))
        html = html.replace(f'ROWSPAN_BUTTON_{prev_button}', str(rowspan_button))

        # JavaScript를 추가하여 버튼 동작 처리
        js = """
            <script>
                function toggleImage(id) {
                    var container = document.getElementById('container_' + id);
                    var btn = document.getElementById('btn_' + id);
                    if (container) {
                        if (container.style.display === "none" || container.style.display === "") {
                            container.style.display = "block";
                            btn.textContent = "원본페이지 숨기기";
                        } else {
                            container.style.display = "none";
                            btn.textContent = "원본페이지 보기";
                        }
                    }
                }
            </script>
        """
        
        return html + js

    # Streamlit을 사용하여 테이블 표시
    html_table = create_html_table(df, keywords)
    height = len(df)*40 + 400
    if height >= 2000:
        height = 2000
    st.components.v1.html(html_table, width=2100, height=height, scrolling=True)

