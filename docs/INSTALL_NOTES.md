# Installation Guide

>**NOTE:**<br> 
>This is the complete setup guide for this Dotfiles repository on macOS. If you would like to use the import/export functionality of this repository, start here! 
>
>Your mileage may vary and proceed at your own risk! If you do not know your way around the tools below and fully understand the commands listed here, it is probably best to pair up with someone. 


## Table of Contents

- [Prerequisites](#prerequisites)
- [Basic CLI Setup](#basic-cli-setup)
- [Development Environment](#development-environment)
- [Connect to Github or Gitlab](#connect-to-github-or-gitlab)
- [Repository Installation](#repository-installation)
- [Post-Installation](#post-installation)


&nbsp;
## Prerequisites

- macOS 10.15+ (Catalina or later)
- Admin privileges for system changes
- Internet connection for downloads

## Basic CLI Setup

### 1. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Essential Tools

```bash
# Update Homebrew
brew upgrade

# Install modern bash and zsh
brew install bash zsh

# Add new bash to allowed shells
echo '/opt/homebrew/bin/bash' | sudo tee -a /etc/shells

# Install Git
brew install git

# Install core development tools
xcode-select --install
```

### 3. Configure Terminal

**Install iTerm2:**
```bash
brew install --cask iterm2
```



## Development Environment

### Programming Languages

**Python with uv:**
If you already have a python installation, feel free to ignore this and skip this step. 
Installing python can be infamously complex and varied, depending on your personal preferences. This is one, modern, up-to-date way to run python... 

```bash
# Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python versions
uv python install 3.12.4 3.11.8 3.10.14
uv python pin 3.12.4  # Set default
```



## Connect to Github or Gitlab

### Generate Personal Access Token for GitLab
---



### Generate SSH Key for GitHub
---
```bash
# Generate new ED25519 key
ssh-keygen -t ed25519 -C "your.email@example.com" -f ~/.ssh/github_ed25519 -N ""

# Create SSH config
cat << EOF > ~/.ssh/config
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/github_ed25519
EOF

# Start SSH agent and add key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/github_ed25519

# Copy public key to clipboard
pbcopy < ~/.ssh/github_ed25519.pub
```

### Add Key to GitHub

1. Go to GitHub.com → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste the key from clipboard
4. Test connection: `ssh -T git@github.com`




## Repository Installation

### Clone Repository

```bash
# Create Projects directory
mkdir -p ~/Projects

# Clone mise-en-place
git clone https://github.com/andisab/mise-en-place.git ~/Projects/mise-en-place
cd ~/Projects/mise-en-place
```

### Configure Dotfiles

```bash
# Review and edit dotfiles.conf
vim dotfiles.conf

# Test configuration
source install.sh
test_config

# Validate configuration
validate_config
```


### Deploy Configurations

```bash
# Sync repository configs to system
sync_dotfiles_from_git

# Inspect output and verify files are in place... 
```

Verify installation:
```bash
# Will differ depending on dotfiles.conf configuration. E.g.:
source ~/.profile

alias
```


## Next Steps
- Customize configurations in `dotfiles.conf` and repeat as needed
- [IDE Tools & Setup](IDE.md)
- [LLM Context Enrichment](LLM.md)
- [CLI Applications Setup](SETUP.md)
- [Additional Tools & Packages](TOOLS.md)
