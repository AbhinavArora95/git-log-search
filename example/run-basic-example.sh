#! /bin/bash

# 1. Prepare embeddings for the repository (this could take a while)
./message.py prepare ./

# 2. Search for commits
./message.py search "When did we add the LICENSE?"
