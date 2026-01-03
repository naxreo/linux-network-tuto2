#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마크다운 파일을 HTML로 변환하는 스크립트

사용법:
    python3 md_to_html.py input.md output.html

또는:
    python3 md_to_html.py TUTORIAL.md tutorial.html
"""

import re
import sys
import os

def md_to_html(text):
    """
    마크다운 텍스트를 HTML로 변환
    
    Args:
        text: 마크다운 형식의 텍스트
        
    Returns:
        HTML 형식의 텍스트
    """
    # 코드 블록을 먼저 임시 플레이스홀더로 교체
    code_blocks = []
    
    def code_block_replacer(match):
        lang = match.group(1) or 'bash'
        code = match.group(2)
        placeholder = f'__CODE_BLOCK_{len(code_blocks)}__'
        code_blocks.append((placeholder, lang, code))
        return placeholder
    
    text = re.sub(r'```(\w+)?\n(.*?)```', code_block_replacer, text, flags=re.DOTALL)
    
    # 인라인 코드
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # 강조 (볼드)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    
    # 제목 처리 (ID 생성)
    def heading_id(match):
        title = match.group(1)
        # 한글과 영문, 숫자, 공백을 ID로 변환
        id_text = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
        return f'<h2 id="{id_text}">{title}</h2>'
    
    text = re.sub(r'^## (.*?)$', heading_id, text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # 구분선
    text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)
    
    # 링크 처리 (마크다운 링크)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    
    # 리스트 처리
    lines = text.split('\n')
    result = []
    in_ul = False
    in_ol = False
    
    for line in lines:
        # 순서 없는 리스트
        if re.match(r'^[-*] ', line):
            if not in_ul and not in_ol:
                result.append('<ul>')
                in_ul = True
            item = re.sub(r'^[-*] ', '', line)
            result.append(f'<li>{item}</li>')
        # 순서 있는 리스트
        elif re.match(r'^\d+\. ', line):
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if not in_ol:
                result.append('<ol>')
                in_ol = True
            item = re.sub(r'^\d+\. ', '', line)
            result.append(f'<li>{item}</li>')
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if in_ol:
                result.append('</ol>')
                in_ol = False
            result.append(line)
    
    if in_ul:
        result.append('</ul>')
    if in_ol:
        result.append('</ol>')
    
    text = '\n'.join(result)
    
    # 단락 처리
    paragraphs = text.split('\n\n')
    final_result = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<') and not para.startswith('```'):
            # 이미 HTML 태그가 있으면 그대로
            if '<' in para and '>' in para:
                final_result.append(para)
            else:
                final_result.append(f'<p>{para}</p>')
        else:
            final_result.append(para)
    
    text = '\n'.join(final_result)
    
    # 코드 블록 플레이스홀더를 실제 HTML로 복원
    for placeholder, lang, code in code_blocks:
        html_code = f'<pre><code class="language-{lang}">{code}</code></pre>'
        text = text.replace(placeholder, html_code)
    
    return text


def generate_html_template(content, title="문서", nav_link="index.html", nav_text="← 홈으로"):
    """
    HTML 템플릿 생성
    
    Args:
        content: 변환된 HTML 콘텐츠
        title: 페이지 제목
        nav_link: 네비게이션 링크
        nav_text: 네비게이션 텍스트
        
    Returns:
        완전한 HTML 문서
    """
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
      background: #0a0a0a;
      color: #e5e5e5;
      line-height: 1.6;
      padding: 20px;
    }}
    
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      background: #1a1a1a;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }}
    
    .nav-link {{
      position: fixed;
      top: 20px;
      right: 20px;
      background: rgba(26, 26, 26, 0.95);
      padding: 12px 20px;
      border-radius: 8px;
      border: 1px solid #333;
      z-index: 1000;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }}
    
    .nav-link a {{
      color: #60a5fa;
      text-decoration: none;
      font-weight: bold;
      font-size: 14px;
    }}
    
    .nav-link a:hover {{
      color: #7dd3fc;
    }}
    
    h1 {{
      color: #7dd3fc;
      border-bottom: 3px solid #2563eb;
      padding-bottom: 10px;
      margin-bottom: 30px;
      font-size: 2.5em;
    }}
    
    h2 {{
      color: #60a5fa;
      margin-top: 40px;
      margin-bottom: 20px;
      padding-top: 20px;
      border-top: 1px solid #333;
      font-size: 2em;
      scroll-margin-top: 80px;
    }}
    
    h3 {{
      color: #94a3b8;
      margin-top: 30px;
      margin-bottom: 15px;
      font-size: 1.5em;
    }}
    
    h4 {{
      color: #9ca3af;
      margin-top: 20px;
      margin-bottom: 10px;
      font-size: 1.2em;
    }}
    
    p {{
      margin: 15px 0;
      color: #d1d5db;
    }}
    
    pre {{
      background: #0f0f0f;
      border: 1px solid #333;
      border-radius: 4px;
      padding: 15px;
      overflow-x: auto;
      margin: 20px 0;
    }}
    
    code {{
      font-family: 'Courier New', monospace;
      font-size: 14px;
      color: #60a5fa;
      background: rgba(96, 165, 250, 0.1);
      padding: 2px 4px;
      border-radius: 3px;
    }}
    
    pre code {{
      color: #e5e5e5;
      display: block;
      background: transparent;
      padding: 0;
    }}
    
    ul, ol {{
      margin: 15px 0;
      padding-left: 30px;
    }}
    
    li {{
      margin: 8px 0;
      color: #d1d5db;
    }}
    
    a {{
      color: #60a5fa;
      text-decoration: none;
    }}
    
    a:hover {{
      color: #7dd3fc;
      text-decoration: underline;
    }}
    
    strong {{
      color: #fbbf24;
      font-weight: bold;
    }}
    
    hr {{
      border: none;
      border-top: 1px solid #333;
      margin: 40px 0;
    }}
    
    .toc {{
      background: #0f0f0f;
      border: 1px solid #333;
      border-radius: 4px;
      padding: 20px;
      margin: 30px 0;
    }}
    
    .toc h2 {{
      margin-top: 0;
      border-top: none;
      padding-top: 0;
    }}
    
    .toc ul {{
      list-style: none;
      padding-left: 0;
    }}
    
    .toc li {{
      margin: 10px 0;
    }}
    
    .toc a {{
      color: #60a5fa;
    }}
  </style>
</head>
<body>
  <div class="nav-link">
    <a href="{nav_link}">{nav_text}</a>
  </div>
  
  <div class="container">
{content}
  </div>
</body>
</html>'''


def main():
    """메인 함수"""
    if len(sys.argv) < 3:
        print("사용법: python3 md_to_html.py <input.md> <output.html> [title] [nav_link] [nav_text]")
        print("\n예시:")
        print("  python3 md_to_html.py TUTORIAL.md tutorial.html")
        print("  python3 md_to_html.py TUTORIAL.md tutorial.html '리눅스 네트워크 튜토리얼' 'index.html' '← 네트워크 흐름도'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else "문서"
    nav_link = sys.argv[4] if len(sys.argv) > 4 else "index.html"
    nav_text = sys.argv[5] if len(sys.argv) > 5 else "← 홈으로"
    
    # 입력 파일 확인
    if not os.path.exists(input_file):
        print(f"오류: 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
    
    # 마크다운 파일 읽기
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except Exception as e:
        print(f"오류: 파일을 읽을 수 없습니다: {e}")
        sys.exit(1)
    
    # HTML로 변환
    html_content = md_to_html(md_content)
    
    # HTML 템플릿 생성
    html_doc = generate_html_template(html_content, title, nav_link, nav_text)
    
    # HTML 파일 저장
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_doc)
        print(f"✓ {output_file} 생성 완료")
    except Exception as e:
        print(f"오류: 파일을 저장할 수 없습니다: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

