import os
import re
import time
import json
import requests
from PIL import Image
from tqdm import tqdm
from io import BytesIO
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

def sanitize_filename(name):
    name = re.sub(r"[\\/:*?\"<>|]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    name = re.sub(r"_+", "_", name)
    return name[:100]

class MangaImageDownloader:
    def __init__(self, chapter_url, output_dir, driver):
        self.chapter_url = chapter_url
        self.output_dir = output_dir
        self.pages_dir = os.path.join(output_dir, "pages")
        self.image_urls = []
        self.driver = driver
        os.makedirs(self.pages_dir, exist_ok=True)

    def fetch_image_urls(self):
        try:
            self.driver.get(self.chapter_url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.chapter-image-container img"))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.image_urls = self._extract_image_urls(soup)

            if not self.image_urls:
                print("[AVISO] Nenhuma imagem encontrada.")
                return False

            print(f"[INFO] Encontradas {len(self.image_urls)} imagens no capítulo.")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao buscar imagens: {e}")
            return False

    def _extract_image_urls(self, soup):
        image_urls = []
        for img in soup.select('div.chapter-image-container img'):
            srcset = img.get('srcset') or img.get('data-srcset')
            if srcset:
                highest_res_url = self._get_highest_resolution_url(srcset)
                image_urls.append(highest_res_url)
            else:
                img_url = img.get('src') or img.get('data-src')
                if img_url:
                    image_urls.append(img_url)
        return image_urls

    def _get_highest_resolution_url(self, srcset):
        srcset_urls = [s.strip().split() for s in srcset.split(',')]
        return sorted(srcset_urls, key=lambda x: int(x[1].replace('w', '')), reverse=True)[0][0]

    def download_image(self, url, filename):
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': self.chapter_url})
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            if img.mode == "P":
                img = img.convert("RGB")

            img_format = 'PNG' if img.mode in ('RGBA', 'LA') else 'JPEG'
            img_path = os.path.join(self.pages_dir, filename)
            img.save(img_path, format=img_format, optimize=True)
            return img_path
        except Exception as e:
            print(f"[ERRO] Falha ao baixar {url}: {e}")
            return None

    def download_all_pages(self):
        success = self.fetch_image_urls()
        if not success:
            return False
        
        print(f"[INFO] Baixando {len(self.image_urls)} imagens para {self.pages_dir}")
        for i, url in enumerate(tqdm(self.image_urls, desc="Baixando Imagens", unit="imagem")):
            self.download_image(url, f"page_{i + 1:03d}.png")
        
        print(f"[SUCESSO] Todas as imagens foram salvas em: {self.pages_dir}")
        return True

    def generate_html_reader(self):
        page_files = sorted(
            [f for f in os.listdir(self.pages_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
            key=lambda x: int(''.join(filter(str.isdigit, x)))
        )
        
        if not page_files:
            print(f"[ERRO] Nenhuma imagem encontrada na pasta {self.pages_dir}")
            return False
        
        chapter_name = os.path.basename(self.output_dir)
        manga_name = chapter_name.split('_capitulo_')[0].replace('_', ' ').title()
        chapter_num = chapter_name.split('_capitulo_')[-1]
        index_path = os.path.relpath(os.path.join(self.output_dir, "..", "index.html"), start=self.output_dir)
        
        html_content = f"""<!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{manga_name} - Capítulo {chapter_num}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: #0e0e0e;
            color: #ccc;
            font-family: Arial, sans-serif;
        }}
        .header {{
            background-color: rgba(0,0,0,0.7);
            padding: 5px 10px;
            font-size: 0.9rem;
            position: sticky;
            top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header a {{
            color: #999;
            text-decoration: none;
            font-size: 0.8rem;
        }}
        .page-container {{
            max-width: 1000px;
            margin: auto;
            padding: 0;
        }}
        .page {{
            margin: 0;
        }}
        .manga-page {{
            width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }}
        .page-number {{
            font-size: 0.7rem;
            color: #555;
            text-align: center;
            margin: 5px 0;
        }}
    </style>
    </head>
    <body>

    <div class="header">
        <a href="{index_path}">← Voltar</a>
        <div>{manga_name} - Cap. {chapter_num}</div>
    </div>

    <div class="page-container">
    """

        for i, page_file in enumerate(page_files, 1):
            page_path = os.path.join("pages", page_file)
            html_content += f"""
        <div class="page">
            <img class="manga-page" src="{page_path}" alt="Página {i}" loading="lazy">
        </div>
        <div class="page-number">Página {i}</div>
    """

        html_content += """
    </div>
    </body>
    </html>
    """
        
        output_html = os.path.join(self.output_dir, "leitor.html")
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[HTML] Gerado com sucesso: {output_html}")
        return True


def generate_html_reader(self):
    # Pegar todas as imagens da pasta pages, em ordem
    page_files = sorted(
        [f for f in os.listdir(self.pages_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
        key=lambda x: int(''.join(filter(str.isdigit, x)))
    )
    
    if not page_files:
        print(f"[ERRO] Nenhuma imagem encontrada na pasta {self.pages_dir}")
        return False
    
    # Extrair nome do mangá e capítulo do nome da pasta
    chapter_name = os.path.basename(self.output_dir)
    manga_name = chapter_name.split('_capitulo_')[0].replace('_', ' ').title()
    chapter_num = chapter_name.split('_capitulo_')[-1]
    
    # Caminho relativo para o index.html (um nível acima)
    index_path = os.path.relpath(os.path.join(self.output_dir, "..", "index.html"), start=self.output_dir)
    
    # Gerar o conteúdo HTML
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{manga_name} - Capítulo {chapter_num}</title>
    <style>
        :root {{
            --bg-color: #1a1a1a;
            --header-color: #000;
            --text-color: #e0e0e0;
            --secondary-text: #aaa;
            --button-color: #333;
            --button-hover: #555;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.5;
        }}
        
        .header {{
            width: 100%;
            background-color: var(--header-color);
            padding: 15px 0;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }}
        
        .header-content {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 15px;
            position: relative;
        }}
        
        .title {{
            margin: 0;
            font-size: 1.3rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .chapter-info {{
            margin-top: 5px;
            font-size: 0.9rem;
            color: var(--secondary-text);
        }}
        
        .back-button {{
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            background-color: var(--button-color);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
            font-size: 0.8rem;
            text-decoration: none;
        }}
        
        .back-button:hover {{
            background-color: var(--button-hover);
        }}
        
        .page-container {{
            width: 100%;
            max-width: 900px;
            margin: 20px auto;
            padding: 0 10px;
        }}
        
        .page {{
            margin-bottom: 20px;
        }}
        
        .page-number {{
            color: var(--secondary-text);
            font-size: 0.8rem;
            margin-bottom: 5px;
            padding-left: 5px;
        }}
        
        .manga-page {{
            width: 100%;
            height: auto;
            display: block;
            border-radius: 3px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
        }}
        
        @media (max-width: 600px) {{
            .title {{
                font-size: 1.1rem;
                padding-left: 40px;
                padding-right: 10px;
            }}
            
            .chapter-info {{
                padding-left: 40px;
                padding-right: 10px;
            }}
            
            .back-button {{
                padding: 4px 8px;
                font-size: 0.7rem;
            }}
            
            .page-container {{
                padding: 0 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <a href="{index_path}" class="back-button">← Voltar</a>
            <h1 class="title">{manga_name}</h1>
            <div class="chapter-info">Capítulo {chapter_num}</div>
        </div>
    </div>
    
    <div class="page-container">
"""

    # Adicionar cada página ao HTML
    for i, page_file in enumerate(page_files, 1):
        page_path = os.path.join("pages", page_file)
        html_content += f"""
        <div class="page">
            <div class="page-number">Página {i}</div>
            <img class="manga-page" src="{page_path}" alt="Página {i}" loading="lazy">
        </div>
"""

    # Fechar o HTML
    html_content += """
    </div>
</body>
</html>
"""
    
    # Escrever o arquivo HTML
    output_html = os.path.join(self.output_dir, "leitor.html")
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[HTML] Gerado com sucesso: {output_html}")
    return True

def get_next_chapter(driver):
    try:
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.next-chapter-btn"))
        )
        next_url = next_btn.get_attribute('href')
        if next_url and next_url != driver.current_url:
            print(f"[INFO] Próximo capítulo encontrado: {next_url}")
            return next_url
    except:
        print("[AVISO] Botão próximo não encontrado, tentando método alternativo...")
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            next_link = soup.find('a', class_='next-chapter-btn') or \
                       soup.find('a', string=re.compile(r'próximo|next', re.IGNORECASE))
            if next_link and next_link.get('href'):
                next_url = next_link['href']
                if next_url != driver.current_url:
                    print(f"[INFO] Próximo capítulo encontrado via HTML: {next_url}")
                    return next_url
        except Exception as e:
            print(f"[ERRO] Método alternativo também falhou: {e}")
    print("[AVISO] Não foi possível encontrar o link para o próximo capítulo")
    return None

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0')
    return webdriver.Chrome(options=options)

def main():
    default_dir = "/home/val/Documentos/Mangas"
    user_input = input(f"Digite o caminho de saída (pressione Enter para usar o padrão: {default_dir}): ").strip()
    output_dir = user_input if user_input else default_dir
    os.makedirs(output_dir, exist_ok=True)

    num_chapters = 8 # ou input se quiser customizar
    driver = setup_driver()

    start_url = input("Digite o link do primeiro capítulo: ")
    current_url = start_url

    for chapter_num in range(1, num_chapters + 1):
        try:
            print(f"\n=== PROCESSANDO CAPÍTULO {chapter_num} ===")
            driver.get(current_url)
            title = driver.title.split('|')[0].strip()
            safe_title = sanitize_filename(title)
            
            # Cria um subdiretório para o capítulo
            chapter_dir = os.path.join(output_dir, f"{safe_title}_capitulo_{chapter_num}")
            os.makedirs(chapter_dir, exist_ok=True)
            
            downloader = MangaImageDownloader(
                chapter_url=current_url,
                output_dir=chapter_dir,
                driver=driver
            )

            # Baixa todas as imagens
            success = downloader.download_all_pages()
            if not success:
                print(f"[AVISO] Falha ao baixar imagens do capítulo {chapter_num}")
                continue

            # Gera o HTML do leitor
            html_success = downloader.generate_html_reader()
            if not html_success:
                print(f"[AVISO] Falha ao gerar HTML para o capítulo {chapter_num}")

            current_url = get_next_chapter(driver)
            if not current_url:
                print("[FIM] Sem próximos capítulos.")
                break

            time.sleep(2)

        except Exception as e:
            print(f"[ERRO CRÍTICO] Capítulo {chapter_num}: {e}")
            break

    driver.quit()
    print("\n✅ Processo concluído! Todos os capítulos foram baixados e os leitores HTML gerados.")

if __name__ == "__main__":
    main()
