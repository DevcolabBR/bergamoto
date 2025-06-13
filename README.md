# Bergamoto - Sistema de Registro de Ponto Eletrônico

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python versão">
  <img src="https://img.shields.io/badge/SQLite-3.0-green.svg" alt="SQLite">
  <img src="https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow.svg" alt="Status">
  <img src="https://img.shields.io/badge/Licença-MIT-red.svg" alt="Licença">
</p>

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Recursos](#-recursos)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação e Configuração](#-instalação-e-configuração)
- [Como Usar](#-como-usar)
- [Módulos Principais](#-módulos-principais)
- [Requisitos Legais](#-requisitos-legais)
- [Contribuições](#-contribuições)

## 🔍 Sobre o Projeto

Bergamoto é um sistema completo de registro de ponto eletrônico desenvolvido para empresas que necessitam controlar a jornada de trabalho de seus colaboradores. O sistema oferece registro de entrada e saída, captura de foto para confirmação de identidade, cálculo automático de horas trabalhadas e diversas análises de períodos trabalhados.

O projeto foi desenvolvido com ênfase na segurança, facilidade de uso e conformidade com as normas brasileiras de controle de ponto eletrônico.

## 🚀 Recursos

- **Registro de Ponto com Foto**: Captura a imagem do colaborador no momento do registro para confirmação de identidade
- **Controle por PIN**: Identificação única por colaborador
- **Análise de Jornada**: Cálculo automático de horas trabalhadas, intervalos e extras
- **Interface Amigável**: Sistema GUI intuitivo para facilitar o uso
- **Relatórios Gerenciais**: Análise de faltas, atrasos e horas trabalhadas
- **Multiplataforma**: Versões para Linux e Windows
- **Banco de Dados Seguro**: Armazenamento centralizado de todos os registros

## 💻 Tecnologias Utilizadas

- **Python**: Linguagem principal
- **SQLite**: Banco de dados para armazenamento
- **OpenCV**: Para captura e processamento de imagens
- **Tkinter**: Interface gráfica com tema moderno
- **Pandas**: Análise de dados e geração de relatórios

## 📂 Estrutura do Projeto

```
bergamoto/
├── auxiliares/           # Scripts auxiliares para processamento de dados
│   ├── simulator.py      # Simulador de registros de ponto
│   ├── pre-analise.py    # Ferramentas de pré-análise de dados
│   └── ...
├── bot/                  # Módulos de automação e notificação
│   ├── notific-faltas.py # Sistema de notificação de faltas
│   └── ...
├── data/                 # Arquivos de dados
│   ├── bergamoto.db      # Banco de dados SQLite
│   └── people.csv        # Cadastro de colaboradores
├── feature-store/        # Módulos de análise avançada
│   ├── faltas.py         # Análise de faltas
│   └── tempo-trabalhado.py # Análise de horas trabalhadas
├── linux/                # Versão do sistema para Linux
│   └── main.py           # Aplicação principal (Linux)
├── win/                  # Versão do sistema para Windows
│   └── main-win.py       # Aplicação principal (Windows)
├── estrutura-project.py  # Script para gerar estrutura de arquivos
└── README.md             # Este arquivo
```

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.9 ou superior
- Pacotes necessários: tkinter, opencv-python, pillow, pandas, ttkthemes

### Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/bergamoto.git
   cd bergamoto
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o banco de dados:
   ```bash
   # No Linux
   python linux/create-people.py
   
   # No Windows
   python win/create-people-win.py
   ```

## 🖱️ Como Usar

### Executando o Sistema

#### No Linux:
```bash
python linux/main.py
```

#### No Windows:
```bash
python win/main-win.py
```

### Registrando Ponto

1. Digite seu PIN na tela inicial
2. Confirme sua identidade na tela seguinte
3. Aguarde a captura da foto (automática ou clique no botão)
4. Seu ponto será registrado automaticamente como entrada ou saída

### Encerrando o Sistema

Digite `----` (quatro hífens) na tela de PIN para encerrar o programa.

## 📊 Módulos Principais

### Sistema de Ponto (main.py)
Módulo principal que gerencia a interface de registro de ponto, captura de fotos e armazenamento de dados.

### Análise de Dados (feature-store/)
Ferramentas para análise de jornada de trabalho, detecção de faltas e cálculo de horas extras.

### Notificações (bot/)
Sistema de alerta para faltas, atrasos ou outros eventos relevantes.

## 📜 Requisitos Legais

No Brasil, sistemas de ponto eletrônico devem estar em conformidade com:
- Portaria 671/2021 do Ministério do Trabalho
- Normas técnicas do Inmetro

Este sistema foi desenvolvido considerando estes requisitos, mas recomenda-se verificar a conformidade com a legislação atual antes da implantação em ambiente de produção.

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

Desenvolvido por DevcolabBR © 2025
