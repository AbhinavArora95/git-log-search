#! /bin/bash

# 1. Prepare embeddings for the repository (this could take a while)
./message.py prepare ./ -p openai -m text-embedding-3-small

# 2. Search for commits
./message.py search "When did we add the LICENSE?" -p openai -m text-embedding-3-small -s -lp openai -lm gpt-4.1-nano

