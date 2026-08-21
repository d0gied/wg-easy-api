#!/bin/bash

tmp_errors_file=$(mktemp)

shopt -s lastpipe

auth="$WG_EASY_USERNAME:$WG_EASY_PASSWORD"
base_url=$WG_EASY_URL/api

# count_errors=0

echo_error() {
  echo "❌" >>"$tmp_errors_file"
  echo "❌" "$@" >&2
}

echo_success() {
  echo "✅" "$@"
}

run_curl() {
  method=$1
  url=$2
  shift 2
  local response
  response=$(
    curl -s -w "%{http_code}" -u "$auth" -X "$method" "$base_url/$url" "$@"
  )
  local http_status_code=${response: -3}
  local body_json=${response%???}
  if [ "$http_status_code" -ne 200 ]; then
    echo_error "CURL FAILED: $method $url (http status code: $http_status_code)"
    return "$http_status_code"
  fi
  echo "$body_json"
  return 0
}

check_key_value() {
  local json_input
  local value
  local title=$1
  local key=$2
  local intended_result=$3
  json_input=$(cat)
  value=$(echo "$json_input" | jq -r ".$key")
  if [ $? -ne 0 ]; then
    echo_error "$title: could not parse key '$key'"
  elif [ "$value" = "$intended_result" ]; then
    echo_success "$title: $key == $intended_result"
  else
    echo_error "$title: $key == $value != $intended_result"
  fi
}

check_success() {
  check_key_value "$1" "success" "true"
}

check_enabled() {
  check_key_value "$1" "enabled" "$2"
}

get_client() {
  client_id=$1
  run_curl GET "client/$client_id"
}

run_curl GET client >/dev/null

init_name="initName"

client_id=$(
  run_curl POST client \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$init_name\", \"expiresAt\": null}" |
    jq -r '.clientId'
)

client=$(get_client "$client_id")

echo "$client" | check_key_value "After POST client" "name" "$init_name"
echo "$client" | check_enabled "After POST client" "true"

new_name="newName"
new_address="10.8.0.99"

changed_client=$(
  echo "$client" |
    jq ".name = \"$new_name\"" |
    jq ".ipv4Address = \"$new_address\""
)

run_curl POST "client/$client_id" \
  -H "Content-Type: application/json" \
  -d "$changed_client" | check_success "Update client"

changed_client=$(get_client "$client_id")

echo "$changed_client" | check_key_value "After update" "name" "$new_name"
echo "$changed_client" | check_key_value "After update" "ipv4Address" "$new_address"

run_curl POST "client/$client_id/disable" | check_success "Disable client"
get_client "$client_id" | check_enabled "After disable" "false"

run_curl POST "client/$client_id/enable" | check_success "Enable client"
get_client "$client_id" | check_enabled "After enable" "true"

config=$(run_curl GET "client/$client_id/configuration")

if echo "$config" | grep -q Interface; then
  echo_success "get config success"
else
  echo_error "to get config fail"
fi

run_curl DELETE "client/$client_id" | check_success "Delete client"

count_errors=$(wc -l <"$tmp_errors_file")
echo "Found $count_errors errors"
[ "$count_errors" -eq 0 ] && exit 0 || exit 1
