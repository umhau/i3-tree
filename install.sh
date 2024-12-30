
#!/bin/bash

# Set installation paths
INSTALL_DIR="/opt/i3tree"
VENV_DIR="$INSTALL_DIR/venv"

# Install system dependencies
sudo xbps-install -Sy python3-pip python3-devel python3-evdev

# Create directory for i3tree
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR

# Create and activate virtual environment
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install pip packages in the virtual environment
pip install i3ipc asyncio PyQt5 asyncqt screeninfo pynput

# Install i3tree.py to the installation directory
cp i3tree.py $INSTALL_DIR/

# Create and install the wrapper script
sudo tee /usr/local/bin/i3tree << EOF
#!/bin/bash
source $VENV_DIR/bin/activate
exec python $INSTALL_DIR/i3tree.py "\$@"
EOF

# Make the wrapper executable
sudo chmod +x /usr/local/bin/i3tree

# Add venv to PATH (add this to your .bashrc or .zshrc)
echo "export PATH=\"$VENV_DIR/bin:\$PATH\"" >> ~/.bashrc
