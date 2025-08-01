
import ee
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class SatelliteDataProcessor:
    """Classe para processamento avançado de dados de satélite"""

    def __init__(self):
        self.initialize_earth_engine()

    def initialize_earth_engine(self):
        """Inicializa o Google Earth Engine com autenticação"""
        try:
            # Autenticação usando arquivo de serviço
            # ee.Authenticate()
            ee.Initialize()
            print("Google Earth Engine inicializado com sucesso!")
        except Exception as e:
            print(f"Erro ao inicializar GEE: {e}")

    def get_landsat_data(self, roi, start_date, end_date):
        """Obtém dados do Landsat 8/9"""
        collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                     .filterBounds(roi)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUD_COVER', 20)))

        def process_landsat(image):
            # Aplicar fatores de escala
            optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
            thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0)

            # Calcular NDWI com Landsat (Green = B3, NIR = B5)
            ndwi = optical_bands.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')

            # Calcular NDVI (NIR = B5, Red = B4)
            ndvi = optical_bands.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')

            return optical_bands.addBands([thermal_bands, ndwi, ndvi])

        return collection.map(process_landsat)

    def get_sentinel2_data(self, roi, start_date, end_date):
        """Obtém dados do Sentinel-2"""
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                     .filterBounds(roi)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

        def process_sentinel2(image):
            # Máscara de nuvens usando QA60
            cloud_mask = image.select('QA60').bitwiseAnd(1024).eq(0).And(
                        image.select('QA60').bitwiseAnd(2048).eq(0))

            # Aplicar máscara
            masked = image.updateMask(cloud_mask).multiply(0.0001)

            # Calcular NDWI (Green = B3, NIR = B8)
            ndwi = masked.normalizedDifference(['B3', 'B8']).rename('NDWI')

            # Calcular NDVI (NIR = B8, Red = B4)
            ndvi = masked.normalizedDifference(['B8', 'B4']).rename('NDVI')

            # Calcular NDMI (NIR = B8, SWIR = B11)
            ndmi = masked.normalizedDifference(['B8', 'B11']).rename('NDMI')

            return masked.addBands([ndwi, ndvi, ndmi])

        return collection.map(process_sentinel2)

    def calculate_evapotranspiration_sebal(self, image, roi):
        """Implementa modelo SEBAL simplificado para ET"""

        # Temperatura de superfície (assumindo Landsat)
        lst = image.select('ST_B10')  # Banda térmica Landsat

        # Albedo de superfície (simplificado)
        blue = image.select('SR_B2')
        green = image.select('SR_B3')
        red = image.select('SR_B4')
        nir = image.select('SR_B5')
        swir1 = image.select('SR_B6')
        swir2 = image.select('SR_B7')

        albedo = (blue.multiply(0.356).add(green.multiply(0.130))
                 .add(red.multiply(0.373)).add(nir.multiply(0.085))
                 .add(swir1.multiply(0.072)).add(swir2.multiply(-0.0018))
                 .subtract(0.0016)).rename('ALBEDO')

        # NDVI
        ndvi = image.select('NDVI')

        # Radiação líquida (simplificada)
        # Rn = Rs * (1 - albedo) - Rl_out
        rs_in = ee.Number(25)  # MJ/m²/day (valor estimado)
        rl_out = lst.multiply(0.01)  # Simplificação
        rn = rs_in.multiply(ee.Image(1).subtract(albedo)).subtract(rl_out).rename('RN')

        # Fluxo de calor do solo (G)
        g = rn.multiply(albedo.multiply(0.0038).add(0.0074)
                       .multiply(albedo).subtract(0.0018)
                       .multiply(albedo).add(0.0026)).rename('G')

        # Fluxo de calor sensível (H) - método simplificado
        # dT = diferença de temperatura
        dt = lst.subtract(lst.reduceRegion(
            reducer=ee.Reducer.percentile([10]),
            geometry=roi,
            scale=30
        ).values().get(0))

        # Resistência aerodinâmica (simplificada)
        rah = ee.Number(50)  # s/m

        # Densidade do ar e calor específico
        rho_cp = ee.Number(1200)  # J/m³/K

        h = dt.multiply(rho_cp).divide(rah).rename('H')

        # Evapotranspiração instantânea (mm/h)
        # ET = (Rn - G - H) / λ
        lambda_et = ee.Number(2.45)  # MJ/kg (calor latente de vaporização)
        et_inst = rn.subtract(g).subtract(h).divide(lambda_et).rename('ET_INST')

        # ET diária (assumindo 8 horas de evaporação ativa)
        et_daily = et_inst.multiply(8).rename('ET_DAILY')

        return image.addBands([albedo, rn, g, h, et_inst, et_daily])

    def export_time_series(self, collection, roi, start_date, end_date):
        """Exporta série temporal para análise"""

        def extract_values(image):
            # Reduzir região para obter valores médios
            stats = image.select(['NDWI', 'NDVI', 'ET_DAILY']).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=30,
                maxPixels=1e9
            )

            # Adicionar data
            date = image.date().format('YYYY-MM-dd')
            return ee.Feature(None, stats.set('date', date))

        # Mapear sobre a coleção
        time_series = collection.map(extract_values)

        # Converter para lista
        ts_list = time_series.getInfo()

        # Converter para DataFrame
        data = []
        for feature in ts_list['features']:
            props = feature['properties']
            if all(key in props for key in ['date', 'NDWI', 'NDVI']):
                data.append(props)

        return pd.DataFrame(data)

    def generate_report(self, df, roi_area_km2):
        """Gera relatório automatizado"""

        report = {
            "data_analise": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "area_estudo_km2": roi_area_km2,
            "periodo_analise": {
                "inicio": df['date'].min(),
                "fim": df['date'].max(),
                "total_dias": len(df)
            },
            "estatisticas": {
                "ndwi": {
                    "media": float(df['NDWI'].mean()),
                    "minimo": float(df['NDWI'].min()),
                    "maximo": float(df['NDWI'].max()),
                    "desvio_padrao": float(df['NDWI'].std())
                },
                "ndvi": {
                    "media": float(df['NDVI'].mean()),
                    "minimo": float(df['NDVI'].min()),
                    "maximo": float(df['NDVI'].max()),
                    "desvio_padrao": float(df['NDVI'].std())
                }
            }
        }

        # Adicionar ET se disponível
        if 'ET_DAILY' in df.columns:
            report["estatisticas"]["evapotranspiracao"] = {
                "media_mm_dia": float(df['ET_DAILY'].mean()),
                "total_mm_periodo": float(df['ET_DAILY'].sum()),
                "minimo": float(df['ET_DAILY'].min()),
                "maximo": float(df['ET_DAILY'].max())
            }

        return report

# Exemplo de uso
if __name__ == "__main__":
    # Inicializar processador
    processor = SatelliteDataProcessor()

    # Definir área de interesse (exemplo: Kennedy, Bahia)
    roi = ee.Geometry.Rectangle([-40.2, -11.1, -40.1, -11.0])

    # Definir período
    start_date = '2023-01-01'
    end_date = '2023-12-31'

    # Obter dados Sentinel-2
    s2_collection = processor.get_sentinel2_data(roi, start_date, end_date)

    # Exportar série temporal
    df = processor.export_time_series(s2_collection, roi, start_date, end_date)

    # Gerar relatório
    report = processor.generate_report(df, 100)  # 100 km²

    print("Processamento concluído!")
    print(f"Total de imagens processadas: {len(df)}")
    print(json.dumps(report, indent=2, ensure_ascii=False))
