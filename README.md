# README.md

# Sistema de Análise de Sazonalidade - Profarma

## 📊 Descrição

Aplicação web para análise de sazonalidade de vendas, desenvolvida para o Grupo Profarma. O sistema processa dados históricos de vendas, identifica e trata outliers estatisticamente, e calcula métricas de sazonalidade para apoio à tomada de decisão.

## 🚀 Funcionalidades

- **Upload de Dados**: Suporte para arquivos CSV e Excel
- **Tratamento Estatístico**: Detecção e tratamento de outliers usando z-score configurável
- **Análise de Sazonalidade**: 
  - Percentual de distribuição ao longo do ano
  - Taxa de crescimento mês a mês
- **Visualizações Interativas**: Gráficos e tabelas com filtros dinâmicos
- **Export de Dados**: Download em formato CSV e Excel
- **Memória de Cálculo**: Registro completo das análises estatísticas
- **Assistente Virtual**: Integração com SazIA para suporte ao usuário

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/profarma/sazonal-analytics.git
cd sazonal-analytics
