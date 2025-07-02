#!/bin/bash

echo "=== Instalador do Stripe Extractor ==="
echo "Este script vai configurar o ambiente para o Stripe Extractor"

# Garantir que o script seja executado pelo bash
if [ "$BASH_VERSION" = "" ]; then
    echo "Este script precisa ser executado com bash. Execute-o assim: bash setup.sh"
    exit 1
fi

# Verificar se o sistema é Linux, macOS ou Windows (via WSL/Git Bash)
if [ "$(uname -s)" = "Linux" ]; then
    SYSTEM="Linux"
    echo "Sistema detectado: Linux"
elif [ "$(uname -s)" = "Darwin" ]; then
    SYSTEM="macOS"
    echo "Sistema detectado: macOS"
elif [ "$OSTYPE" = "msys" ] || [ "$OSTYPE" = "cygwin" ]; then
    SYSTEM="Windows"
    echo "Sistema detectado: Windows (Git Bash/WSL)"
else
    echo "Sistema operacional não suportado: $(uname -s)"
    exit 1
fi

# Verificar e instalar Python se necessário
if ! command -v python3 > /dev/null 2>&1; then
    echo "Python3 não encontrado. Tentando instalar..."
    
    if [ "$SYSTEM" = "Linux" ]; then
        # Para distribuições baseadas em Debian/Ubuntu
        if command -v apt > /dev/null 2>&1; then
            sudo apt update
            sudo apt install -y python3 python3-pip
        # Para distribuições baseadas em RHEL/CentOS/Fedora
        elif command -v dnf > /dev/null 2>&1; then
            sudo dnf install -y python3 python3-pip
        elif command -v yum > /dev/null 2>&1; then
            sudo yum install -y python3 python3-pip
        else
            echo "Não foi possível identificar o gerenciador de pacotes. Por favor, instale Python3 manualmente."
            exit 1
        fi
    elif [ "$SYSTEM" = "macOS" ]; then
        # Para macOS, recomendamos usar Homebrew
        if ! command -v brew > /dev/null 2>&1; then
            echo "Homebrew não encontrado. Por favor, instale-o primeiro:"
            echo "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        else
            brew install python3
        fi
    elif [ "$SYSTEM" = "Windows" ]; then
        echo "Para Windows, recomendamos baixar e instalar Python do site oficial:"
        echo "https://www.python.org/downloads/"
        echo "Certifique-se de marcar a opção 'Add Python to PATH' durante a instalação."
        exit 1
    fi
fi

echo "Verificando a versão do Python..."
python3 --version

# Verificar e instalar pip se necessário
if ! command -v pip3 > /dev/null 2>&1; then
    echo "pip3 não encontrado. Tentando instalar..."
    
    if [ "$SYSTEM" = "Linux" ]; then
        if command -v apt > /dev/null 2>&1; then
            sudo apt install -y python3-pip
        elif command -v dnf > /dev/null 2>&1; then
            sudo dnf install -y python3-pip
        elif command -v yum > /dev/null 2>&1; then
            sudo yum install -y python3-pip
        fi
    elif [ "$SYSTEM" = "macOS" ]; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py
        rm get-pip.py
    fi
fi

echo "Verificando a versão do pip..."
pip3 --version

# Criar ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
if [ "$SYSTEM" = "Windows" ]; then
    # Use source ou . dependendo da shell
    . venv/Scripts/activate || source venv/Scripts/activate
else
    . venv/bin/activate || source venv/bin/activate
fi

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt || pip3 install -r requirements.txt

# Verificar arquivo .env
if [ ! -f .env ]; then
    echo "Criando arquivo .env..."
    echo "STRIPE_API_KEY=seu_api_key_aqui" > .env
    echo "IMPORTANTE: Edite o arquivo .env e adicione sua chave API do Stripe."
else
    echo "Arquivo .env já existe."
fi

# Criar diretório de saída
mkdir -p outputs

# Desativa o ambiente virtual para evitar confusão
deactivate 2>/dev/null || true

echo "=== Instalação concluída! ==="
echo "Para usar o Stripe Extractor:"
echo ""
echo "1. Ative o ambiente virtual com um destes comandos:"
echo "   - No Linux/macOS: source venv/bin/activate"
echo "   - No Windows CMD: venv\Scripts\activate.bat"
echo "   - No Windows PowerShell: .\venv\Scripts\Activate.ps1"
echo "   - No Git Bash/WSL: source venv/Scripts/activate"
echo ""
echo "2. Execute o script: python stripe_extractor.py"
echo ""
echo "IMPORTANTE: Você DEVE ativar o ambiente virtual antes de executar o script,"
echo "           caso contrário, receberá erro de módulo não encontrado."

echo ""
echo "Para executar tudo em uma única linha (Linux/macOS):"
echo "source venv/bin/activate && python stripe_extractor.py"
