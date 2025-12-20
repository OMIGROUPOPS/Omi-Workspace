#!/bin/bash

echo "Creating OMI Edge file structure..."

# Edge client routes
mkdir -p "app/(edge)/edge"
mkdir -p "app/(edge)/edge/login"
mkdir -p "app/(edge)/edge/signup"
mkdir -p "app/(edge)/edge/pricing"
mkdir -p "app/(edge)/portal"
mkdir -p "app/(edge)/portal/sports/\[sport\]"
mkdir -p "app/(edge)/portal/sports/game/\[id\]"
mkdir -p "app/(edge)/portal/events/\[category\]"
mkdir -p "app/(edge)/portal/events/market/\[id\]"
mkdir -p "app/(edge)/portal/edge-cards"
mkdir -p "app/(edge)/portal/settings/subscription"

# Edge internal
mkdir -p "app/(edge-internal)/edge-console"

# API routes
mkdir -p "app/api/edge/auth"
mkdir -p "app/api/edge/sports/\[sport\]"
mkdir -p "app/api/edge/games/\[id\]"
mkdir -p "app/api/edge/events/\[category\]"
mkdir -p "app/api/edge/markets/\[id\]"
mkdir -p "app/api/edge/edge-cards"
mkdir -p "app/api/edge/assistant"
mkdir -p "app/api/edge/webhooks"
mkdir -p "app/api/edge/internal"

# Components
mkdir -p "components/edge"

# Lib
mkdir -p "lib/edge/db"
mkdir -p "lib/edge/api"
mkdir -p "lib/edge/pillars/modifiers"
mkdir -p "lib/edge/engine"
mkdir -p "lib/edge/assistant"
mkdir -p "lib/edge/utils"

# Types
mkdir -p "types/edge"

echo "✅ Done! OMI Edge folders created."