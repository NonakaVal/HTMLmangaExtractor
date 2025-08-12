import os

def generate_index_html(base_dir):
    index_path = os.path.join(base_dir, "index.html")
    chapters = []
    
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and "_capitulo_" in item:
            if os.path.exists(os.path.join(item_path, "leitor.html")):
                chapter_name = item.replace("_", " ").replace("capitulo", "Capítulo")
                
                # Caminho relativo da capa
                cover_rel = os.path.join(item, "pages", "page_02.png")
                cover_abs = os.path.join(base_dir, cover_rel)

                if not os.path.exists(cover_abs):
                    pages = sorted([f for f in os.listdir(os.path.join(item_path, "pages")) 
                                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                    if len(pages) >= 2:
                        cover_rel = os.path.join(item, "pages", pages[1])
                    elif pages:
                        cover_rel = os.path.join(item, "pages", pages[0])
                    else:
                        cover_rel = None

                chapters.append({
                    'path': item,
                    'name': chapter_name,
                    'cover': cover_rel if cover_rel and os.path.exists(os.path.join(base_dir, cover_rel)) else None,
                    'leitor': os.path.join(item, "leitor.html")
                })
    
    if not chapters:
        print("Nenhum capítulo válido encontrado para gerar o índice.")
        return False
    
    chapters.sort(key=lambda x: int(''.join(filter(str.isdigit, x['path']))))
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biblioteca de Mangás</title>
    <style>
        :root {{
            --bg-color: #f8f8f8;
            --card-bg: #ffffff;
            --text-color: #333333;
            --secondary-text: #666666;
            --accent-color: #4a6fa5;
            --border-color: #e0e0e0;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .title {{
            font-size: 28px;
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 5px;
        }}
        
        .subtitle {{
            font-size: 14px;
            color: var(--secondary-text);
        }}
        
        .library-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .chapters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
            padding: 10px;
        }}
        
        .chapter-card {{
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
        }}
        
        .chapter-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
        }}
        
        .cover-container {{
            position: relative;
            width: 100%;
            height: 250px;
            overflow: hidden;
            background-color: #f0f0f0;
        }}
        
        .chapter-cover {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }}
        
        .chapter-card:hover .chapter-cover {{
            transform: scale(1.03);
        }}
        
        .no-cover {{
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--secondary-text);
            font-size: 14px;
        }}
        
        .chapter-info {{
            padding: 14px;
        }}
        
        .chapter-name {{
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 3px;
            color: var(--text-color);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .chapter-number {{
            font-size: 13px;
            color: var(--secondary-text);
        }}
        
        @media (max-width: 768px) {{
            .chapters-grid {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px;
            }}
            
            .cover-container {{
                height: 200px;
            }}
            
            .title {{
                font-size: 24px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .chapters-grid {{
                grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
                gap: 12px;
            }}
            
            .cover-container {{
                height: 180px;
            }}
            
            .chapter-info {{
                padding: 12px;
            }}
            
            .chapter-name {{
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{os.path.basename(base_dir)}</h1>
        <p class="subtitle">{len(chapters)} capítulos disponíveis</p>
    </div>
    
    <div class="library-container">
        <div class="chapters-grid">
"""

    for chapter in chapters:
        cover_html = f'<img src="{chapter["cover"]}" class="chapter-cover" alt="Capa">' if chapter["cover"] else '<div class="no-cover">Sem imagem</div>'
        chapter_num = ''.join(filter(str.isdigit, chapter['path'].split('_capitulo_')[-1]))
        
        html_content += f"""
            <a href="{chapter['leitor']}" class="chapter-card">
                <div class="cover-container">
                    {cover_html}
                </div>
                <div class="chapter-info">
                    <h3 class="chapter-name">{chapter['name'].split(' Capítulo')[0]}</h3>
                    <p class="chapter-number">Capítulo {chapter_num}</p>
                </div>
            </a>
"""

    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Index gerado com sucesso: {index_path}")
    return True
if __name__ == "__main__":
    base_dir = input("Digite o caminho absoluto da pasta que contém os capítulos: ").strip()
    if not os.path.isabs(base_dir):
        print("ERRO: O caminho deve ser absoluto.")
    elif not os.path.exists(base_dir):
        print("ERRO: Caminho informado não existe.")
    else:
        has_chapters = any("_capitulo_" in folder for folder in os.listdir(base_dir))
        if has_chapters:
            generate_index_html(base_dir)
        else:
            print("ERRO: Nenhuma pasta de capítulo encontrada no caminho informado.")
