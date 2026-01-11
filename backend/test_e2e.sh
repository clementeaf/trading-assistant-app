#!/bin/bash

# Test E2E para todos los endpoints del Trading Assistant
# Requiere: servidor corriendo en localhost:8000

BASE_URL="http://localhost:8000/api/market-briefing"

echo "🧪 Running E2E Tests for Trading Assistant API"
echo "=============================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

test_endpoint() {
    local name=$1
    local url=$2
    shift 2
    local expected_fields=("$@")
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${BLUE}[$TOTAL_TESTS]${NC} Testing ${YELLOW}$name${NC}..."
    echo "    URL: $url"
    
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        # Validar campos esperados
        all_fields_present=true
        missing_fields=()
        
        for field in "${expected_fields[@]}"; do
            if ! echo "$body" | jq -e ".$field" > /dev/null 2>&1; then
                all_fields_present=false
                missing_fields+=("$field")
            fi
        done
        
        if $all_fields_present; then
            echo -e "    ${GREEN}✓ PASS${NC} (HTTP 200, all fields present)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo -e "    ${RED}✗ FAIL${NC} (HTTP 200, missing fields: ${missing_fields[*]})"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        echo -e "    ${RED}✗ FAIL${NC} (HTTP $http_code)"
        if [ "$http_code" != "000" ]; then
            echo "$body" | jq -C '.' 2>/dev/null || echo "$body"
        else
            echo "    Error: Cannot connect to server. Is it running on $BASE_URL?"
        fi
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
    echo ""
}

# Verificar que el servidor está corriendo
echo -n "Checking if server is running... "
if curl -s "$BASE_URL/../docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Error: Server is not responding. Start it with:"
    echo "  cd backend && uvicorn app.main:app --reload"
    exit 1
fi
echo ""

# Tests por endpoint
echo "Running tests..."
echo "----------------"

test_endpoint \
    "High Impact News" \
    "$BASE_URL/high-impact-news" \
    "has_high_impact_news" "count" "events" "summary" "instrument" "geopolitical_risk"

test_endpoint \
    "Event Schedule" \
    "$BASE_URL/event-schedule?include_gold_impact=true" \
    "total_events" "usd_events_count" "events" "summary"

test_endpoint \
    "Yesterday Analysis" \
    "$BASE_URL/yesterday-analysis?instrument=XAUUSD" \
    "instrument" "date" "close_price" "sessions" "summary"

test_endpoint \
    "DXY-Bond Alignment" \
    "$BASE_URL/dxy-bond-alignment?include_gold_correlation=true" \
    "dxy_symbol" "bond_symbol" "alignment" "market_bias" "gold_dxy_correlation"

test_endpoint \
    "Trading Mode" \
    "$BASE_URL/trading-mode?instrument=XAUUSD" \
    "mode" "confidence" "reasoning" "factors" "operational_levels"

test_endpoint \
    "Trading Recommendation" \
    "$BASE_URL/trading-recommendation?instrument=XAUUSD" \
    "disclaimer" "direction" "confidence" "risk_reward_details" "confidence_breakdown"

test_endpoint \
    "Technical Analysis" \
    "$BASE_URL/technical-analysis?instrument=XAUUSD" \
    "instrument" "analysis_date"

test_endpoint \
    "Psychological Levels" \
    "$BASE_URL/psychological-levels?instrument=XAUUSD" \
    "instrument" "current_price" "levels"

# Resumen
echo ""
echo "=============================================="
echo "Test Summary"
echo "=============================================="
echo -e "Total:  $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Check the output above for details.${NC}"
    exit 1
fi
