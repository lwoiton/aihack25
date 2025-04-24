#!/bin/bash
# improved-install.sh - Sets up the EUROGATE AI Agent environment and dependencies

echo "======================================================="
echo "EUROGATE AI Agent - Environment Setup"
echo "======================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Step 1: Check for Conda installation
echo "Checking for Conda installation..."
if command_exists conda; then
    echo "✓ Conda is installed."
else
    echo "✗ Conda is not installed."
    echo "Installing Miniconda..."
    
    # Determine OS and download appropriate Miniconda installer
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if [[ $(uname -m) == "arm64" ]]; then
            # M1/M2 Mac
            wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -O miniconda.sh
        else
            # Intel Mac
            wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh
        fi
    else
        echo "Unsupported operating system. Please install Miniconda manually from:"
        echo "https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    # Install Miniconda
    bash miniconda.sh -b -p $HOME/miniconda
    rm miniconda.sh
    
    # Add conda to PATH for the current session
    export PATH="$HOME/miniconda/bin:$PATH"
    
    # Initialize conda for bash
    $HOME/miniconda/bin/conda init bash
    
    echo "✓ Miniconda installed successfully."
    echo "Please restart your terminal after this script completes."
    
    # Make conda command available in current script
    source $HOME/miniconda/etc/profile.d/conda.sh
fi

# Step 2: Create or update the Conda environment
echo -e "\nSetting up Conda environment..."
ENV_NAME="eurogate-ai"

# Ensure we're using conda from the correct path
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"

# Check if the environment already exists
if conda info --envs | grep -q $ENV_NAME; then
    echo "Environment '$ENV_NAME' already exists."
    conda activate $ENV_NAME
    
    # Get timestamp of requirements.txt
    REQ_TIMESTAMP=$(stat -c %Y requirements.txt 2>/dev/null || stat -f %m requirements.txt 2>/dev/null)
    
    # Create a marker file to track last update if it doesn't exist
    if [ ! -f ".env_last_updated" ]; then
        echo "0" > .env_last_updated
    fi
    
    LAST_UPDATE=$(cat .env_last_updated)
    
    # Check if requirements.txt is newer than our last update
    if [ "$REQ_TIMESTAMP" -gt "$LAST_UPDATE" ]; then
        echo "Requirements file has been updated. Refreshing dependencies..."
        # Update the timestamp
        echo "$REQ_TIMESTAMP" > .env_last_updated
    else
        echo "Dependencies are up to date."
        # Skip the installation steps
        SKIP_INSTALL=true
    fi
else
    echo "Creating new environment '$ENV_NAME'..."
    conda create -y -n $ENV_NAME python=3.12
    conda activate $ENV_NAME
    
    # Create a marker file to track last update
    echo "0" > .env_last_updated
fi

# Ensure conda environment is activated
CURRENT_ENV=$(conda info --envs | grep '*' | awk '{print $1}')
if [ "$CURRENT_ENV" != "$ENV_NAME" ]; then
    echo "Failed to activate conda environment. Attempting again..."
    conda deactivate  # Just in case
    conda activate $ENV_NAME
fi

if [ "$SKIP_INSTALL" != "true" ]; then
    # Step 3: Install UV in the Conda environment if not present
    echo -e "\nChecking for UV package manager..."
    if ! command_exists uv; then
        echo "Installing UV package manager..."
        pip install uv
        echo "✓ UV installed successfully."
    else
        echo "✓ UV is already installed."
    fi

    # Step 4: Install required dependencies using UV
    echo -e "\nInstalling project dependencies..."

    # Install crucial packages with conda for better binary compatibility
    echo "Installing core scientific packages with conda..."
    conda install -y pandas numpy scipy

    # Install remaining packages with UV
    echo "Installing remaining dependencies with UV..."
    uv pip install -r requirements.txt

    # Check if requests is installed properly
    echo -e "\nVerifying requests installation..."
    if python -c "import requests" &>/dev/null; then
        echo "✓ Requests package is installed properly."
    else
        echo "⚠️ Requests package not found. Installing directly..."
        pip install requests
        if python -c "import requests" &>/dev/null; then
            echo "✓ Requests package installed successfully."
        else
            echo "✗ Failed to install requests package. Please check your Python environment."
        fi
    fi

    # Update the timestamp after successful installation
    REQ_TIMESTAMP=$(stat -c %Y requirements.txt 2>/dev/null || stat -f %m requirements.txt 2>/dev/null)
    echo "$REQ_TIMESTAMP" > .env_last_updated
fi

# Step 5: Set up environment variables
echo -e "\nSetting up environment configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.template .env
    echo "✓ Created .env file. Please edit it to add your API keys."
else
    echo "✓ .env file already exists."
fi

# Step 6: Create convenience scripts
echo -e "\nCreating convenience scripts..."

# Activation script
cat > activate.sh << EOL
#!/bin/bash
# Activates the Conda environment for the EUROGATE AI Agent
source \$(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME
echo "EUROGATE AI Agent environment activated."
EOL
chmod +x activate.sh

# Run script
cat > run.sh << EOL
#!/bin/bash
# Runs the EUROGATE AI Agent API server
source \$(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME
python -m app.main
EOL
chmod +x run.sh

echo -e "\n======================================================="
echo "✓ Installation complete!"
echo "======================================================="
echo
echo "To activate the environment manually: source ./activate.sh"
echo "To run the application: ./run.sh"
echo
echo "If this is your first time installing, please restart your"
echo "terminal to ensure Conda is properly initialized."
echo "======================================================="

# Automatically activate the environment
source ./activate.sh