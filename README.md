# Bergamoto - Sistema de Registro de Ponto Eletrônico v2.0

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python versão">
  <img src="https://img.shields.io/badge/SQLite-3.0-green.svg" alt="SQLite">
  <img src="https://img.shields.io/badge/Status-Refatorado-brightgreen.svg" alt="Status">
  <img src="https://img.shields.io/badge/Licença-MIT-red.svg" alt="Licença">
  <img src="https://img.shields.io/badge/Versão-2.0.0-orange.svg" alt="Versão">
</p>

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [O Que Mudou na v2.0](#-o-que-mudou-na-v20)
- [Recursos](#-recursos)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Nova Estrutura do Projeto](#-nova-estrutura-do-projeto)
- [Instalação Rápida](#-instalação-rápida)
- [Uso da Aplicação](#-uso-da-aplicação)
- [Documentação Técnica](#-documentação-técnica)
- [Migração da v1.x](#-migração-da-v1x)
- [Contribuições](#-contribuições)

## 🔍 Sobre o Projeto

Bergamoto é um sistema completo de registro de ponto eletrônico desenvolvido para empresas que necessitam controlar a jornada de trabalho de seus colaboradores. O sistema oferece registro de entrada e saída, captura de foto para confirmação de identidade, cálculo automático de horas trabalhadas e diversas análises de períodos trabalhados.

**Versão 2.0:** Completamente refatorado com arquitetura modular, melhor organização de código, sistema de configuração centralizado e suporte multiplataforma unificado.

## 🚀 O Que Mudou na v2.0

### ✅ Melhorias Implementadas

- **🏗️ Arquitetura Modular**: Código organizado em módulos bem definidos
- **🔧 Configuração Centralizada**: Sistema de configuração unificado com suporte a .env
- **🗄️ Banco de Dados Padronizado**: Schema consistente com migrações automáticas
- **📱 Interface Unificada**: Uma única aplicação que funciona em Linux, Windows e macOS
- **📊 Sistema de Monitoramento**: Health checks e logging estruturado
- **🔄 Código Reutilizável**: Eliminação de duplicação entre versões de SO
- **⚙️ Setup Automatizado**: Script de configuração inicial simplificado

### �️ Problemas Resolvidos

- ~~Caminhos hardcoded específicos do desenvolvedor~~
- ~~Duplicação de código entre `linux/main.py` e `win/main-win.py`~~
- ~~Inconsistências no schema do banco de dados~~
- ~~Falta de sistema de configuração~~
- ~~Estrutura de projeto desorganizada~~

## 🚀 Recursos

- **Registro de Ponto com Foto**: Captura automática de imagem para confirmação
- **Controle por PIN**: Identificação única e segura por colaborador
- **Interface Moderna**: UI responsiva com temas personalizáveis
- **Banco de Dados Robusto**: SQLite com integridade e backups automáticos
- **Relatórios Gerenciais**: Análise de horas, faltas e produtividade
- **Multiplataforma**: Funciona nativamente em Linux, Windows e macOS
- **Sistema de Logs**: Monitoramento completo e debugging facilitado
- **Migração Automática**: Atualização seamless de versões anteriores

## 💻 Tecnologias Utilizadas

### Obrigatórias
- **Python 3.9+**: Linguagem principal
- **SQLite 3**: Banco de dados embutido
- **Tkinter**: Interface gráfica (incluído no Python)

### Opcionais (Funcionalidade Completa)
- **OpenCV**: Captura e processamento de imagens
- **Pillow**: Manipulação de imagens
- **ttkthemes**: Temas modernos para interface
- **pandas**: Análise de dados avançada

## 📂 Nova Estrutura do Projeto

```
bergamoto/
├── main.py                    # 🎯 Ponto de entrada único
├── setup.py                   # ⚙️ Script de configuração
├── requirements.txt           # 📦 Dependências
├── README.md                 # 📖 Esta documentação
│
├── src/bergamoto/            # 🏗️ Código principal
│   ├── core/                 # 💼 Lógica de negócio
│   │   ├── employee.py       # 👤 Gestão de funcionários
│   │   ├── timesheet.py      # ⏰ Registro de ponto
│   │   └── main_app.py       # 🖥️ Aplicação principal
│   │
│   ├── database/             # 🗄️ Camada de dados
│   │   ├── manager.py        # 🔧 Gerenciador do BD
│   │   ├── models.py         # 📋 Modelos de dados
│   │   └── schemas.py        # 🏛️ Estrutura do BD
│   │
│   └── utils/                # 🛠️ Utilitários
│       ├── logger.py         # 📝 Sistema de logs
│       ├── camera.py         # 📷 Captura de fotos
│       └── monitoring.py     # 📊 Health checks
│
├── config/                   # ⚙️ Configurações
│   ├── settings.py           # 🔧 Configurações centrais
│   └── .env.example          # 📄 Exemplo de ambiente
│
├── scripts/                  # 🔄 Scripts utilitários
│   └── migrate_database.py   # 🔄 Migração do BD
│
├── analysis/                 # 📈 Análises (antigo feature-store)
├── data/                     # 💾 Dados da aplicação
├── logs/                     # 📋 Arquivos de log
└── tests/                    # 🧪 Testes automatizados
```

## ⚡ Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/DevcolabBR/bergamoto.git
cd bergamoto
```

### 2. Execute o Setup Automático
```bash
python setup.py
```

O script irá:
- ✅ Criar diretórios necessários
- ✅ Configurar arquivo de ambiente
- ✅ Instalar dependências (opcional)
- ✅ Migrar/criar banco de dados
- ✅ Criar funcionários de exemplo (opcional)

### 3. Execute a Aplicação
```bash
python main.py
```

## 🖱️ Uso da Aplicação

### Primeiro Acesso
1. Execute `python setup.py` para configuração inicial
2. Aceite criar funcionários de exemplo quando perguntado
3. Execute `python main.py` para iniciar

### Registrando Ponto
1. Digite seu PIN na tela inicial
2. Confirme sua identidade
3. Aguarde a captura automática da foto (3 segundos)
4. Seu ponto será registrado automaticamente

### Funcionalidades Especiais
- **Encerrar Sistema**: Digite `----` no campo PIN
- **Ver Logs**: `tail -f logs/bergamoto.log`
- **Health Check**: Execute diagnósticos do sistema

## � Documentação Técnica

### Arquitetura

O sistema segue uma arquitetura em camadas:

```
┌─────────────────┐
│   Interface     │  ← main.py, UI components
├─────────────────┤
│   Core Logic    │  ← Business rules, services
├─────────────────┤
│   Database      │  ← Data layer, models
├─────────────────┤
│   Utils         │  ← Logging, monitoring, tools
└─────────────────┘
```

### APIs Principais

#### EmployeeService
```python
from bergamoto.core import EmployeeService

# Criar funcionário
service.create_employee("1234", "João Silva", "vendas", "Maria Santos")

# Buscar por PIN
employee = service.get_employee_by_pin("1234")
```

#### TimesheetService
```python
from bergamoto.core import TimesheetService

# Registrar ponto
success, message = service.clock_in(employee)

# Obter resumo do dia
summary = service.get_daily_summary(employee.id, "26-09-2025")
```

### Configuração

Arquivo `.env`:
```env
DB_NAME=bergamoto.db
UI_THEME=equilux
UI_FULLSCREEN=true
LOG_LEVEL=INFO
```

## � Migração da v1.x

Se você tem uma versão anterior instalada:

1. **Backup dos dados existentes**
2. **Execute o novo setup**: `python setup.py`
3. **A migração é automática**: Dados serão preservados
4. **Arquivos antigos podem ser removidos**:
   - `linux/main.py`
   - `win/main-win.py`
   - Scripts duplicados em `auxiliares/`

## 📊 Análises e Relatórios

Os scripts de análise foram mantidos no diretório `analysis/` para compatibilidade. Eles serão integrados à interface principal em versões futuras.

### Análises Disponíveis:
- **Horas trabalhadas por funcionário**
- **Análise de faltas e atrasos**
- **Variações de horário**
- **Produtividade por setor**

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest

# Executar testes
python -m pytest tests/

# Com cobertura
python -m pytest --cov=src tests/
```

## 🤝 Contribuições

Contribuições são bem-vindas! A nova arquitetura facilita muito o desenvolvimento.

### Processo:
1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Faça suas alterações
4. Execute os testes: `python -m pytest`
5. Commit: `git commit -m 'Adiciona nova funcionalidade'`
6. Push: `git push origin feature/nova-funcionalidade`
7. Abra um Pull Request

### Áreas que Precisam de Ajuda:
- 🧪 Testes automatizados
- 📱 Interface mobile/web
- 🌐 API REST
- 📊 Dashboard de análises
- 🔐 Autenticação avançada

## 📜 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🏆 Créditos

- **Desenvolvimento Original**: DevcolabBR
- **Refatoração v2.0**: GitHub Copilot + DevcolabBR
- **Comunidade**: Contribuidores do projeto

---

**📧 Contato**: [DevcolabBR](https://github.com/DevcolabBR)  
**🐛 Issues**: [GitHub Issues](https://github.com/DevcolabBR/bergamoto/issues)  
**📖 Wiki**: [Documentação Completa](https://github.com/DevcolabBR/bergamoto/wiki)
