#!/usr/bin/env python3
"""
Script to fix user_id logging in ui_components.py
"""

import re

# Read the file with UTF-8 encoding
with open('src/ui/ui_components.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Show Encode Section - Replace hardcoded user_id=1
old_encode_logging = """                # Log operation
                log_operation(
                    user_id=1,
                    method=method,
                    input_image=uploaded_file.name,
                    output_image=f"encoded_{method}.png",
                    message_size=len(message),
                    encoding_time=0.5,
                    status="success"
                )
                
                st.success("Message encoded successfully!")"""

new_encode_logging = """                # Log operation with actual user_id
                user_id = st.session_state.get('user_id')
                if user_id:
                    log_operation(
                        user_id=user_id,
                        method=method,
                        input_image=uploaded_file.name,
                        output_image=f"encoded_{method}.png",
                        message_size=len(message),
                        encoding_time=0.5,
                        status="success"
                    )
                    log_activity(
                        user_id=user_id,
                        action="encode",
                        details=f"Encoded message using {method} method"
                    )
                
                st.success("Message encoded successfully!")"""

content = content.replace(old_encode_logging, new_encode_logging)

# Fix 2: Show Decode Section - Replace hardcoded user_id=1
old_decode_logging = """            # Log operation
            log_operation(
                user_id=1,
                method=method,
                input_image=uploaded_file.name,
                output_image="",
                message_size=len(decoded_message),
                encoding_time=0.3,
                status="success"
            )"""

new_decode_logging = """            # Log operation with actual user_id
            user_id = st.session_state.get('user_id')
            if user_id:
                log_operation(
                    user_id=user_id,
                    method=method,
                    input_image=uploaded_file.name,
                    output_image="",
                    message_size=len(decoded_message),
                    encoding_time=0.3,
                    status="success"
                )
                log_activity(
                    user_id=user_id,
                    action="decode",
                    details=f"Decoded message using {method} method"
                )"""

content = content.replace(old_decode_logging, new_decode_logging)

# Write the fixed content back with UTF-8 encoding
with open('src/ui/ui_components.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed ui_components.py - user_id logging updated!")
print("✅ Activity logging added for encode/decode operations!")