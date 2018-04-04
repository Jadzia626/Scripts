#!/bin/bash

echo ""
echo "Running default Debian installs ..."
echo "****************************************************************************************************"
echo ""

if [ "$1" == "-x" ]; then

    echo "Skipping download of third party .deb packages ..."
    echo ""

else

    # Somewhere to store Downloads
    cd $HOME/Downloads

    # Chrome
    echo ""
    echo "Installing Google Chrome ..."
    echo "****************************************************************************************************"
    echo ""
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    dpkg -i google-chrome-stable_current_amd64.deb
    echo ""
    echo "****************************************************************************************************"

    # VSCode
    echo ""
    echo "Installing Visual Studio Code ..."
    echo "****************************************************************************************************"
    echo ""
    wget https://go.microsoft.com/fwlink/?LinkID=760868 -O code_latest_amd64.deb
    dpkg -i code_latest_amd64.deb
    echo ""
    echo "****************************************************************************************************"
    echo ""

    # Fix Dependencies
    apt -fy install
    echo ""
    echo "****************************************************************************************************"
    echo ""

    rm -v google-chrome-stable_current_amd64.deb
    rm -v code_latest_amd64.deb

fi

# Main Packages
echo ""
echo "Installing default packages ..."
echo "****************************************************************************************************"
echo ""
apt update
apt install -y \
    aptitude \
    apt-transport-https \
    automake \
    autotools-dev \
    bless \
    build-essential \
    calibre \
    cmake \
    curl \
    gcc \
    geany \
    geany-plugins \
    gfortran \
    gimp \
    git \
    gnome-shell-extension-dashtodock \
    gnome-shell-extension-pixelsaver \
    gnome-shell-extension-system-monitor \
    gnome-shell-extension-weather \
    g++ \
    inetutils-tools \
    inkscape \
    ipython \
    ipython3 \
    keepass2 \
    libboost-all-dev \
    libhdf5-dev \
    libhdf5-openmpi-dev \
    libopenmpi-dev \
    libreoffice-style-breeze \
    libssl-dev \
    lm-sensors \
    locate \
    meld \
    mutt \
    net-tools \
    nodejs \
    pandoc \
    par2 \
    pkg-config \
    python3 \
    python3-gi \
    python3-matplotlib \
    python3-numpy \
    python3-pytest \
    python-matplotlib \
    python-numpy \
    p7zip \
    rar \
    rsync \
    screen \
    secure-delete \
    smartmontools \
    system-config-printer \
    terminator \
    texlive-full \
    thunar \
    thunderbird \
    thunderbird-l10n-nb-no \
    typecatcher \
    unrar \
    vlc \
    zim

apt purge -y \
    cups-browsed

echo ""
echo "****************************************************************************************************"
echo ""

# Syncthing
if [ ! -f /etc/apt/sources.list.d/syncthing.list ]; then
    echo ""
    echo "Installing Syncthing ..."
    echo "****************************************************************************************************"
    echo ""
    curl -s https://syncthing.net/release-key.txt | sudo apt-key add -
    echo "deb https://apt.syncthing.net/ syncthing stable" | tee /etc/apt/sources.list.d/syncthing.list
    apt update
    apt install -y syncthing
    apt -f install
    systemctl enable syncthing@vkbo.service
    systemctl start syncthing@vkbo.service
    echo "****************************************************************************************************"
    echo ""
fi

# Spotify
if [ ! -f /etc/apt/sources.list.d/spotify.list ]; then
    echo ""
    echo "Installing Spotify ..."
    echo "****************************************************************************************************"
    echo ""
    apt install -y dirmngr
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0DF731E45CE24F27EEEB1450EFDC8610341D9410
    echo deb http://repository.spotify.com stable non-free | tee /etc/apt/sources.list.d/spotify.list
    apt update
    apt install -y spotify-client
    apt -f install
    echo "****************************************************************************************************"
    echo ""
fi

# NodeJS
if [ ! -f /etc/apt/sources.list.d/nodesource.list ]; then
    echo ""
    echo "Installing NodeJS ..."
    echo "****************************************************************************************************"
    echo ""
    curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
    apt update
    apt install -y nodejs
    echo "****************************************************************************************************"
    echo ""
fi
