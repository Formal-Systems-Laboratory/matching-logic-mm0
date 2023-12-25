#! /bin/sh

git submodule update --init

# Install Metamath Zero
cd mm0/mm0-c
./make.sh
cd ../mm0-rs
cargo build --release
cd ../..

# Install Python requirements
poetry install

# Select the right Maude binary to use depending on the platform
if [ $# -gt 0 ] && [ "$1" = "macOS" ]
  then
    cp maude/maude.darwin64 maude/maude
  else
    cp maude/maude.linux64 maude/maude
fi
