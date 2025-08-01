
import streamlit as st
import ee
import geemap.foliumap as geemap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import requests
import json
from io import BytesIO
import base64

# Configuração da página Streamlit
st.set_page_config(
    page_title="Sistema de Monitoramento de Evapotranspiração - NDWI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4682B4;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .sidebar-info {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4682B4;
    }
</style>
""", unsafe_allow_html=True)

class EVETMonitoringSystem:
  def initialize_ee(self):
    """Inicializa o Google Earth Engine"""
    try:
        # NOVO CÓDIGO - Usando Streamlit Secrets
        import json
        sa_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT_JSON"])
        credentials = ee.ServiceAccountCredentials(sa_info["client_email"], json.dumps(sa_info))
        ee.Initialize(credentials)
    except KeyError:
        st.error("❌ Credenciais GEE não encontradas. Configure os Secrets do Streamlit.")
        st.stop()
    except Exception as e:
    st.error(f"Erro GEE completo: {e}")
    st.stop()

    def calculate_ndwi(self, image):
        """Calcula o NDWI (Normalized Difference Water Index)"""
        # NDWI = (GREEN - NIR) / (GREEN + NIR)
        green = image.select('B3')  # Banda verde Sentinel-2
        nir = image.select('B8')    # Banda NIR Sentinel-2
        ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI')
        return image.addBands(ndwi)

    def calculate_ndvi(self, image):
        """Calcula o NDVI (Normalized Difference Vegetation Index)"""
        # NDVI = (NIR - RED) / (NIR + RED)
        nir = image.select('B8')    # Banda NIR
        red = image.select('B4')    # Banda vermelha
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
        return image.addBands(ndvi)

    def estimate_evapotranspiration(self, image, ndwi, ndvi, temp=None):
        """Estima evapotranspiração baseada em NDWI, NDVI e outros parâmetros"""
        # Modelo simplificado de ET baseado em índices espectrais
        # ET = f(NDVI, NDWI, temperatura, radiação)

        # Fator de vegetação baseado em NDVI
        vegetation_factor = ndvi.multiply(1.2).add(0.1)

        # Fator de água baseado em NDWI
        water_factor = ndwi.multiply(0.8).add(1.0)

        # ET simplificada (mm/dia)
        et_simple = vegetation_factor.multiply(water_factor).multiply(3.5).rename('ET_daily')

        return image.addBands([et_simple, vegetation_factor.rename('VEG_FACTOR'), 
                              water_factor.rename('WATER_FACTOR')])

    def get_satellite_data(self, roi, start_date, end_date):
        """Obtém dados de satélite Sentinel-2"""
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                     .filterBounds(roi)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                     .sort('system:time_start'))

        def process_image(image):
            # Máscara de nuvens
            cloud_mask = image.select('QA60').bitwiseAnd(1024).eq(0).And(
                        image.select('QA60').bitwiseAnd(2048).eq(0))

            # Aplicar máscara e calcular índices
            masked = image.updateMask(cloud_mask)
            with_ndwi = self.calculate_ndwi(masked)
            with_ndvi = self.calculate_ndvi(with_ndwi)
            with_et = self.estimate_evapotranspiration(with_ndvi, 
                                                     with_ndvi.select('NDWI'), 
                                                     with_ndvi.select('NDVI'))

            return with_et

        processed_collection = collection.map(process_image)
        return processed_collection

    def create_time_series(self, collection, roi):
        """Cria série temporal dos índices"""
        def extract_values(image):
            stats = image.select(['NDWI', 'NDVI', 'ET_daily']).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=30,
                maxPixels=1e9
            )
            return ee.Feature(None, stats.set('date', image.date().format('YYYY-MM-dd')))

        time_series = collection.map(extract_values)
        return time_series

    def download_time_series_data(self, time_series):
        """Baixa dados da série temporal"""
        try:
            data = time_series.getInfo()
            records = []

            for feature in data['features']:
                props = feature['properties']
                if all(k in props for k in ['date', 'NDWI', 'NDVI', 'ET_daily']):
                    records.append({
                        'Data': props['date'],
                        'NDWI': props['NDWI'],
                        'NDVI': props['NDVI'],
                        'ET_diaria': props['ET_daily']
                    })

            return pd.DataFrame(records)
        except Exception as e:
            st.error(f"Erro ao baixar dados: {e}")
            return pd.DataFrame()

def main():
    # Título principal
    st.markdown('<h1 class="main-header">🌱 Sistema de Monitoramento de Evapotranspiração - NDWI</h1>', 
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.markdown("### 📊 Parâmetros de Monitoramento")
        st.markdown("Configure os parâmetros para análise da evapotranspiração</div>", 
                   unsafe_allow_html=True)

        # Seleção de coordenadas (exemplo para Kennedy, Bahia)
        lat = st.number_input("Latitude", value=-11.0833, format="%.4f")
        lon = st.number_input("Longitude", value=-40.1667, format="%.4f")
        buffer_size = st.slider("Tamanho da área (km)", 1, 10, 3)

        # Seleção de datas
        end_date = st.date_input("Data final", datetime.now().date())
        start_date = st.date_input("Data inicial", 
                                 end_date - timedelta(days=90))

        # Botão para processar
        process_button = st.button("🚀 Processar Dados", type="primary")

    # Inicializar sistema
    system = EVETMonitoringSystem()

    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs(["📍 Área de Estudo", "📈 Análise Temporal", 
                                      "🗺️ Mapas Interativos", "📊 Relatórios"])

    with tab1:
        st.markdown('<h2 class="sub-header">Definição da Área de Estudo</h2>', 
                   unsafe_allow_html=True)

        # Criar ROI
        roi = ee.Geometry.Point([lon, lat]).buffer(buffer_size * 1000)

        # Mapa interativo
        m = geemap.Map(center=[lat, lon], zoom=12)
        m.addLayer(roi, {'color': 'red'}, 'Área de Estudo')
        m.add_basemap('SATELLITE')

        col1, col2 = st.columns([3, 1])
        with col1:
            m.to_streamlit(height=500)

        with col2:
            st.markdown("### 📍 Informações da Área")
            st.metric("Latitude", f"{lat:.4f}°")
            st.metric("Longitude", f"{lon:.4f}°")
            st.metric("Área", f"{(buffer_size*2)**2:.1f} km²")
            st.metric("Período", f"{(end_date - start_date).days} dias")

    with tab2:
        st.markdown('<h2 class="sub-header">Análise da Série Temporal</h2>', 
                   unsafe_allow_html=True)

        if process_button:
            with st.spinner("Processando dados de satélite..."):
                try:
                    # Obter dados
                    collection = system.get_satellite_data(roi, 
                                                         start_date.strftime('%Y-%m-%d'),
                                                         end_date.strftime('%Y-%m-%d'))

                    # Criar série temporal
                    time_series = system.create_time_series(collection, roi)

                    # Baixar dados
                    df = system.download_time_series_data(time_series)

                    if not df.empty:
                        # Converter data
                        df['Data'] = pd.to_datetime(df['Data'])
                        df = df.sort_values('Data')

                        # Armazenar no session state
                        st.session_state['df'] = df

                        st.success(f"✅ Processados {len(df)} pontos de dados!")
                    else:
                        st.warning("Nenhum dado encontrado para o período selecionado.")

                except Exception as e:
                    st.error(f"Erro no processamento: {e}")

        # Mostrar gráficos se dados disponíveis
        if 'df' in st.session_state:
            df = st.session_state['df']

            # Métricas resumo
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("NDWI Médio", f"{df['NDWI'].mean():.3f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("NDVI Médio", f"{df['NDVI'].mean():.3f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("ET Média", f"{df['ET_diaria'].mean():.2f} mm/dia")
                st.markdown('</div>', unsafe_allow_html=True)

            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Pontos de Dados", len(df))
                st.markdown('</div>', unsafe_allow_html=True)

            # Gráfico de série temporal
            fig = go.Figure()

            fig.add_trace(go.Scatter(x=df['Data'], y=df['NDWI'], 
                                   name='NDWI', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df['Data'], y=df['NDVI'], 
                                   name='NDVI', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=df['Data'], y=df['ET_diaria']/10, 
                                   name='ET (mm/dia ÷ 10)', line=dict(color='red')))

            fig.update_layout(title="Série Temporal - NDWI, NDVI e Evapotranspiração",
                            xaxis_title="Data",
                            yaxis_title="Valor do Índice",
                            height=500)

            st.plotly_chart(fig, use_container_width=True)

            # Correlação entre índices
            col1, col2 = st.columns(2)

            with col1:
                fig_corr = px.scatter(df, x='NDWI', y='ET_diaria', 
                                    title="Correlação NDWI vs ET",
                                    trendline="ols")
                st.plotly_chart(fig_corr, use_container_width=True)

            with col2:
                fig_corr2 = px.scatter(df, x='NDVI', y='ET_diaria', 
                                     title="Correlação NDVI vs ET",
                                     trendline="ols")
                st.plotly_chart(fig_corr2, use_container_width=True)

    with tab3:
        st.markdown('<h2 class="sub-header">Mapas de Índices Espectrais</h2>', 
                   unsafe_allow_html=True)

        if 'df' in st.session_state and not st.session_state['df'].empty:
            # Seletor de data para visualização
            dates_available = pd.to_datetime(st.session_state['df']['Data']).dt.date.unique()
            selected_date = st.selectbox("Selecione uma data para visualização:", 
                                       dates_available)

            if selected_date:
                # Criar mapa com índices
                map_viz = geemap.Map(center=[lat, lon], zoom=11)

                # Obter imagem da data selecionada
                target_date = selected_date.strftime('%Y-%m-%d')
                next_date = (selected_date + timedelta(days=1)).strftime('%Y-%m-%d')

                try:
                    collection = system.get_satellite_data(roi, target_date, next_date)
                    image = collection.first()

                    # Parâmetros de visualização
                    ndwi_params = {'min': -0.5, 'max': 0.5, 'palette': ['red', 'yellow', 'green', 'blue']}
                    ndvi_params = {'min': -0.2, 'max': 0.8, 'palette': ['brown', 'yellow', 'green', 'darkgreen']}
                    et_params = {'min': 0, 'max': 8, 'palette': ['white', 'lightblue', 'blue', 'darkblue']}

                    # Adicionar camadas
                    map_viz.addLayer(image.select('NDWI'), ndwi_params, 'NDWI')
                    map_viz.addLayer(image.select('NDVI'), ndvi_params, 'NDVI')
                    map_viz.addLayer(image.select('ET_daily'), et_params, 'ET Diária (mm)')
                    map_viz.addLayer(roi, {'color': 'red'}, 'ROI')

                    map_viz.to_streamlit(height=600)

                except Exception as e:
                    st.error(f"Erro ao criar mapa: {e}")
        else:
            st.info("Execute o processamento de dados na aba 'Análise Temporal' primeiro.")

    with tab4:
        st.markdown('<h2 class="sub-header">Relatórios e Download</h2>', 
                   unsafe_allow_html=True)

        if 'df' in st.session_state and not st.session_state['df'].empty:
            df = st.session_state['df']

            # Estatísticas descritivas
            st.subheader("📊 Estatísticas Descritivas")
            stats = df[['NDWI', 'NDVI', 'ET_diaria']].describe()
            st.dataframe(stats)

            # Análise de tendências
            st.subheader("📈 Análise de Tendências")

            # Calcular correlações
            corr_matrix = df[['NDWI', 'NDVI', 'ET_diaria']].corr()
            fig_heatmap = px.imshow(corr_matrix, 
                                  title="Matriz de Correlação",
                                  aspect="auto",
                                  color_continuous_scale="RdBu")
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # Download dos dados
            st.subheader("💾 Download dos Dados")

            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Baixar dados como CSV",
                data=csv,
                file_name=f"evapotranspiracao_ndwi_{start_date}_{end_date}.csv",
                mime="text/csv"
            )

            # Resumo executivo
            st.subheader("📋 Resumo Executivo")

            avg_et = df['ET_diaria'].mean()
            avg_ndwi = df['NDWI'].mean()
            avg_ndvi = df['NDVI'].mean()

            st.markdown(f"""
            **Período de Análise:** {start_date} a {end_date}

            **Resultados Principais:**
            - Evapotranspiração média: {avg_et:.2f} mm/dia
            - NDWI médio: {avg_ndwi:.3f} (indicador de conteúdo de água)
            - NDVI médio: {avg_ndvi:.3f} (indicador de vigor vegetativo)

            **Interpretação:**
            - NDWI próximo de 0: Equilíbrio entre vegetação e água
            - NDVI > 0.3: Vegetação saudável
            - ET entre 2-6 mm/dia: Faixa típica para culturas
            """)
        else:
            st.info("Execute o processamento de dados primeiro para gerar relatórios.")

if __name__ == "__main__":
    main()
