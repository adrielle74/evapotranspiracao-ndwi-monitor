
# Sistema de Monitoramento de Evapotranspiração através de NDWI

## 📋 Visão Geral

Este sistema foi desenvolvido para monitorar a evapotranspiração em áreas agrícolas utilizando o Índice de Diferença Normalizada de Água (NDWI) através de dados de satélite. O sistema integra:

- **Google Earth Engine** para acesso a dados de satélite
- **Streamlit** para interface web interativa
- **Algoritmos de processamento** para cálculo de índices espectrais
- **Modelos de evapotranspiração** baseados em sensoriamento remoto

## 🚀 Funcionalidades Principais

### 1. Processamento de Dados Satelitais
- Acesso a imagens Sentinel-2 e Landsat 8/9
- Cálculo automático de NDWI, NDVI e NDMI
- Filtragem de nuvens e correções atmosféricas
- Processamento em lote para séries temporais

### 2. Cálculo de Evapotranspiração
- Modelo SEBAL simplificado
- Estimativas baseadas em índices espectrais
- Correlações entre NDWI e perda de água
- Mapas de ET em alta resolução (10-30m)

### 3. Interface Web Interativa
- Seleção de área de estudo via mapa
- Configuração de períodos de análise
- Visualização de séries temporais
- Mapas interativos com diferentes índices
- Download de dados e relatórios

### 4. Análises Estatísticas
- Correlações entre índices
- Tendências temporais
- Estatísticas descritivas
- Matriz de correlação
- Relatórios automatizados

## 🛠️ Instalação e Configuração

### Pré-requisitos
```bash
# Python 3.8 ou superior
python --version

# Git para controle de versão
git --version
```

### 1. Clonar/Criar o Projeto
```bash
# Criar diretório do projeto
mkdir evapotranspiracao-ndwi
cd evapotranspiracao-ndwi

# Copiar os arquivos criados
# app.py, requirements.txt, config_gee.json, data_processor.py
```

### 2. Configurar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
# Instalar pacotes Python
pip install -r requirements.txt

# Verificar instalação
pip list
```

### 4. Configurar Google Earth Engine

#### Opção A: Autenticação via Browser (Recomendado para desenvolvimento)
```bash
# Instalar earthengine-api
pip install earthengine-api

# Executar autenticação
earthengine authenticate

# Inicializar (executar uma vez)
python -c "import ee; ee.Initialize()"
```

#### Opção B: Service Account (Recomendado para produção)
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione existente
3. Ative a API do Earth Engine
4. Crie uma Service Account:
   - IAM & Admin > Service Accounts
   - Create Service Account
   - Atribua papel "Earth Engine Resource Viewer"
5. Gere uma chave JSON:
   - Actions > Create Key > JSON
6. Baixe o arquivo e substitua `config_gee.json`
7. Configure a variável de ambiente:
```bash
# Windows
set GOOGLE_APPLICATION_CREDENTIALS=config_gee.json

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS=config_gee.json
```

### 5. Executar a Aplicação
```bash
# Executar aplicação Streamlit
streamlit run app.py

# A aplicação será aberta em http://localhost:8501
```

## 📊 Como Usar o Sistema

### 1. Configuração Inicial
1. Abra a aplicação no navegador
2. Na barra lateral, configure:
   - **Latitude/Longitude**: Coordenadas da área de interesse
   - **Buffer**: Tamanho da área de estudo (km)
   - **Datas**: Período de análise

### 2. Processamento de Dados
1. Vá para a aba "Análise Temporal"
2. Clique em "🚀 Processar Dados"
3. Aguarde o processamento (pode levar alguns minutos)
4. Visualize as métricas e gráficos gerados

### 3. Análise de Mapas
1. Acesse a aba "Mapas Interativos"
2. Selecione uma data específica
3. Visualize os mapas de NDWI, NDVI e ET
4. Use as camadas para comparar índices

### 4. Relatórios
1. Na aba "Relatórios e Download"
2. Visualize estatísticas descritivas
3. Analise correlações entre índices
4. Faça download dos dados em CSV

## 🔬 Metodologia Científica

### Cálculo do NDWI
```
NDWI = (Verde - NIR) / (Verde + NIR)
```
- **Verde**: Banda 3 (Sentinel-2) ou Banda 3 (Landsat)
- **NIR**: Banda 8 (Sentinel-2) ou Banda 5 (Landsat)
- **Interpretação**:
  - NDWI > 0: Maior conteúdo de água
  - NDWI < 0: Menor conteúdo de água

### Estimativa de Evapotranspiração
O sistema utiliza uma abordagem multi-índice:

1. **Fator de Vegetação**: Baseado no NDVI
   ```
   FV = (NDVI × 1.2) + 0.1
   ```

2. **Fator de Água**: Baseado no NDWI
   ```
   FA = (NDWI × 0.8) + 1.0
   ```

3. **ET Estimada**:
   ```
   ET = FV × FA × 3.5 mm/dia
   ```

### Modelo SEBAL (Avançado)
Para análises mais precisas, o sistema implementa o modelo SEBAL:

1. **Balanço de Energia**:
   ```
   Rn = G + H + λET
   ```
   - Rn: Radiação líquida
   - G: Fluxo de calor do solo
   - H: Fluxo de calor sensível
   - λET: Fluxo de calor latente (evapotranspiração)

2. **Temperatura de Superfície**: Banda térmica do Landsat
3. **Albedo**: Combinação ponderada das bandas ópticas
4. **Resistência Aerodinâmica**: Baseada em características da superfície

## 📈 Interpretação dos Resultados

### NDWI (Normalized Difference Water Index)
- **-1 a -0.3**: Vegetação densa, solo seco
- **-0.3 a 0**: Vegetação moderada
- **0 a 0.3**: Solo úmido, vegetação esparsa
- **0.3 a 1**: Corpos d'água, solo saturado

### NDVI (Normalized Difference Vegetation Index)
- **< 0**: Água, nuvens, neve
- **0 a 0.1**: Solo nu, rocha
- **0.1 a 0.3**: Vegetação esparsa
- **0.3 a 0.7**: Vegetação moderada a densa
- **> 0.7**: Vegetação muito densa

### Evapotranspiração (mm/dia)
- **0-2**: ET baixa (período seco, vegetação estressada)
- **2-4**: ET moderada (condições normais)
- **4-6**: ET alta (vegetação ativa, boa disponibilidade hídrica)
- **> 6**: ET muito alta (irrigação, período chuvoso)

## 🔧 Personalização e Extensões

### Adicionar Novos Índices
```python
def calculate_custom_index(image):
    # Exemplo: Índice de Estresse Hídrico
    swir1 = image.select('B11')  # SWIR1 Sentinel-2
    nir = image.select('B8')     # NIR Sentinel-2

    wsi = swir1.divide(nir).rename('WSI')
    return image.addBands(wsi)
```

### Integrar Dados Meteorológicos
```python
# Adicionar dados de temperatura e precipitação
def add_weather_data(collection, roi):
    weather = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR')

    def add_weather(image):
        date = image.date()
        weather_img = weather.filterDate(date, date.advance(1, 'day')).first()

        temp = weather_img.select('temperature_2m').rename('TEMP')
        precip = weather_img.select('total_precipitation_sum').rename('PRECIP')

        return image.addBands([temp, precip])

    return collection.map(add_weather)
```

### Adicionar Novos Sensores
```python
def get_modis_data(roi, start_date, end_date):
    """Integrar dados MODIS para análises de longo prazo"""
    collection = (ee.ImageCollection('MODIS/061/MOD13Q1')
                 .filterBounds(roi)
                 .filterDate(start_date, end_date))

    def process_modis(image):
        ndvi = image.select('NDVI').multiply(0.0001)
        return image.addBands(ndvi.rename('NDVI_MODIS'))

    return collection.map(process_modis)
```

## 🐛 Solução de Problemas

### Erro de Autenticação GEE
```
Error: Please authenticate to Earth Engine
```
**Solução**:
```bash
earthengine authenticate
```

### Erro de Memória
```
Error: Computation timed out
```
**Solução**:
- Reduza o tamanho da área de estudo
- Diminua o período de análise
- Aumente a escala de processamento (scale=60 em vez de 30)

### Erro de Dependências
```
ModuleNotFoundError: No module named 'ee'
```
**Solução**:
```bash
pip install earthengine-api geemap
```

### Imagens Sem Dados
**Problema**: Gráficos vazios ou valores NaN
**Soluções**:
- Verificar cobertura de nuvens
- Ajustar filtros de qualidade
- Expandir período de análise
- Verificar coordenadas da área

## 📚 Referências Científicas

1. **NDWI**: Gao, B. C. (1996). "NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space"

2. **SEBAL**: Bastiaanssen, W. G. M. (1998). "Remote sensing in water resources management: the state of the art"

3. **Evapotranspiração**: Allen, R. G. (1998). "Crop evapotranspiration-Guidelines for computing crop water requirements"

4. **Google Earth Engine**: Gorelick, N. (2017). "Google Earth Engine: Planetary-scale geospatial analysis for everyone"

## 📧 Suporte e Contribuições

Para dúvidas, sugestões ou contribuições:
- Abra uma issue no repositório
- Envie pull requests com melhorias
- Consulte a documentação oficial do GEE

## 📄 Licença

Este projeto está licenciado sob MIT License - veja o arquivo LICENSE para detalhes.
