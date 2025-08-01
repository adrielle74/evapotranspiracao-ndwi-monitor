
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import SatelliteDataProcessor
import ee
import pandas as pd

class TestSatelliteDataProcessor(unittest.TestCase):

    def setUp(self):
        """Configurar testes"""
        try:
            ee.Initialize()
            self.processor = SatelliteDataProcessor()
            self.test_roi = ee.Geometry.Point([-40.1667, -11.0833]).buffer(1000)
        except Exception as e:
            self.skipTest(f"Não foi possível inicializar GEE: {e}")

    def test_processor_initialization(self):
        """Testar inicialização do processador"""
        self.assertIsInstance(self.processor, SatelliteDataProcessor)

    def test_sentinel2_data_access(self):
        """Testar acesso a dados Sentinel-2"""
        collection = self.processor.get_sentinel2_data(
            self.test_roi, '2023-01-01', '2023-01-31'
        )
        self.assertIsInstance(collection, ee.ImageCollection)

    def test_landsat_data_access(self):
        """Testar acesso a dados Landsat"""
        collection = self.processor.get_landsat_data(
            self.test_roi, '2023-01-01', '2023-01-31'
        )
        self.assertIsInstance(collection, ee.ImageCollection)

    def test_report_generation(self):
        """Testar geração de relatório"""
        # Criar DataFrame de teste
        test_data = {
            'date': ['2023-01-01', '2023-01-02'],
            'NDWI': [0.1, 0.2],
            'NDVI': [0.3, 0.4],
            'ET_DAILY': [2.5, 3.0]
        }
        df = pd.DataFrame(test_data)

        report = self.processor.generate_report(df, 100)

        self.assertIn('data_analise', report)
        self.assertIn('estatisticas', report)
        self.assertEqual(report['area_estudo_km2'], 100)

if __name__ == '__main__':
    unittest.main()
