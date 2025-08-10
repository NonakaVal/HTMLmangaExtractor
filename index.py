import os

def generate_index_html(base_dir):
    index_path = os.path.join(base_dir, "index.html")
    chapters = []
    
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and "_capitulo_" in item:
            if os.path.exists(os.path.join(item_path, "leitor.html")):
                chapter_name = item.replace("_", " ").replace("capitulo", "Capítulo")
                
                # Caminho relativo da capa (sempre page_002.png se existir)
                cover_rel = os.path.join(item, "pages", "page_02.png")
                cover_abs = os.path.join(base_dir, cover_rel)

                if not os.path.exists(cover_abs):
                    # Pega segunda imagem disponível
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
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }}
        .manga-title {{
            font-size: 2.5em;
            margin: 0;
            color: #222;
        }}
        .chapters-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 25px;
            padding: 20px;
        }}
        .chapter-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
        }}
        .chapter-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        .chapter-cover {{
            width: 100%;
            height: 280px;
            object-fit: cover;
            border-bottom: 1px solid #eee;
        }}
        .chapter-info {{
            padding: 15px;
            text-align: center;
        }}
        .chapter-name {{
            margin: 0;
            font-weight: 600;
            font-size: 1.1em;
        }}
        .no-cover {{
            height: 280px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #eee;
            color: #777;
        }}
        @media (max-width: 600px) {{
            .chapters-container {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="manga-title">{os.path.basename(base_dir)}</h1>
    </div>
    
    <div class="chapters-container">
"""

    for chapter in chapters:
        cover_html = f'<img src="{chapter["cover"]}" class="chapter-cover" alt="Capa">' if chapter["cover"] else '<div class="no-cover">Sem capa</div>'
        html_content += f"""
        <a href="{chapter['leitor']}" class="chapter-card">
            {cover_html}
            <div class="chapter-info">
                <h3 class="chapter-name">{chapter['name']}</h3>
            </div>
        </a>
"""

    html_content += """
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
