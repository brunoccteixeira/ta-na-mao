# PWA Icons - Tá na Mão

Este diretório deve conter os ícones do PWA em diferentes tamanhos.

## Tamanhos necessários

- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png
- apple-touch-icon.png (180x180)

## Como gerar os ícones

### Opção 1: Usando o arquivo icon.svg

O arquivo `icon.svg` contém o ícone base. Você pode convertê-lo usando:

**Via CLI (ImageMagick):**
```bash
for size in 72 96 128 144 152 192 384 512; do
  convert icon.svg -resize ${size}x${size} icon-${size}x${size}.png
done
convert icon.svg -resize 180x180 apple-touch-icon.png
```

**Via Figma/Sketch:**
1. Importe o icon.svg
2. Exporte em cada tamanho necessário

### Opção 2: Geradores online

- [RealFaviconGenerator](https://realfavicongenerator.net/)
- [PWA Asset Generator](https://tools.crawlink.com/tools/pwa-icon-generator/)

## Especificações

- Formato: PNG
- Fundo: Gradiente verde (#10b981 para #059669)
- Ícone: Branco
- Maskable: Sim (área segura respeitada)
