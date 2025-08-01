
# 🌱 Sistema de Monitoramento de Evapotranspiração - NDWI

Sistema web interativo para monitoramento de evapotranspiração em áreas agrícolas usando dados de satélite e índices espectrais.

## ⚡ Início Rápido

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar Google Earth Engine
earthengine authenticate

# 3. Executar aplicação
streamlit run app.py
```

## 🎯 Características

- 🛰️ **Dados de Satélite**: Sentinel-2 e Landsat 8/9
- 📊 **Índices Espectrais**: NDWI, NDVI, NDMI
- 💧 **Evapotranspiração**: Modelos SEBAL e estimativas baseadas em índices
- 🗺️ **Mapas Interativos**: Visualização de índices em alta resolução
- 📈 **Análise Temporal**: Séries temporais e correlações
- 📄 **Relatórios**: Estatísticas e downloads de dados

## 🏗️ Estrutura do Projeto

```
evapotranspiracao-ndwi/
├── app.py                 # Aplicação principal Streamlit
├── data_processor.py      # Processamento avançado de dados
├── requirements.txt       # Dependências Python
├── config_gee.json       # Configuração Google Earth Engine
├── README.md             # Este arquivo
└── docs/
    └── documentation.md   # Documentação completa
```

## 📖 Documentação Completa

Veja [documentation.md](docs/documentation.md) para:
- Guia detalhado de instalação
- Metodologia científica
- Como personalizar o sistema
- Solução de problemas
- Referências acadêmicas

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📧 Contato

Para dúvidas técnicas ou sugestões, abra uma issue no repositório.

## 📜 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.
