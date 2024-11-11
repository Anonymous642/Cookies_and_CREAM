#!/bin/bash

CHROMIUM_DIR=$1

cd chromium_files

for filename in chrome/browser/extensions/api/cookies/*; do
    cp "$filename" "$CHROMIUM_DIR/src/$filename"
done
    
for filename in net/cookies/*; do
    cp "$filename" "$CHROMIUM_DIR/src/$filename"
done
    
for filename in net/log/*; do
    cp "$filename" "$CHROMIUM_DIR/src/$filename"
done
    
for filename in net/url_request/*; do
    cp "$filename" "$CHROMIUM_DIR/src/$filename"
done
    
for filename in services/network/public/cpp/*; do
    cp "$filename" "$CHROMIUM_DIR/src/$filename"
done
    
for filename in services/network/public/mojom/*; do
    cp "$filename" "$CHROMIUM_DIR/src/$filename"
done    

cp "services/network/cookie_manager.cc" "$CHROMIUM_DIR/src/services/network/cookie_manager.cc"
cp "services/network/cookie_manager.h" "$CHROMIUM_DIR/src/services/network/cookie_manager.h"
